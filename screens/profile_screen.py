from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {
            "name": "John Doe",
            "handle": "@johndoe",
            "bio": "Passionate developer | Coffee enthusiast | Tech lover ☕",
            "posts": 45,
            "followers": 1250,
            "following": 340,
            "profile_pic": "assets/profile.png",  # Default profile image
        }
        self.build_ui()

    def build_ui(self):
        """Build the profile screen UI"""
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Header with profile info
        header = BoxLayout(orientation="horizontal", size_hint_y=0.25, spacing=15)

        # Profile picture (circular)
        pic_container = BoxLayout(size_hint_x=0.3)
        profile_img = Image(
            source=self.user_data["profile_pic"], size_hint=(1, 1), allow_stretch=True
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
        posts_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        posts_layout.bind(minimum_height=posts_layout.setter("height"))

        # Sample posts
        sample_posts = [
            ("Just finished a great project! 🚀", "2 hours ago"),
            ("Coffee and coding 💻☕", "5 hours ago"),
            ("New blog post about Kivy framework", "1 day ago"),
            ("Amazing day at the tech conference", "2 days ago"),
            ("Started learning new programming language", "3 days ago"),
        ]

        for post_text, time_ago in sample_posts:
            post_widget = self.create_post_widget(post_text, time_ago)
            posts_layout.add_widget(post_widget)

        scroll.add_widget(posts_layout)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

    def create_post_widget(self, text, time):
        """Create a complete post widget like Facebook"""
        import random

        post_box = BoxLayout(
            orientation="vertical", size_hint_y=None, height=200, spacing=5
        )
        post_box.padding = 5
        post_box.canvas.before.clear()

        # Header: User info and time
        header = BoxLayout(orientation="horizontal", size_hint_y=0.15, spacing=10)

        # User profile pic (small)
        user_pic = Image(source="assets/profile.png", size_hint_x=0.1, size_hint_y=1)
        header.add_widget(user_pic)

        # User name and time
        info_layout = BoxLayout(orientation="vertical", size_hint_x=0.85, spacing=2)
        name = Label(
            text=self.user_data["name"], font_size="12sp", bold=True, size_hint_y=0.5
        )
        time_label = Label(
            text=time, font_size="10sp", color=(0.6, 0.6, 0.6, 1), size_hint_y=0.5
        )
        info_layout.add_widget(name)
        info_layout.add_widget(time_label)
        header.add_widget(info_layout)

        post_box.add_widget(header)

        # Post text content
        post_text = Label(
            text=text,
            font_size="15sp",
            size_hint_y=0.2,
            text_size=(self.width - 10, None),
            valign="top",
        )
        post_box.add_widget(post_text)

        # Engagement stats
        stats = [random.randint(10, 200), random.randint(2, 50), random.randint(1, 30)]

        stats_label = Label(
            text=f"👍 {stats[0]} likes  💬 {stats[1]} comments  ↗️ {stats[2]} shares",
            font_size="10sp",
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.15,
        )
        post_box.add_widget(stats_label)

        # Action buttons
        actions = BoxLayout(size_hint_y=0.25, spacing=5)

        like_btn = Button(
            text="👍 Like", size_hint_x=0.33, background_color=(0.9, 0.9, 0.9, 1)
        )
        like_btn.bind(on_press=lambda x: self.like_post(text))
        actions.add_widget(like_btn)

        comment_btn = Button(
            text="💬 Comment", size_hint_x=0.33, background_color=(0.9, 0.9, 0.9, 1)
        )
        comment_btn.bind(on_press=lambda x: self.comment_post(text))
        actions.add_widget(comment_btn)

        share_btn = Button(
            text="↗️ Share", size_hint_x=0.34, background_color=(0.9, 0.9, 0.9, 1)
        )
        share_btn.bind(on_press=lambda x: self.share_post(text))
        actions.add_widget(share_btn)

        post_box.add_widget(actions)

        return post_box

    def like_post(self, post_text):
        """Handle like button"""
        print(f"Liked post: {post_text[:30]}...")

    def comment_post(self, post_text):
        """Handle comment button"""
        print(f"Commenting on: {post_text[:30]}...")

    def share_post(self, post_text):
        """Handle share button"""
        print(f"Sharing post: {post_text[:30]}...")

        return post_box

    def edit_profile(self, instance):
        """Handle edit profile button press"""
        print("Edit profile clicked - can edit name, bio, etc. but not picture!")
