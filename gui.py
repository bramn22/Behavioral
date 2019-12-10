from kivy import properties
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class VideoWidget(BoxLayout):
    video_path = properties.StringProperty('data/segments/212_453.avi')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_next_video(self):
        print("Get next video")

    def set_invalid(self):
        pass

    def set_valid(self):
        pass


class BehavioralApp(App):
    # Returns root widget
    def build(self):
        return VideoWidget()


if __name__ == "__main__":
    BehavioralApp().run()