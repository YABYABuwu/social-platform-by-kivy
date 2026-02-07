from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from screens.feed_screen import FeedScreen  # import FeedScreen
from screens.friend_screen import FindFreindScreen
from screens.profile_screen import ProfileScreen


class RootLayout(BoxLayout):
    pass


class SocialPlatformApp(App):
    def build(self):
        Builder.load_file("kv/components.kv")
        Builder.load_file("kv/feed_screen.kv")
        Builder.load_file("kv/friend_screen.kv")
        Builder.load_file("kv/profile_screen.kv")
        return RootLayout()


SocialPlatformApp().run()
