from kivy import properties
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from functools import partial
from kivy.clock import Clock
from kivy.graphics import Color

from dataset import DataSet
import os
import extract
import utils

class VideoWidget(BoxLayout):
    user = properties.StringProperty('')
    video_path = properties.StringProperty('')
    current_key_action = None

    invalid_state = properties.StringProperty('normal')
    no_response_state = properties.StringProperty('normal')
    orienting_state = properties.StringProperty('normal')
    deceleration_state = properties.StringProperty('normal')
    acceleration_state = properties.StringProperty('normal')

    def __init__(self, dataset, cfg, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self.cfg = cfg
        self.user = cfg['user']
        self.set_user()
        Window.bind(on_key_up=self._keyup)

    def play_next_video(self):
        print("Get next video")
        print(self.user)
        next_video = self.dataset.get_next_unclassified(self.user)
        self.current_video = {'id': next_video.index.item(),
                'path': os.path.join(next_video['Path'].item(), next_video['Onset'].item()+'.avi')}
        self.video_path = self.current_video['path']
        # Clock.schedule_interval(self.show_onset, 8)

    def show_onset(self):
        video_pos = self.ids['video'].position
        # print(video_pos)
        if video_pos >= 3 and video_pos < 4:
            print("show onset")
            self.onset_color = (1, 1, 1, 0.8)
        else:
            self.onset_color = (1, 1, 1, 0)

        # Clock.schedule_interval(self.show_onset, 8)

    def set_classification(self, type):
        print(f"Set classification - {type}")
        classification_dict = {
            'invalid': 0,
            'no response': 1,
            'orienting': 2,
            'deceleration': 3,
            'acceleration': 4
        }
        self.dataset.add_record(self.user, self.current_video['id'], classification_dict[type])
        self.play_next_video()

    def set_user(self):
        self.user = self.ids['textinput'].text
        self.dataset.add_user(self.user)
        self.play_next_video()

    def extract_segments(self):
        extract.extract_all(data_path=self.cfg['data_path'], segments_path=self.cfg['segments_path'])
        self.dataset.add_segments(segments_path=self.cfg['segments_path'])

    # def _execute_key_action(self):
    #     if self.current_key_action:
    #         self.current_key_action()

    def _keyup(self, *args):
        self.invalid_state = 'normal'
        self.no_response_state = 'normal'
        self.orienting_state = 'normal'
        self.deceleration_state = 'normal'
        self.acceleration_state = 'normal'
        key = args[2]
        if key == 39:
            self.invalid_state = 'down'
            self.current_key_action = 'invalid'
        elif key == 30:
            self.no_response_state = 'down'
            self.current_key_action = 'no response'
        elif key == 31:
            self.orienting_state = 'down'
            self.current_key_action = 'orienting'
        elif key == 32:
            self.deceleration_state = 'down'
            self.current_key_action = 'deceleration'
        elif key == 33:
            self.acceleration_state = 'down'
            self.current_key_action = 'acceleration'
        elif key == 40: # Enter key
            if self.current_key_action:
                self.set_classification(self.current_key_action)
        else:
            self.current_key_action = None

            # self._execute_key_action()
        # fn = self.key_dict.get(args[2], None)
        # self.current_key_action = fn
        print(args)


class BehavioralApp(App):
    # Returns root widget
    def build(self):
        cfg = utils.load_config()

        if os.path.exists(f"{cfg['user']}.csv"):
            print('Existing csv found, loading the file')
            dataset = DataSet(cfg, create_csv=False)
        else:
            print('No csv found, creating one using segmented data')
            extract.extract_all(data_path=cfg['data_path'], segments_path=cfg['segments_path'])
            dataset = DataSet(cfg, create_csv=True)
        return VideoWidget(dataset, cfg)


if __name__ == "__main__":
    BehavioralApp().run()