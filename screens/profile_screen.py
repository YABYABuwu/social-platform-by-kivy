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

# Import UserManager เพื่อโหลดข้อมูลผู้ใช้จริง
try:
    from Users.user_manager import UserManager
except ImportError:
    from user_manager import UserManager


class ProfileCard(BoxLayout):  # คลาสสำหรับแสดงผลโพสต์แต่ละอันในหน้าโปรไฟล์
    username = StringProperty()
    content = StringProperty()
    likes = NumericProperty(0)
    timestamp = StringProperty()
    image = StringProperty("")
    post_id = StringProperty()
    is_liked = BooleanProperty(False)

    def toggle_like(self):  # ฟังก์ชันสำหรับสลับสถานะการกดไลค์
        # สลับสถานะใน UI
        if self.is_liked:
            self.likes -= 1
            self.is_liked = False
        else:
            self.likes += 1
            self.is_liked = True

        # อัปเดตจำนวนไลค์ในฐานข้อมูล (ไฟล์ .txt) พร้อมการป้องกัน race condition
        try:
            app = App.get_running_app()
            profile_screen = None
            if hasattr(app.root, "get_screen"):
                profile_screen = app.root.get_screen("profile")

            if profile_screen and hasattr(profile_screen, "manager_instance"):
                # ใช้ Lock เพื่อป้องกันการเข้าถึงข้อมูลพร้อมกันจากหลาย thread
                if hasattr(profile_screen, "data_lock"):
                    with profile_screen.data_lock:
                        # ตรวจสอบว่าข้อมูลกำลังโหลดอยู่หรือไม่
                        if profile_screen.is_loading:
                            print("Data still loading, skipping like update")
                            return

                        manager = profile_screen.manager_instance
                        if manager:
                            # วนลูปหาโพสต์ที่ตรงกันเพื่ออัปเดตจำนวนไลค์
                            for user_info in manager.data["users"].values():
                                for post in user_info.get("posts", []):
                                    if str(post.get("id")) == str(self.post_id):
                                        post["likes"] = int(self.likes)
                                        manager.save()
                                        print(f"Updated likes for post {self.post_id}")
                                        return
        except Exception as e:
            print(f"Error updating likes: {e}")


