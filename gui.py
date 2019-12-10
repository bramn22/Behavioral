from kivy import properties
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window

from dataset import DataSet
import os
import extract


class VideoWidget(BoxLayout):
    user = properties.StringProperty('')
    video_path = properties.StringProperty('')
    current_key_action = None

    def __init__(self, dataset, **kwargs):
        super().__init__(**kwargs)
        self.dataset = dataset
        self.key_dict = {# relates to 0, 1, 2, 3 and 4
            39: self.set_invalid,
            30: self.set_valid,
            31: self.set_valid,
            32: self.set_valid,
            33: self.set_valid,
        }
        Window.bind(on_key_up=self._keyup)

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

    def extract_segments(self):
        extract.extract_all(data_path='data')
        self.dataset.add_segments(segments_path='data/segments')

    def _execute_key_action(self):
        if self.current_key_action:
            self.current_key_action()

    def _keyup(self, *args):
        if args[2] == 40: # Enter key
            self._execute_key_action()
        fn = self.key_dict.get(args[2], None)
        self.current_key_action = fn
        print(args)


class BehavioralApp(App):
    # Returns root widget
    def build(self):
        if os.path.exists('classifications.csv'):
            print('Existing classification csv found, loading the file')
            dataset = DataSet(csv_path='classifications.csv')
        else:
            print('No classification csv found, creating one using segmented data')
            extract.extract_all(data_path='data')
            dataset = DataSet(segments_path='data/segments')
        return VideoWidget(dataset)


if __name__ == "__main__":
    BehavioralApp().run()