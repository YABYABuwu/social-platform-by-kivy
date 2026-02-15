from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
import sys
import os

# Import UserManager from Users/user_manager.py
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Users.user_manager import UserManager


class FindFreindScreen(Screen):
    # สร้าง ListProperty สำหรับเก็บรายชื่อเพื่อนและไม่ใช่เพื่อน
    friends = ListProperty([])
    non_friends = ListProperty([])

    # เรียกใช้ load_users เมื่อเข้าสู่หน้าจอ
    def on_pre_enter(self, *args):
        self.load_users()

    # โหลดรายชื่อผู้ใช้และจัดกลุ่มเป็นเพื่อนและไม่ใช่เพื่อน
    def load_users(self):
        manager = UserManager()  # สร้างอินสแตนซ์ของ UserManager เพื่อเข้าถึงข้อมูลผู้ใช้
        data = manager.get_data()  # ดึงข้อมูลทั้งหมดจาก UserManager
        current_user = data.get("current_user", "You")  # ดึงชื่อผู้ใช้ปัจจุบันจาก data
        users = data.get("users", {})
        # ตรวจสอบว่าผู้ใช้ปัจจุบันมีอยู่ในข้อมูลหรือไม่ ถ้าไม่มีก็ให้รายชื่อเพื่อนและไม่ใช่เพื่อนเป็นว่าง
        if current_user not in users:
            self.friends = []
            self.non_friends = []
            return
        friend_names = set(
            users[current_user].get("friends", [])
        )  # ดึงรายชื่อเพื่อนของผู้ใช้ปัจจุบันและเก็บไว้ใน set เพื่อความเร็วในการค้นหา
        all_names = set(users.keys()) - {
            current_user
        }  # สร้าง set ของชื่อผู้ใช้ทั้งหมดโดยไม่รวมชื่อผู้ใช้ปัจจุบัน
        self.friends = [
            u for u in all_names if u in friend_names
        ]  # สร้างรายชื่อเพื่อนโดยการกรองชื่อผู้ใช้ทั้งหมดที่อยู่ใน friend_names
        self.non_friends = [
            u for u in all_names if u not in friend_names
        ]  # สร้างรายชื่อไม่ใช่เพื่อนโดยการกรองชื่อผู้ใช้ทั้งหมดที่ไม่อยู่ใน friend_names
        self.friends = list(self.friends)
        self.non_friends = list(self.non_friends)

    # เพิ่มเพื่อนโดยการอัปเดตข้อมูลใน UserManager และโหลดรายชื่อใหม่
    def add_friend(self, username):
        manager = UserManager()
        data = manager.get_data()
        current_user = data.get("current_user", "You")
        users = data.get("users", {})  # ดึงข้อมูลผู้ใช้ทั้งหมดจาก data
        if current_user in users and username in users:
            if (
                username not in users[current_user]["friends"]
            ):  # ถ้าผู้ใช้ไม่ได้เป็นเพื่อน ให้เพิ่มเพื่อนในรายชื่อเพื่อน
                users[current_user]["friends"].append(username)
                data["users"] = users
                manager.set_data(data)
                self.load_users()

    # ลบเพื่อนโดยการอัปเดตข้อมูลใน UserManager และโหลดรายชื่อใหม่
    def remove_friend(self, username):
        manager = UserManager()
        data = manager.get_data()
        current_user = data.get("current_user", "You")
        users = data.get("users", {})
        if current_user in users and username in users:
            if (
                username in users[current_user]["friends"]
            ):  # ถ้าผู้ใช้เป็นเพื่อน ให้ลบเพื่อนออกจากรายชื่อเพื่อน
                users[current_user]["friends"].remove(username)
                data["users"] = users
                manager.set_data(data)
                self.load_users()