class ProfileScreen(Screen):  # คลาสหลักสำหรับหน้าจอโปรไฟล์
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ข้อมูลผู้ใช้เริ่มต้น (จะถูกเขียนทับด้วยข้อมูลจริง)
        self.user_data = {
            "name": "Chanathip Nuisee",
            "handle": "@boss_20060902",
            "bio": "I'm gay.",
            "posts": 0,
            "followers": 0,
            "following": 0,
            # อัปเดต: ชี้ไปยัง path รูปภาพในเครื่องของคุณ
            "profile_pic": r"Users\images\my_picture.png",
        }
        self.manager_instance = None  # instance ของ UserManager
        self.data_loaded = False  # Flag เพื่อตรวจสอบว่าโหลดข้อมูลแล้วหรือยัง
        self.is_loading = False  # Flag เพื่อตรวจสอบสถานะการโหลด
        self.data_lock = Lock()  # ตัวแปร Lock สำหรับป้องกัน race condition

    def on_enter(self):  # ฟังก์ชันที่ Kivy เรียกใช้เมื่อเข้ามาในหน้านี้
        # โหลดข้อมูลเพียงครั้งเดียวเมื่อเข้าหน้าครั้งแรก
        if not self.data_loaded:
            self.load_profile_data()

    def load_profile_data(self):  # ฟังก์ชันสำหรับโหลดข้อมูลโปรไฟล์จาก UserManager
        """โหลดข้อมูลโปรไฟล์จาก UserManager - สร้าง UI เพียงครั้งเดียวและป้องกัน race condition"""
        # ล็อคเพื่อป้องกันการเข้าถึงข้อมูลพร้อมกัน
        with self.data_lock:
            self.is_loading = True

        try:
            # สร้าง instance ของ UserManager และโหลดข้อมูลจากไฟล์
            self.manager_instance = UserManager(txt_file="Users/users_data.txt")
            raw_data = self.manager_instance.load()

            # ดึงข้อมูลของผู้ใช้ปัจจุบัน (You)
            current_user_info = raw_data["users"].get("You", {})

            self.user_data["posts"] = len(current_user_info.get("posts", []))
            self.user_data["followers"] = current_user_info.get("followers", 0)

            # นับจำนวน following ให้ตรงกับหน้า friend (นับเฉพาะ user ที่มีอยู่จริง)
            all_users = set(raw_data["users"].keys())
            friends = current_user_info.get("friends", [])
            self.user_data["following"] = len([f for f in friends if f in all_users])

            # หากต้องการให้รูปโปรไฟล์มาจากฐานข้อมูลแทนการ hardcode
            # self.user_data["profile_pic"] = current_user_info.get("profile_pic", self.user_data["profile_pic"])

            # สร้าง UI ด้วยข้อมูลที่โหลดมา
            self.build_ui(raw_data)

            # ปลดล็อคและอัปเดตสถานะการโหลด
            with self.data_lock:
                self.data_loaded = True
                self.is_loading = False

        except Exception as e:
            print(f"Error in load_profile_data: {e}")
            self.build_ui(None)  # สร้าง UI แม้ว่าจะเกิดข้อผิดพลาด (แสดงหน้าว่าง)
            with self.data_lock:
                self.data_loaded = True
                self.is_loading = False

    def build_ui(self, raw_data=None):  # ฟังก์ชันสำหรับสร้างส่วนประกอบ UI ของหน้าโปรไฟล์
        """สร้าง UI ของหน้าโปรไฟล์"""
        # Layout หลักแนวตั้ง
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # ส่วน Header ที่มีข้อมูลโปรไฟล์
        header = BoxLayout(orientation="horizontal", size_hint_y=0.25, spacing=15)

        # รูปโปรไฟล์ (พร้อม fallback หากไม่พบรูป)
        pic_container = BoxLayout(size_hint_x=0.3)
        profile_pic_source = self.user_data["profile_pic"]

        # ตรวจสอบว่า path ของรูปภาพมีอยู่จริงหรือไม่
        if not os.path.exists(profile_pic_source):
            # print warning but keep the path so you can see if Kivy can load it anyway,
            # or set to empty string if you prefer a blank space.
            print(f"Warning: Profile image not found at {profile_pic_source}")
            # profile_pic_source = "" # หากต้องการให้รูปหายไปเลยเมื่อไม่พบ

        profile_img = Image(
            source=profile_pic_source, size_hint=(1, 1), allow_stretch=True
        )
        pic_container.add_widget(profile_img)
        header.add_widget(pic_container)

        # ส่วนข้อมูลผู้ใช้ (ชื่อ, handle, bio)
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
            font_size="20sp",
            size_hint_y=0.2,
        )
        info_layout.add_widget(bio_label)

        header.add_widget(info_layout)
        main_layout.add_widget(header)

        # ส่วนสถิติ (Posts, Followers, Following)
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

        # ปุ่ม Edit Profile
        edit_btn = Button(
            text="Edit Profile", size_hint_y=0.08, background_color=(0.2, 0.6, 0.8, 1)
        )
        edit_btn.bind(on_press=self.edit_profile)
        main_layout.add_widget(edit_btn)

        # ส่วนแสดงโพสต์
        posts_label = Label(
            text="Your Posts", font_size="16sp", bold=True, size_hint_y=0.08
        )
        main_layout.add_widget(posts_label)

        # รายการโพสต์ที่สามารถเลื่อนได้
        scroll = ScrollView(size_hint=(1, 0.48))
        posts_layout = GridLayout(cols=1, spacing=20, size_hint_y=None, padding=10)
        posts_layout.bind(minimum_height=posts_layout.setter("height"))

        # ตรวจสอบว่ามีข้อมูลดิบ (raw_data) หรือไม่
        if raw_data:
            # ดึงรายการโพสต์ของผู้ใช้ปัจจุบัน
            current_user_posts = raw_data["users"].get("You", {}).get("posts", [])
            if current_user_posts:
                # วนลูปสร้าง PostCard สำหรับแต่ละโพสต์
                for post in current_user_posts:
                    post_image = post.get("image", "")
                    if post_image and not os.path.exists(post_image):
                        post_image = ""

                    post_widget = ProfileCard(
                        post_id=str(post.get("id", "")),
                        username="Tae Tae",
                        content=post.get("content", ""),
                        likes=float(post.get("likes", 0)),
                        timestamp=post.get("timestamp", ""),
                        image=post_image,
                        is_liked=False,  # สถานะไลค์เริ่มต้น
                        size_hint_y=None,
                        height=250,
                    )
                    posts_layout.add_widget(post_widget)
            else:
                # แสดงข้อความเมื่อยังไม่มีโพสต์
                empty_label = Label(
                    text="No posts yet. Create your first post!",
                    font_size="14sp",
                    color=(0.6, 0.6, 0.6, 1),
                )
                posts_layout.add_widget(empty_label)

        scroll.add_widget(posts_layout)
        main_layout.add_widget(scroll)

        # เพิ่ม layout หลักลงใน screen
        self.add_widget(main_layout)

    def edit_profile(self, instance):  # ฟังก์ชันที่จะถูกเรียกเมื่อกดปุ่ม Edit Profile
        print("Edit profile clicked")
