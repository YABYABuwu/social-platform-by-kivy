import os
import re
from datetime import datetime


class UserManager:
    """Minimal UserManager: Load and Save user data only"""

    def __init__(self, txt_file="Users/users_data.txt"):
        self.txt_file = txt_file
        self.data = self._load_users()

    def _load_users(self):
        """Load users from TXT file"""
        if not os.path.exists(self.txt_file):
            return {"current_user": "You", "users": {}}

        with open(self.txt_file, "r", encoding="utf-8") as f:
            content = f.read()

        data = {"current_user": "You", "users": {}}

        # Parse SYSTEM section
        system_match = re.search(r"\[SYSTEM\](.*?)\n\[", content, re.DOTALL)
        if system_match:
            system_content = system_match.group(1)
            for line in system_content.strip().split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() == "current_user":
                        data["current_user"] = value.strip()

        # Parse [USER] blocks
        user_pattern = r"\[USER\](.*?)\[/USER\]"
        for user_match in re.finditer(user_pattern, content, re.DOTALL):
            user_content = user_match.group(1)
            user_info = {}

            for line in user_content.strip().split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    user_info[key.strip()] = value.strip()

            if "name" in user_info:
                user_name = user_info["name"]
                friends_str = user_info.get("friends", "")
                friends = [f.strip() for f in friends_str.split("|") if f.strip()]

                # Parse posts for this user
                posts_section_name = user_name.upper().replace(" ", "_")
                posts_pattern = rf"\[POSTS_{posts_section_name}\](.*?)\[/POSTS_{posts_section_name}\]"

                posts = []
                posts_match = re.search(posts_pattern, content, re.DOTALL)
                if posts_match:
                    posts_content = posts_match.group(1)
                    for line in posts_content.strip().split("\n"):
                        line = line.strip()
                        if line and line.startswith("["):
                            post = self._parse_post_line(line)
                            if post:
                                posts.append(post)

                data["users"][user_name] = {
                    "id": user_info.get("id", ""),
                    "name": user_name,
                    "profile_pic": user_info.get("profile_pic", "👤").replace(
                        "\\", "/"
                    ),
                    "bio": user_info.get("bio", ""),
                    "friends": friends,
                    "posts": posts,
                }

        return data

    def _parse_post_line(self, line):
        """Parse a post line: [timestamp] content |likes:X|liked_by:user1,user2|image:path"""
        match = re.match(
            r"\[(.*?)\]\s(.*?)\s\|likes:(\d+)\|liked_by:(.*?)(?:\|image:(.*))?$", line
        )

        if match:
            timestamp = match.group(1)
            content = match.group(2)
            likes = int(match.group(3))
            liked_by_str = match.group(4)
            image = match.group(5) if match.group(5) else ""
            liked_by = [u.strip() for u in liked_by_str.split(",") if u.strip()]

            return {
                "id": str(abs(hash(timestamp + content)) % 100000),
                "timestamp": timestamp,
                "content": content,
                "likes": likes,
                "liked_by": liked_by,
                "image": image.strip().replace("\\", "/") if image else "",
            }
        return None

    def _save_users(self):
        """Save users to TXT file"""
        lines = []
        lines.append("[SYSTEM]")
        lines.append(f"current_user={self.data.get('current_user', 'You')}")
        lines.append("")

        for user_name, user_data in self.data.get("users", {}).items():
            lines.append("[USER]")
            lines.append(f"id={user_data.get('id', '')}")
            lines.append(f"name={user_data.get('name', '')}")
            lines.append(
                f"profile_pic={user_data.get('profile_pic', '👤').replace('\\', '/')}"
            )
            lines.append(f"bio={user_data.get('bio', '')}")
            friends_str = "|".join(user_data.get("friends", []))
            lines.append(f"friends={friends_str}")
            lines.append("[/USER]")
            lines.append("")

            posts_section_name = user_name.upper().replace(" ", "_")
            lines.append(f"[POSTS_{posts_section_name}]")

            for post in user_data.get("posts", []):
                liked_by_str = ",".join(post.get("liked_by", []))
                image_str = post.get("image", "").replace("\\", "/")

                if image_str:
                    post_line = f"[{post['timestamp']}] {post['content']} |likes:{post['likes']}|liked_by:{liked_by_str}|image:{image_str}"
                else:
                    post_line = f"[{post['timestamp']}] {post['content']} |likes:{post['likes']}|liked_by:{liked_by_str}"
                lines.append(post_line)

            lines.append(f"[/POSTS_{posts_section_name}]")
            lines.append("")

        os.makedirs(os.path.dirname(self.txt_file) or ".", exist_ok=True)
        with open(self.txt_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def get_data(self):
        """Get all data"""
        return self.data

    def set_data(self, new_data):
        """Set data and save to file"""
        self.data = new_data
        self._save_users()

    def save(self):
        """Save current data to file"""
        self._save_users()

    def load(self):
        """Load data from file"""
        self.data = self._load_users()
        return self.data
