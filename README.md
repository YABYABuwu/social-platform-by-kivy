My First git and kivy dev as team
**Team list**
- นายคุณัชญ์ ทวีรัตน์ 6810110038
- นายธีรวัต แซ่น่ำ 6810110163
- นายชนาธิป นุ้ยสี 6810110566

**Social Platform (Kivy)**

โปรเจกต์ตัวอย่างแสดงการพัฒนาแอปโซเชียลแบบเรียบง่ายด้วย Kivy + Python ซึ่งมีหน้าจอหลักคือ Feed, Friends และ Profile

**คุณสมบัติเด่น:**
- **ดูฟีด:** แสดงโพสต์หรือคอนเทนต์ในหน้า Feed
- **รายชื่อเพื่อน:** ดูและจัดการเพื่อนในหน้า Friends
- **โปรไฟล์ผู้ใช้:** ดูข้อมูลผู้ใช้และรูปภาพในหน้า Profile

**ความต้องการระบบ:**
- Python 3.8+ (แนะนำ 3.10/3.11)
- Kivy (ติดตั้งผ่าน `pip install kivy`)

**ติดตั้ง & รัน:**
1. สร้าง virtual environment (แนะนำ):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # สำหรับ Mac/Linux
   .venv\Scripts\activate     # สำหรับ Windows

2. ติดตั้ง Kivy:

	pip install kivy

3. รันแอป:

	python main.py

**โครงสร้างโปรเจกต์ (สรุป):**
- [main.py](main.py) : จุดเริ่มต้นของแอป
- [kv/components.kv](kv/components.kv) : ส่วนประกอบ UI ทั่วไป
- [kv/feed_screen.kv](kv/feed_screen.kv) : เลย์เอาต์หน้าฟีด
- [kv/friend_screen.kv](kv/friend_screen.kv) : เลย์เอาต์หน้าเพื่อน
- [kv/profile_screen.kv](kv/profile_screen.kv) : เลย์เอาต์หน้าโปรไฟล์
- [screens/feed_screen.py](screens/feed_screen.py) : โลจิกของหน้า Feed
- [screens/friend_screen.py](screens/friend_screen.py) : โลจิกของหน้า Friends
- [screens/profile_screen.py](screens/profile_screen.py) : โลจิกของหน้า Profile
- [Users/user_manager.py](Users/user_manager.py) : จัดการข้อมูลผู้ใช้ (อ่าน/เขียน)
- [Users/users_data.txt](Users/users_data.txt) : ตัวอย่างข้อมูลผู้ใช้
- [Users/images/](Users/images/) : ไฟล์รูปภาพตัวอย่าง

**วิธีพัฒนาเพิ่มเติม:**
- เพิ่มระบบบันทึกข้อมูลแบบจริงจัง (เช่น SQLite หรือ API)
- เชื่อมต่อกับ backend เพื่อดึง/โพสต์คอนเทนต์
- ปรับปรุง UI/UX และรองรับการย่อ/ขยายหน้าจอ

**ร่วมพัฒนา:**
- สร้าง branch ใหม่สำหรับฟีเจอร์ที่ต้องการ
- เปิด pull request พร้อมคำอธิบายการเปลี่ยนแปลง

