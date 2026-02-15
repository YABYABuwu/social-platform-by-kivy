from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
import sys
import os

# Import UserManager from Users/user_manager.py
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from Users.user_manager import UserManager


class FindFreindScreen(Screen):
    friends = ListProperty([])
    non_friends = ListProperty([])

    def on_pre_enter(self, *args):
        self.load_users()

    def load_users(self):
        manager = UserManager()
        data = manager.get_data()
        current_user = data.get("current_user", "You")
        users = data.get("users", {})
        if current_user not in users:
            self.friends = []
            self.non_friends = []
            return
        friend_names = set(users[current_user].get("friends", []))
        all_names = set(users.keys()) - {current_user}
        self.friends = [u for u in all_names if u in friend_names]
        self.non_friends = [u for u in all_names if u not in friend_names]
        # Reverse lists so new names appear at the bottom
        self.friends = list(self.friends)
        self.non_friends = list(self.non_friends)

    def add_friend(self, username):
        manager = UserManager()
        data = manager.get_data()
        current_user = data.get("current_user", "You")
        users = data.get("users", {})
        if current_user in users and username in users:
            if username not in users[current_user]["friends"]:
                users[current_user]["friends"].append(username)
                data["users"] = users
                manager.set_data(data)
                self.load_users()

    def remove_friend(self, username):
        manager = UserManager()
        data = manager.get_data()
        current_user = data.get("current_user", "You")
        users = data.get("users", {})
        if current_user in users and username in users:
            if username in users[current_user]["friends"]:
                users[current_user]["friends"].remove(username)
                data["users"] = users
                manager.set_data(data)
                self.load_users()
