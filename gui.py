from kivy import properties
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from dataset import DataSet
import os


class VideoWidget(BoxLayout):
    user = properties.StringProperty('')
    video_path = properties.StringProperty('')

    def __init__(self, dataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset

    def play_next_video(self):
        print("Get next video")
        print(self.user)
        next_video = self.dataset.get_next_unclassified(self.user)
        self.current_video = {'id': next_video.index.item(),
                'path': os.path.join(next_video['Path'].item(), next_video['Onset'].item()+'.avi')}
        self.video_path = self.current_video['path']

    def set_invalid(self):
        print("Set invalid")
        self.dataset.add_record(self.user, self.current_video['id'], 'invalid')
        self.play_next_video()

    def set_valid(self):
        print("Set valid")
        self.dataset.add_record(self.user, self.current_video['id'], 'valid')
        self.play_next_video()

    def set_user(self):
        self.user = self.ids['textinput'].text
        self.dataset.add_user(self.user)
        self.play_next_video()


class BehavioralApp(App):
    # Returns root widget
    def build(self):
        if os.path.exists('classifications.csv'):
            print('Existing classification csv found, loading the file')
            dataset = DataSet(csv_path='classifications.csv')
        else:
            print('No classification csv found, creating one using segmented data')
            dataset = DataSet(segments_path='data/segments')
        return VideoWidget(dataset)


if __name__ == "__main__":
    BehavioralApp().run()