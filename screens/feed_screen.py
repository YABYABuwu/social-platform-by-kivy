from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.app import App
import os

# แก้ไข Path การ Import ให้ตรงกับโครงสร้างของคุณ
try:
    from Users.user_manager import UserManager
except ImportError:
    # เผื่อกรณีรันจากโฟลเดอร์ที่ต่างกัน
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
        # สลับสถานะ Like ใน UI
        if self.is_liked:
            self.likes -= 1
            self.is_liked = False
        else:
            self.likes += 1
            self.is_liked = True

        # อัปเดตข้อมูลลงไฟล์ .txt ผ่าน UserManager
        try:
            # หา UserManager Instance จากหน้า FeedScreen
            app = App.get_running_app()
            # พยายามหา FeedScreen ใน ScreenManager (ระบุชื่อหน้าให้ถูก)
            feed_screen = None
            if hasattr(app.root, "get_screen"):
                feed_screen = app.root.get_screen("feed")

            if feed_screen and hasattr(feed_screen, "manager_instance"):
                manager = feed_screen.manager_instance
                # วนลูปหา Post ID ที่ตรงกันเพื่ออัปเดต Like
                for user_info in manager.data["users"].values():
                    for post in user_info.get("posts", []):
                        if str(post.get("id")) == str(self.post_id):
                            post["likes"] = int(self.likes)

                            # อัปเดตรายการคนที่กดไลค์ (liked_by)
                            liked_by = post.get("liked_by", []) or []
                            current_user = manager.data.get("current_user", "You")
                            if self.is_liked:
                                if current_user not in liked_by:
                                    liked_by.append(current_user)
                            else:
                                if current_user in liked_by:
                                    try:
                                        liked_by.remove(current_user)
                                    except ValueError:
                                        pass

                            post["liked_by"] = liked_by
                            manager.save()
                            print(f"Updated likes for post {self.post_id}")
                            return
        except Exception as e:
            print(f"Error updating likes: {e}")


class FeedScreen(Screen):
    def on_enter(self):
        # โหลดข้อมูลทุกครั้งที่เข้าหน้า Feed
        Clock.schedule_once(lambda dt: self.load_feed_data(), 0.2)

    def load_feed_data(self):
        try:
            # 1. โหลดข้อมูล
            self.manager_instance = UserManager(txt_file="Users/users_data.txt")
            raw_data = self.manager_instance.load()

            # 2. เตรียมข้อมูลเพื่อน
            current_user_info = raw_data["users"].get("You", {})
            friends_list = current_user_info.get("friends", [])

            friend_posts = []
            other_posts = []

            # --- [ส่วนที่แก้ไข] เปลี่ยนมาจำ "เนื้อหา" แทน "ID" ---
            seen_content = set()
            # ------------------------------------------------

            # 3. วนลูปดึงข้อมูล
            for user_name, user_info in raw_data["users"].items():
                if user_name == "You":
                    continue

                for post in user_info.get("posts", []):
                    # สร้างรหัสตรวจสอบจาก "ชื่อคนโพสต์ + เวลา + ข้อความ"
                    # .strip() ช่วยตัดช่องว่างส่วนเกินทิ้ง ป้องกันบั๊กวรรคเกิน
                    content_key = f"{user_name}|{post.get('timestamp', '').strip()}|{post.get('content', '').strip()}"

                    # --- เช็คว่าเนื้อหานี้เคยโชว์ไปหรือยัง ---
                    if content_key in seen_content:
                        print(
                            f"Skipping duplicate post: {content_key}"
                        )  # ปริ้นท์บอกใน Console ว่าเจอกันซ้ำ
                        continue

                    # ถ้ายังไม่เคยเจอ ให้จดไว้
                    seen_content.add(content_key)
                    # -------------------------------------

                    # Validate image path exists
                    post_image = post.get("image", "")
                    if post_image and not os.path.exists(post_image):
                        post_image = ""  # Clear invalid image path

                    post_data = {
                        "post_id": str(post.get("id", "")),
                        "username": user_name,
                        "content": post.get("content", ""),
                        "likes": float(post.get("likes", 0)),
                        "timestamp": post.get("timestamp", ""),
                        "image": post_image,
                        "is_liked": False,
                    }

                    if user_name in friends_list:
                        friend_posts.append(post_data)
                    else:
                        other_posts.append(post_data)

            # 4. ส่งเข้าหน้าจอ (ล้างของเก่าอัตโนมัติ)
            if "feed_rv" in self.ids:
                self.ids.feed_rv.data = friend_posts + other_posts
                self.ids.feed_rv.refresh_from_data()  # บังคับให้หน้าจอรีเฟรชทันที

        except Exception as e:
            print(f"Error in load_feed_data: {e}")
