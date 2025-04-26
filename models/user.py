from enum import Enum


class UserType(Enum):
    REGULAR = 0  # مستخدم عادي
    VOLUNTEER = 1  # متطوع
    GUEST = 2  # ضيف
    ADMIN = 3  # مشرف


class VolunteerType(Enum):
    FIELD = 0  # ميداني
    DESIGN = 1  # تصميم
    PUBLISHING = 2  # نشر


class User:
    def __init__(
            self,
            id=None,
            name="",
            id_number="",
            center="",
            address="",
            phone_number="",
            user_type=UserType.GUEST,
            volunteer_type=None,
            points=0
    ):
        self.id = id
        self.name = name
        self.id_number = id_number
        self.center = center
        self.address = address
        self.phone_number = phone_number
        self.user_type = user_type
        self.volunteer_type = volunteer_type
        self.points = points  # نقاط المستخدم (نظام النقاط والمكافآت)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'id_number': self.id_number,
            'center': self.center,
            'address': self.address,
            'phone_number': self.phone_number,
            'user_type': self.user_type.value,
            'points': self.points
        }

        if self.volunteer_type:
            data['volunteer_type'] = self.volunteer_type.value

        return data

    @staticmethod
    def from_dict(data):
        user = User(
            id=data.get('id'),
            name=data.get('name', ""),
            id_number=data.get('id_number', ""),
            center=data.get('center', ""),
            address=data.get('address', ""),
            phone_number=data.get('phone_number', ""),
            user_type=UserType(data.get('user_type', UserType.GUEST.value)),
            points=data.get('points', 0)
        )

        if 'volunteer_type' in data:
            user.volunteer_type = VolunteerType(data.get('volunteer_type'))

        return user