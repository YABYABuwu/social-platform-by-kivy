from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty


# คลาสสำหรับแต่ละแถวใน Feed
class PostCard(BoxLayout):
    username = StringProperty()
    content = StringProperty()
    likes = StringProperty()

    def toggle_like(self):
        btn = self.ids.like_btn
        if btn.text == "Like":
            btn.text = "Liked!"
            btn.background_color = (1, 0.3, 0.3, 1)
        else:
            btn.text = "Like"
            btn.background_color = (1, 1, 1, 1)


# screens/feed_screen.py


class FeedScreen(Screen):
    def on_enter(self):
        # ใช้ Clock เพื่อหน่วงเวลาให้ KV โหลดเสร็จชัวร์ๆ ก่อนรัน (ทางเลือกที่ปลอดภัย)
        from kivy.clock import Clock

        Clock.schedule_once(lambda dt: self.load_feed_data())

    def load_feed_data(self):
        posts = []
        for i in range(20):
            posts.append(
                {
                    "username": f"Friend {i+1}",
                    "content": f"RecycleView ({i+1})",
                    "likes": str(i * 5),
                }
            )

        # ป้องกันการเด้ง: เช็คว่ามี id ชื่อ feed_rv อยู่จริงไหม
        if "feed_rv" in self.ids:
            self.ids.feed_rv.data = posts
        else:
            print("Warning: feed_rv not found in ids yet!")
