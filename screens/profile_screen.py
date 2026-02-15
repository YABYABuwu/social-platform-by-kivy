from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.clock import Clock
from kivy.app import App
from threading import Lock
import os

# Import UserManager to load actual user data
try:
    from Users.user_manager import UserManager
except ImportError:
    from user_manager import UserManager


class PostCard(BoxLayout):
    username = StringProperty()
    content = StringProperty()
    likes = NumericProperty(0)
    timestamp = StringProperty()
    image = StringProperty("")
    post_id = StringProperty()
    is_liked = BooleanProperty(False)

    def toggle_like(self):
        if self.is_liked:
            self.likes -= 1
            self.is_liked = False
        else:
            self.likes += 1
            self.is_liked = True

        # Update likes in the database with thread safety
        try:
            app = App.get_running_app()
            profile_screen = None
            if hasattr(app.root, "get_screen"):
                profile_screen = app.root.get_screen("profile")

            if profile_screen and hasattr(profile_screen, "manager_instance"):
                # Use lock to prevent race conditions
                if hasattr(profile_screen, "data_lock"):
                    with profile_screen.data_lock:
                        # Check if data is still loading
                        if profile_screen.is_loading:
                            print("Data still loading, skipping like update")
                            return

                        manager = profile_screen.manager_instance
                        if manager:
                            for user_info in manager.data["users"].values():
                                for post in user_info.get("posts", []):
                                    if str(post.get("id")) == str(self.post_id):
                                        post["likes"] = int(self.likes)
                                        manager.save()
                                        print(f"Updated likes for post {self.post_id}")
                                        return
        except Exception as e:
            print(f"Error updating likes: {e}")


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {
            "name": "Tae Tae",
            "handle": "@t_ttaexd",
            "bio": "I'm gay",
            "posts": 0,
            "followers": 0,
            "following": 0,
            # UPDATED: Pointing to your specific local image
            "profile_pic": r"D:\University\Kivy App Project\social-platform-by-kivy\Users\images\my_picture.png",
        }
        self.manager_instance = None
        self.data_loaded = False
        self.is_loading = False
        self.data_lock = Lock()  # Thread lock for data access

    def on_enter(self):
        # Load data once on first enter only
        if not self.data_loaded:
            self.load_profile_data()

    def load_profile_data(self):
        """Load profile data from UserManager - builds UI only once with thread safety"""
        with self.data_lock:
            self.is_loading = True

        try:
            self.manager_instance = UserManager(txt_file="Users/users_data.txt")
            raw_data = self.manager_instance.load()

            # Get current user's data (You)
            current_user_info = raw_data["users"].get("You", {})
            self.user_data["posts"] = len(current_user_info.get("posts", []))
            self.user_data["followers"] = current_user_info.get("followers", 0)
            self.user_data["following"] = len(current_user_info.get("friends", []))

            # If you want the profile pic to come from the database instead of hardcoding,
            # you would uncomment the line below (assuming your text file has this field):
            # self.user_data["profile_pic"] = current_user_info.get("profile_pic", self.user_data["profile_pic"])

            self.build_ui(raw_data)

            with self.data_lock:
                self.data_loaded = True
                self.is_loading = False

        except Exception as e:
            print(f"Error in load_profile_data: {e}")
            self.build_ui(None)
            with self.data_lock:
                self.data_loaded = True
                self.is_loading = False

    def build_ui(self, raw_data=None):
        """Build the profile screen UI"""
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Header with profile info
        header = BoxLayout(orientation="horizontal", size_hint_y=0.25, spacing=15)

        # Profile picture (circular) - with fallback if image not found
        pic_container = BoxLayout(size_hint_x=0.3)
        profile_pic_source = self.user_data["profile_pic"]

        # Validate image path exists
        if not os.path.exists(profile_pic_source):
            # print warning but keep the path so you can see if Kivy can load it anyway,
            # or set to empty string if you prefer a blank space.
            print(f"Warning: Profile image not found at {profile_pic_source}")
            # profile_pic_source = "" # Uncomment this if you want it to disappear completely on error

        profile_img = Image(
            source=profile_pic_source, size_hint=(1, 1), allow_stretch=True
        )
        pic_container.add_widget(profile_img)
        header.add_widget(pic_container)

        # User info
        info_layout = BoxLayout(orientation="vertical", size_hint_x=0.7, spacing=5)

        name_label = Label(
            text=self.user_data["name"], font_size="24sp", bold=True, size_hint_y=0.3
        )
        info_layout.add_widget(name_label)

        handle_label = Label(
            text=self.user_data["handle"],
            font_size="14sp",
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.2,
        )
        info_layout.add_widget(handle_label)

        bio_label = Label(
            text=self.user_data["bio"],
            font_size="12sp",
            size_hint_y=0.5,
            text_size=(self.width * 0.7, None),
            valign="top",
        )
        info_layout.add_widget(bio_label)

        header.add_widget(info_layout)
        main_layout.add_widget(header)

        # Stats section
        stats_layout = GridLayout(cols=3, size_hint_y=0.15, spacing=10)

        stats = [
            ("Posts", self.user_data["posts"]),
            ("Followers", self.user_data["followers"]),
            ("Following", self.user_data["following"]),
        ]

        for stat_name, stat_count in stats:
            stat_box = BoxLayout(orientation="vertical")
            count_label = Label(text=str(stat_count), font_size="18sp", bold=True)
            name_label = Label(
                text=stat_name, font_size="10sp", color=(0.6, 0.6, 0.6, 1)
            )
            stat_box.add_widget(count_label)
            stat_box.add_widget(name_label)
            stats_layout.add_widget(stat_box)

        main_layout.add_widget(stats_layout)

        # Edit Profile Button
        edit_btn = Button(
            text="Edit Profile", size_hint_y=0.08, background_color=(0.2, 0.6, 0.8, 1)
        )
        edit_btn.bind(on_press=self.edit_profile)
        main_layout.add_widget(edit_btn)

        # Posts section
        posts_label = Label(
            text="Your Posts", font_size="16sp", bold=True, size_hint_y=0.08
        )
        main_layout.add_widget(posts_label)

        # Scrollable posts list
        scroll = ScrollView(size_hint=(1, 0.48))
        posts_layout = GridLayout(cols=1, spacing=20, size_hint_y=None, padding=10)
        posts_layout.bind(minimum_height=posts_layout.setter("height"))

        if raw_data:
            current_user_posts = raw_data["users"].get("You", {}).get("posts", [])
            if current_user_posts:
                for post in current_user_posts:
                    post_image = post.get("image", "")
                    if post_image and not os.path.exists(post_image):
                        post_image = ""

                    post_widget = PostCard(
                        post_id=str(post.get("id", "")),
                        username="You",
                        content=post.get("content", ""),
                        likes=float(post.get("likes", 0)),
                        timestamp=post.get("timestamp", ""),
                        image=post_image,
                        is_liked=False,
                        size_hint_y=None,
                        height=250,
                    )
                    posts_layout.add_widget(post_widget)
            else:
                empty_label = Label(
                    text="No posts yet. Create your first post!",
                    font_size="14sp",
                    color=(0.6, 0.6, 0.6, 1),
                )
                posts_layout.add_widget(empty_label)

        scroll.add_widget(posts_layout)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

    def edit_profile(self, instance):
        print("Edit profile clicked")
