import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

def extract_ROI(img):
    # kernel = np.ones((9, 9)) * -1
    # kernel[3:6, 3:6] = 1
    # res = cv2.matchTemplate(img, template, method=cv2.TM_CCORR)
    # if n > 340:
    #     plt.imshow(res)
    #     plt.show()
    # res = cv2.filter2D(img, ddepth=-1, kernel=kernel)
    x, y, w, h = 570, 270, 60, 60
    intens = np.max(img[y:y+h, x:x+w, :])
    cv2.rectangle(img, (x, y), (x+w, y+h), color=(0, 0, 255), thickness=5)
    return intens

def extract_stimuli(intens, cutoff):
    stimuli = list(map(lambda i: True if i >= cutoff else False, intens))
    return stimuli

def filter_intens(intens, fps):
    # Intensity filtering
    max_threshold = 480000
    min_threshold = 125

    intens = list(map(lambda i: i if i >= min_threshold and i <= max_threshold else 0, intens))

    # plt.plot(range(len(intens)), intens)
    # plt.show()

    intens = np.asarray(intens)
    # intens_norm = intens
    intens_norm = (intens - np.min(intens))
    intens_norm = intens_norm / np.max(intens_norm)

    stimuli = extract_stimuli(intens_norm, 0.6)
    # plt.plot(range(len(stimuli)), stimuli)
    # plt.show()

    s_stimulus = 0.9

    n_stimulus = s_stimulus * fps
    num_true = 0
    for i in range(len(stimuli)):
        if stimuli[i]:
            num_true += 1
        else:
            # Remove false positives that show heightened intensity for less than 1 second
            if num_true > 0 and num_true < n_stimulus:
                stimuli[i-num_true:i] = [False]*num_true
            num_true = 0
    return stimuli


def get_segments(stimuli, s_before, s_after, fps):
    n_before = int(s_before*fps)
    n_after = int(s_after*fps) + 1 # +1 is the stimulus length

    segments = []
    on = False
    for i, stim in enumerate(stimuli):
        if not on and stim:
            segments.append((i-n_before, i+n_after))
            on = True
        if on and not stim:
            on = False
    return segments


def detect_stimuli(cap, fps):
    intens = []
    n = 0
    while cap.isOpened():
        print(n)
        ret, frame = cap.read()
        if ret:
            intens.append(extract_ROI(frame))
            cv2.imshow('Stimulus detection', frame)
            cv2.waitKey(1)
            n += 1
        else:
            break
    stimuli = filter_intens(intens, fps)
    # plt.plot(range(len(stimuli)), stimuli)
    # plt.show()
    return stimuli


def write_video_segments(segments, cap, fps, folder_path):
    os.makedirs(folder_path)

    for (start, end) in segments:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        n = start
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(os.path.join(folder_path, f'{start}_{end}.avi'), fourcc, int(fps), (640,480))

        while cap.isOpened() and n < end:
            print(n)
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                n += 1
            else:
                print("Video processing stopped early")
                break
        out.release()


# def extract(filename):
#     cap = cv2.VideoCapture(filename)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     print(f"FPS: {fps}")
#     segments = process_video(cap)
#     print(segments)
#     extract_video_segments(segments, cap)
#     cap.release()
#     cv2.destroyAllWindows()


def extract_all(data_path, segments_path):
    os.makedirs(segments_path, exist_ok=True)

    experiments = [f for f in os.listdir(data_path) if f != 'segments']
    for experiment in experiments:
        experiment_path = os.path.join(data_path, experiment)
        videos = [f for f in os.listdir(experiment_path) if f.endswith('avi')]
        for video in videos:
            folder_path = os.path.join(segments_path, experiment, os.path.splitext(video)[0])
            if not os.path.exists(folder_path):
                cap = cv2.VideoCapture(os.path.join(experiment_path, video))
                fps = cap.get(cv2.CAP_PROP_FPS)
                print(f"FPS: {fps}")

                # Detect stimuli
                stimuli = detect_stimuli(cap, fps)
                # Extract segments
                segments = get_segments(stimuli, s_before=3, s_after=5, fps=fps)
                # Save segments
                write_video_segments(segments, cap, fps=fps, folder_path=folder_path)
                cap.release()
                cv2.destroyAllWindows()