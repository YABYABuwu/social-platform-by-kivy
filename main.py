from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from screens.feed_screen import FeedScreen  # import FeedScreen


class SocialPlatformApp(App):
    def build(self):
        Builder.load_file("kv/components.kv")
        Builder.load_file("kv/feed_screen.kv")

        sm = ScreenManager()
        sm.add_widget(FeedScreen(name="feed"))
        return sm
