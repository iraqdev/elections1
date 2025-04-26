import json
import os
import uuid
from datetime import datetime
from models.user import User, UserType, VolunteerType


class AuthService:
    def __init__(self):
        self.users_file = "data/users.json"
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_users(self):
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            return [User.from_dict(user_data) for user_data in users_data]
        except Exception as e:
            print(f"Error loading users: {e}")
            return []

    def _save_users(self, users):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump([user.to_dict() for user in users], f, ensure_ascii=False)

    def register(self, name, id_number, center, address, phone_number):
        users = self._load_users()

        # التحقق من وجود المستخدم بنفس رقم البطاقة
        for user in users:
            if user.id_number == id_number:
                raise ValueError("رقم البطاقة مسجل بالفعل")

        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            name=name,
            id_number=id_number,
            center=center,
            address=address,
            phone_number=phone_number,
            user_type=UserType.REGULAR
        )

        users.append(new_user)
        self._save_users(users)
        self._save_current_user(new_user)

        return new_user

    def register_volunteer(self, name, id_number, center, address, phone_number, volunteer_type):
        users = self._load_users()

        # التحقق من وجود المستخدم بنفس رقم البطاقة
        for user in users:
            if user.id_number == id_number:
                raise ValueError("رقم البطاقة مسجل بالفعل")

        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            name=name,
            id_number=id_number,
            center=center,
            address=address,
            phone_number=phone_number,
            user_type=UserType.VOLUNTEER,
            volunteer_type=volunteer_type
        )

        users.append(new_user)
        self._save_users(users)
        self._save_current_user(new_user)

        return new_user

    def login_as_guest(self):
        user_id = f"guest-{str(uuid.uuid4())}"
        guest_user = User(
            id=user_id,
            name="ضيف",
            user_type=UserType.GUEST
        )

        self._save_current_user(guest_user)
        return guest_user

    def login(self, id_number):
        users = self._load_users()
        for user in users:
            if user.id_number == id_number:
                self._save_current_user(user)
                return user
        return None

    def add_user_points(self, user_id, points):
        users = self._load_users()
        for user in users:
            if user.id == user_id:
                user.points += points
                self._save_users(users)
                return user.points
        return None

    def _save_current_user(self, user):
        user_data = user.to_dict()
        with open("data/current_user.json", 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False)

    def get_current_user(self):
        try:
            with open("data/current_user.json", 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            return User.from_dict(user_data)
        except:
            return None

    def logout(self):
        if os.path.exists("data/current_user.json"):
            os.remove("data/current_user.json")