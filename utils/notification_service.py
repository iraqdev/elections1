import json
import os
import uuid
from datetime import datetime
from typing import List


class Notification:
    def __init__(self, id, title, message, date, notification_type="general", target_users=None):
        self.id = id
        self.title = title
        self.message = message
        self.date = date
        self.notification_type = notification_type  # general, urgent, event, quote
        self.target_users = target_users or []  # قائمة بأرقام تعريف المستخدمين المستهدفين، إذا كان فارغًا فهو للجميع

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'notification_type': self.notification_type,
            'target_users': self.target_users
        }

    @staticmethod
    def from_dict(data):
        return Notification(
            id=data['id'],
            title=data['title'],
            message=data['message'],
            date=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
            notification_type=data.get('notification_type', 'general'),
            target_users=data.get('target_users', [])
        )


class NotificationService:
    def __init__(self):
        self.notifications_file = "data/notifications.json"
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        os.makedirs(os.path.dirname(self.notifications_file), exist_ok=True)
        if not os.path.exists(self.notifications_file):
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def create_notification(self, title, message, notification_type="general", target_users=None):
        """
        إنشاء إشعار جديد
        """
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                notifications_data = json.load(f)

            notification_id = str(uuid.uuid4())
            notification = Notification(
                id=notification_id,
                title=title,
                message=message,
                date=datetime.now(),
                notification_type=notification_type,
                target_users=target_users or []
            )

            notifications_data.append(notification.to_dict())

            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump(notifications_data, f, ensure_ascii=False)

            return notification
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None

    def get_notifications_for_user(self, user_id=None, limit=20):
        """
        الحصول على الإشعارات للمستخدم
        إذا كان user_id هو None، فإننا نفترض أنه مستخدم ضيف ويحصل فقط على الإشعارات العامة
        """
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                notifications_data = json.load(f)

            notifications = [Notification.from_dict(item) for item in notifications_data]

            # فلترة الإشعارات
            if user_id is None:
                # المستخدم ضيف، يحصل فقط على الإشعارات العامة
                filtered_notifications = [n for n in notifications if
                                          n.notification_type == "general" and not n.target_users]
            else:
                # المستخدم مسجل، يحصل على الإشعارات العامة وتلك المستهدفة له
                filtered_notifications = [n for n in notifications if not n.target_users or user_id in n.target_users]

            # ترتيب الإشعارات من الأحدث إلى الأقدم
            filtered_notifications.sort(key=lambda x: x.date, reverse=True)

            return filtered_notifications[:limit]
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []

    def send_election_day_reminder(self, polling_center, user_id=None):
        """
        إرسال تذكير بيوم الانتخابات مع مركز الاقتراع
        """
        title = "تذكير بيوم الانتخابات"
        message = f"غدًا هو يوم الانتخابات! مركز الاقتراع الخاص بك هو: {polling_center}."
        target_users = [user_id] if user_id else []

        return self.create_notification(
            title=title,
            message=message,
            notification_type="election_day",
            target_users=target_users
        )