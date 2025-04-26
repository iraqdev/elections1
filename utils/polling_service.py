import json
import os
from datetime import datetime


class PollingService:
    def __init__(self):
        self.polling_changes_file = "data/polling_changes.json"
        self.emergencies_file = "data/emergencies.json"
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        os.makedirs(os.path.dirname(self.polling_changes_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.emergencies_file), exist_ok=True)

        if not os.path.exists(self.polling_changes_file):
            with open(self.polling_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

        if not os.path.exists(self.emergencies_file):
            with open(self.emergencies_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def check_polling_center_change(self, user_center):
        """
        التحقق مما إذا كان هناك تغيير في مركز الاقتراع للمستخدم
        """
        try:
            with open(self.polling_changes_file, 'r', encoding='utf-8') as f:
                changes = json.load(f)

            for change in changes:
                if change.get("old_center") == user_center:
                    return {
                        "changed": True,
                        "new_center": change.get("new_center"),
                        "reason": change.get("reason", "")
                    }

            return {
                "changed": False,
                "new_center": user_center,
                "reason": ""
            }
        except Exception as e:
            print(f"Error checking polling center change: {e}")
            return {
                "changed": False,
                "new_center": user_center,
                "reason": ""
            }

    def report_emergency(self, user_id, center, description):
        """
        الإبلاغ عن مشكلة طارئة في يوم الانتخابات
        """
        try:
            with open(self.emergencies_file, 'r', encoding='utf-8') as f:
                emergencies = json.load(f)

            emergencies.append({
                "user_id": user_id,
                "center": center,
                "description": description,
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "status": "pending"  # pending, in_progress, resolved
            })

            with open(self.emergencies_file, 'w', encoding='utf-8') as f:
                json.dump(emergencies, f, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error reporting emergency: {e}")
            return False

    def get_emergencies(self, status=None):
        """
        الحصول على قائمة المشاكل الطارئة
        يمكن تصفيتها حسب الحالة (pending, in_progress, resolved)
        """
        try:
            with open(self.emergencies_file, 'r', encoding='utf-8') as f:
                emergencies = json.load(f)

            if status:
                emergencies = [e for e in emergencies if e.get("status") == status]

            return emergencies
        except Exception as e:
            print(f"Error getting emergencies: {e}")
            return []

    def update_emergency_status(self, emergency_index, new_status):
        """
        تحديث حالة مشكلة طارئة
        """
        try:
            with open(self.emergencies_file, 'r', encoding='utf-8') as f:
                emergencies = json.load(f)

            if 0 <= emergency_index < len(emergencies):
                emergencies[emergency_index]["status"] = new_status

                with open(self.emergencies_file, 'w', encoding='utf-8') as f:
                    json.dump(emergencies, f, ensure_ascii=False)

                return True

            return False
        except Exception as e:
            print(f"Error updating emergency status: {e}")
            return False

    def add_polling_center_change(self, old_center, new_center, reason=""):
        """
        إضافة تغيير في مركز اقتراع
        """
        try:
            with open(self.polling_changes_file, 'r', encoding='utf-8') as f:
                changes = json.load(f)

            # التحقق من وجود تغيير مسبق لنفس المركز
            for change in changes:
                if change.get("old_center") == old_center:
                    change["new_center"] = new_center
                    change["reason"] = reason

                    with open(self.polling_changes_file, 'w', encoding='utf-8') as f:
                        json.dump(changes, f, ensure_ascii=False)

                    return True

            # إضافة تغيير جديد
            changes.append({
                "old_center": old_center,
                "new_center": new_center,
                "reason": reason
            })

            with open(self.polling_changes_file, 'w', encoding='utf-8') as f:
                json.dump(changes, f, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error adding polling center change: {e}")
            return False