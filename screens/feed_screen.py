from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.app import App

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
            # 1. โหลดข้อมูลจาก UserManager
            self.manager_instance = UserManager(txt_file="Users/users_data.txt")
            raw_data = self.manager_instance.load()

            # 2. ดึงรายชื่อเพื่อนของ "You" เพื่อจัดลำดับ
            current_user_info = raw_data["users"].get("You", {})
            friends_list = current_user_info.get("friends", [])

            friend_posts = []
            other_posts = []

            # 3. จัดเตรียมข้อมูลสำหรับ RecycleView
            for user_name, user_info in raw_data["users"].items():
                if user_name == "You":
                    continue  # ไม่แสดงโพสต์ตัวเองใน Feed

                for post in user_info.get("posts", []):
                    post_data = {
                        "post_id": str(post.get("id", "")),
                        "username": user_name,
                        "content": post.get("content", ""),
                        "likes": float(post.get("likes", 0)),
                        "timestamp": post.get("timestamp", ""),
                        "image": post.get("image", ""),
                        "is_liked": False,  # เริ่มต้นเป็น False (สามารถขยายระบบจำค่า Like ต่อได้)
                    }

                    if user_name in friends_list:
                        friend_posts.append(post_data)
                    else:
                        other_posts.append(post_data)

            # 4. รวมโพสต์ (เพื่อนก่อน) และส่งให้ UI
            if "feed_rv" in self.ids:
                self.ids.feed_rv.data = friend_posts + other_posts

        except Exception as e:
            print(f"Error in load_feed_data: {e}")
