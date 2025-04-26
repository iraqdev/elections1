from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from utils.auth_service import AuthService
from utils.data_service import DataService
from utils.notification_service import NotificationService
from models.user import UserType, VolunteerType
from datetime import datetime
import threading

Builder.load_string("""
<AdminTab>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)

        ScrollView:
            id: scroll_view
            size_hint_y: 1
            bar_width: dp(0)

            MDBoxLayout:
                id: content
                orientation: 'vertical'
                adaptive_height: True
                spacing: dp(10)
                padding: dp(10)

<AdminPanelScreen>:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "لوحة تحكم المشرف"
            left_action_items: [["menu", lambda x: app.root.toggle_nav_drawer()]]
            right_action_items: [["logout", lambda x: root.logout()]]

        MDTabs:
            id: admin_tabs
            tab_indicator_height: dp(3)
            tab_indicator_type: "line"
            background_color: app.theme_cls.primary_light

            AdminTab:
                id: content_tab
                title: "المحتوى"

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(20)
                    padding: dp(20)

                    MDLabel:
                        text: "إدارة المحتوى"
                        font_style: 'H6'
                        size_hint_y: None
                        height: dp(40)

                    MDSeparator:

                    MDRaisedButton:
                        text: "إضافة خبر جديد"
                        size_hint_x: None
                        width: dp(200)
                        on_release: root.add_news()

                    MDRaisedButton:
                        text: "إضافة فعالية جديدة"
                        size_hint_x: None
                        width: dp(200)
                        on_release: root.add_event()

                    MDRaisedButton:
                        text: "تحديث اقتباس اليوم"
                        size_hint_x: None
                        width: dp(200)
                        on_release: root.add_quote()

            AdminTab:
                id: notifications_tab
                title: "الإشعارات"

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(20)
                    padding: dp(20)

                    MDLabel:
                        text: "إرسال إشعارات"
                        font_style: 'H6'
                        size_hint_y: None
                        height: dp(40)

                    MDSeparator:

                    MDRaisedButton:
                        text: "إرسال إشعار عام"
                        size_hint_x: None
                        width: dp(200)
                        on_release: root.send_general_notification()

                    MDRaisedButton:
                        text: "إرسال إشعار للمتطوعين فقط"
                        size_hint_x: None
                        width: dp(200)
                        on_release: root.send_volunteers_notification()

                    MDRaisedButton:
                        text: "إرسال إشعار تذكير بيوم الانتخابات"
                        size_hint_x: None
                        width: dp(200)
                        on_release: root.send_election_reminder()

            AdminTab:
                id: volunteers_tab
                title: "المتطوعين"

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(10)
                    padding: dp(20)

                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)

                        MDLabel:
                            text: "قائمة المتطوعين"
                            font_style: 'H6'

                        MDRaisedButton:
                            text: "تحديث"
                            on_release: root.load_volunteers()

                    MDSeparator:

                    ScrollView:
                        MDList:
                            id: volunteers_list
                            padding: dp(10)

            AdminTab:
                id: voters_tab
                title: "الناخبين"

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(10)
                    padding: dp(20)

                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)

                        MDLabel:
                            text: "قائمة الناخبين المسجلين"
                            font_style: 'H6'

                        MDRaisedButton:
                            text: "تحديث"
                            on_release: root.load_voters()

                    MDSeparator:

                    ScrollView:
                        MDList:
                            id: voters_list
                            padding: dp(10)

            AdminTab:
                id: statistics_tab
                title: "الإحصائيات"

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(20)
                    padding: dp(20)

                    MDLabel:
                        text: "إحصائيات التطبيق"
                        font_style: 'H6'
                        size_hint_y: None
                        height: dp(40)

                    MDSeparator:

                    MDList:
                        id: statistics_list
                        padding: dp(10)
""")


class AdminTab(FloatLayout, MDTabsBase):
    pass


class AdminPanelScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()
        self.data_service = DataService()
        self.notification_service = NotificationService()
        self.dialog = None

    def on_enter(self):
        # تحميل البيانات عند الدخول إلى الشاشة
        self.load_volunteers()
        self.load_voters()
        self.load_statistics()

    def load_volunteers(self):
        # تحميل قائمة المتطوعين
        def load_data():
            users = self.auth_service._load_users()
            volunteers = [user for user in users if user.user_type == UserType.VOLUNTEER]

            from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget
            from kivy.clock import Clock

            def update_ui(dt):
                # حذف العناصر القديمة
                self.ids.volunteers_list.clear_widgets()

                if not volunteers:
                    from kivymd.uix.label import MDLabel
                    self.ids.volunteers_list.add_widget(
                        MDLabel(
                            text="لا يوجد متطوعين مسجلين",
                            halign="center"
                        )
                    )
                    return

                for volunteer in volunteers:
                    volunteer_type_text = ""
                    if volunteer.volunteer_type is not None:
                        if volunteer.volunteer_type.value == 0:
                            volunteer_type_text = "ميداني"
                        elif volunteer.volunteer_type.value == 1:
                            volunteer_type_text = "تصميم"
                        elif volunteer.volunteer_type.value == 2:
                            volunteer_type_text = "نشر"

                    item = ThreeLineAvatarIconListItem(
                        text=volunteer.name,
                        secondary_text=f"نوع التطوع: {volunteer_type_text}",
                        tertiary_text=f"رقم الهاتف: {volunteer.phone_number}",
                        on_release=lambda x, v=volunteer: self.show_volunteer_details(v)
                    )

                    icon = IconLeftWidget(icon="account-group")
                    item.add_widget(icon)

                    self.ids.volunteers_list.add_widget(item)

            Clock.schedule_once(update_ui)

        threading.Thread(target=load_data).start()

    def show_volunteer_details(self, volunteer):
        # عرض تفاصيل المتطوع
        volunteer_type_text = ""
        if volunteer.volunteer_type is not None:
            if volunteer.volunteer_type.value == 0:
                volunteer_type_text = "ميداني"
            elif volunteer.volunteer_type.value == 1:
                volunteer_type_text = "تصميم"
            elif volunteer.volunteer_type.value == 2:
                volunteer_type_text = "نشر"

        details = f"""
        الاسم: {volunteer.name}
        رقم البطاقة: {volunteer.id_number}
        المركز: {volunteer.center}
        العنوان: {volunteer.address}
        رقم الهاتف: {volunteer.phone_number}
        نوع التطوع: {volunteer_type_text}
        النقاط: {volunteer.points}
        """

        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="بيانات المتطوع",
            text=details,
            buttons=[
                MDFlatButton(
                    text="غلق",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="إرسال مهمة",
                    on_release=lambda x: self.send_task_to_volunteer(volunteer)
                )
            ],
        )
        self.dialog.open()

    def send_task_to_volunteer(self, volunteer):
        # إرسال مهمة للمتطوع
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField

        class TaskContent(MDBoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"
                self.size_hint_y = None
                self.height = "120dp"

                self.text_field = MDTextField(
                    hint_text="وصف المهمة",
                    multiline=True,
                    max_height="100dp"
                )
                self.add_widget(self.text_field)

        content = TaskContent()

        task_dialog = MDDialog(
            title=f"إرسال مهمة إلى {volunteer.name}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: task_dialog.dismiss()
                ),
                MDFlatButton(
                    text="إرسال",
                    on_release=lambda x: self.submit_task(content.text_field.text, volunteer, task_dialog)
                )
            ],
        )
        task_dialog.open()

    def submit_task(self, task_text, volunteer, dialog):
        # إرسال المهمة
        if not task_text.strip():
            app = MDApp.get_running_app()
            app.show_snackbar("يرجى كتابة وصف المهمة")
            return

        # إرسال إشعار للمتطوع بالمهمة الجديدة
        title = "مهمة جديدة"
        self.notification_service.create_notification(
            title=title,
            message=task_text,
            notification_type="task",
            target_users=[volunteer.id]
        )

        dialog.dismiss()

        if self.dialog:
            self.dialog.dismiss()

        app = MDApp.get_running_app()
        app.show_snackbar(f"تم إرسال المهمة بنجاح إلى {volunteer.name}")

    def load_voters(self):
        # تحميل قائمة الناخبين المسجلين
        def load_data():
            users = self.auth_service._load_users()
            voters = [user for user in users if user.user_type == UserType.REGULAR]

            from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget
            from kivy.clock import Clock

            def update_ui(dt):
                # حذف العناصر القديمة
                self.ids.voters_list.clear_widgets()

                if not voters:
                    from kivymd.uix.label import MDLabel
                    self.ids.voters_list.add_widget(
                        MDLabel(
                            text="لا يوجد ناخبين مسجلين",
                            halign="center"
                        )
                    )
                    return

                for voter in voters:
                    item = ThreeLineAvatarIconListItem(
                        text=voter.name,
                        secondary_text=f"المركز: {voter.center}",
                        tertiary_text=f"رقم الهاتف: {voter.phone_number}",
                        on_release=lambda x, v=voter: self.show_voter_details(v)
                    )

                    icon = IconLeftWidget(icon="account")
                    item.add_widget(icon)

                    self.ids.voters_list.add_widget(item)

            Clock.schedule_once(update_ui)

        threading.Thread(target=load_data).start()

    def show_voter_details(self, voter):
        # عرض تفاصيل الناخب
        details = f"""
        الاسم: {voter.name}
        رقم البطاقة: {voter.id_number}
        المركز: {voter.center}
        العنوان: {voter.address}
        رقم الهاتف: {voter.phone_number}
        النقاط: {voter.points}
        """

        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="بيانات الناخب",
            text=details,
            buttons=[
                MDFlatButton(
                    text="غلق",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="إرسال تذكير",
                    on_release=lambda x: self.send_reminder_to_voter(voter)
                )
            ],
        )
        self.dialog.open()

    def send_reminder_to_voter(self, voter):
        # إرسال تذكير للناخب
        # إرسال إشعار تذكير بمركز الاقتراع
        self.notification_service.send_election_day_reminder(voter.center, voter.id)

        if self.dialog:
            self.dialog.dismiss()

        app = MDApp.get_running_app()
        app.show_snackbar(f"تم إرسال تذكير بمركز الاقتراع إلى {voter.name}")

    def load_statistics(self):
        # تحميل إحصائيات التطبيق
        def load_data():
            users = self.auth_service._load_users()
            total_users = len(users)
            total_voters = len([user for user in users if user.user_type == UserType.REGULAR])
            total_volunteers = len([user for user in users if user.user_type == UserType.VOLUNTEER])

            from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
            from kivy.clock import Clock

            def update_ui(dt):
                # حذف العناصر القديمة
                self.ids.statistics_list.clear_widgets()

                # إجمالي المستخدمين
                item1 = TwoLineIconListItem(
                    text="إجمالي المستخدمين",
                    secondary_text=str(total_users)
                )
                item1.add_widget(IconLeftWidget(icon="account-multiple"))
                self.ids.statistics_list.add_widget(item1)

                # الناخبين المسجلين
                item2 = TwoLineIconListItem(
                    text="الناخبين المسجلين",
                    secondary_text=str(total_voters)
                )
                item2.add_widget(IconLeftWidget(icon="account"))
                self.ids.statistics_list.add_widget(item2)

                # المتطوعين
                item3 = TwoLineIconListItem(
                    text="المتطوعين",
                    secondary_text=str(total_volunteers)
                )
                item3.add_widget(IconLeftWidget(icon="account-group"))
                self.ids.statistics_list.add_widget(item3)

                # الإشعارات المرسلة
                try:
                    with open("data/notifications.json", 'r', encoding='utf-8') as f:
                        import json
                        notifications_data = json.load(f)
                        total_notifications = len(notifications_data)
                except:
                    total_notifications = 0

                item4 = TwoLineIconListItem(
                    text="إجمالي الإشعارات المرسلة",
                    secondary_text=str(total_notifications)
                )
                item4.add_widget(IconLeftWidget(icon="bell"))
                self.ids.statistics_list.add_widget(item4)

            Clock.schedule_once(update_ui)

        threading.Thread(target=load_data).start()

    def add_news(self):
        # إضافة خبر جديد
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.selection import MDSelectionList
        from kivymd.uix.selectioncontrol import MDCheckbox

        class NewsContent(MDBoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"
                self.size_hint_y = None
                self.height = "250dp"

                self.title_field = MDTextField(
                    hint_text="عنوان الخبر",
                )
                self.add_widget(self.title_field)

                self.content_field = MDTextField(
                    hint_text="محتوى الخبر",
                    multiline=True,
                    max_height="150dp"
                )
                self.add_widget(self.content_field)

                self.image_url_field = MDTextField(
                    hint_text="رابط الصورة (اختياري)"
                )
                self.add_widget(self.image_url_field)

                urgent_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp")
                from kivymd.uix.label import MDLabel
                urgent_layout.add_widget(MDLabel(text="خبر عاجل"))

                self.urgent_checkbox = MDCheckbox()
                urgent_layout.add_widget(self.urgent_checkbox)

                self.add_widget(urgent_layout)

        content = NewsContent()

        news_dialog = MDDialog(
            title="إضافة خبر جديد",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: news_dialog.dismiss()
                ),
                MDFlatButton(
                    text="إضافة",
                    on_release=lambda x: self.submit_news(
                        content.title_field.text,
                        content.content_field.text,
                        content.image_url_field.text,
                        content.urgent_checkbox.active,
                        news_dialog
                    )
                )
            ],
        )
        news_dialog.open()

    def submit_news(self, title, content, image_url, is_urgent, dialog):
        # إضافة الخبر
        if not title.strip() or not content.strip():
            app = MDApp.get_running_app()
            app.show_snackbar("يرجى تعبئة عنوان ومحتوى الخبر")
            return

        self.data_service.add_news(
            title=title,
            content=content,
            image_url=image_url if image_url.strip() else None,
            is_urgent=is_urgent
        )

        dialog.dismiss()

        app = MDApp.get_running_app()
        app.show_snackbar("تمت إضافة الخبر بنجاح")

        # إرسال إشعار للمستخدمين إذا كان الخبر عاجلاً
        if is_urgent:
            self.notification_service.create_notification(
                title="خبر عاجل",
                message=title,
                notification_type="urgent"
            )

    def add_event(self):
        # إضافة فعالية جديدة
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.pickers import MDDatePicker, MDTimePicker

        class EventContent(MDBoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"
                self.size_hint_y = None
                self.height = "400dp"

                self.title_field = MDTextField(
                    hint_text="عنوان الفعالية",
                )
                self.add_widget(self.title_field)

                self.description_field = MDTextField(
                    hint_text="وصف الفعالية",
                    multiline=True,
                    max_height="100dp"
                )
                self.add_widget(self.description_field)

                self.location_name_field = MDTextField(
                    hint_text="اسم المكان",
                )
                self.add_widget(self.location_name_field)

                self.latitude_field = MDTextField(
                    hint_text="خط العرض (مثال: 30.0444)",
                    input_filter="float"
                )
                self.add_widget(self.latitude_field)

                self.longitude_field = MDTextField(
                    hint_text="خط الطول (مثال: 31.2357)",
                    input_filter="float"
                )
                self.add_widget(self.longitude_field)

                self.image_url_field = MDTextField(
                    hint_text="رابط الصورة (اختياري)"
                )
                self.add_widget(self.image_url_field)

                date_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp")
                self.date_button = MDFlatButton(
                    text="اختيار التاريخ",
                    on_release=lambda x: self.show_date_picker()
                )
                date_layout.add_widget(self.date_button)

                self.time_button = MDFlatButton(
                    text="اختيار الوقت",
                    on_release=lambda x: self.show_time_picker()
                )
                date_layout.add_widget(self.time_button)

                self.add_widget(date_layout)

                self.selected_date = None
                self.selected_time = None

            def show_date_picker(self):
                date_dialog = MDDatePicker()
                date_dialog.bind(on_save=self.on_date_save)
                date_dialog.open()

            def on_date_save(self, instance, value, date_range):
                self.selected_date = value
                self.date_button.text = value.strftime("%Y-%m-%d")

            def show_time_picker(self):
                time_dialog = MDTimePicker()
                time_dialog.bind(on_save=self.on_time_save)
                time_dialog.open()

            def on_time_save(self, instance, value):
                self.selected_time = value
                self.time_button.text = value.strftime("%H:%M")

        content = EventContent()

        event_dialog = MDDialog(
            title="إضافة فعالية جديدة",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: event_dialog.dismiss()
                ),
                MDFlatButton(
                    text="إضافة",
                    on_release=lambda x: self.submit_event(
                        content.title_field.text,
                        content.description_field.text,
                        content.location_name_field.text,
                        content.latitude_field.text,
                        content.longitude_field.text,
                        content.image_url_field.text,
                        content.selected_date,
                        content.selected_time,
                        event_dialog
                    )
                )
            ],
        )
        event_dialog.open()

    def submit_event(self, title, description, location_name, latitude, longitude, image_url, selected_date,
                     selected_time, dialog):
        # إضافة الفعالية
        if not title.strip() or not description.strip() or not location_name.strip() or not latitude or not longitude or not selected_date or not selected_time:
            app = MDApp.get_running_app()
            app.show_snackbar("يرجى تعبئة جميع الحقول المطلوبة")
            return

        try:
            lat = float(latitude)
            lng = float(longitude)

            from datetime import datetime, timedelta
            event_date = datetime.combine(selected_date, selected_time)

            self.data_service.add_event(
                title=title,
                description=description,
                date=event_date,
                latitude=lat,
                longitude=lng,
                location_name=location_name,
                image_url=image_url if image_url.strip() else None
            )

            dialog.dismiss()

            app = MDApp.get_running_app()
            app.show_snackbar("تمت إضافة الفعالية بنجاح")

            # إرسال إشعار للمستخدمين
            self.notification_service.create_notification(
                title="فعالية جديدة",
                message=f"{title} - {location_name} - {event_date.strftime('%Y-%m-%d %H:%M')}",
                notification_type="event"
            )

        except Exception as e:
            app = MDApp.get_running_app()
            app.show_snackbar(f"حدث خطأ: {str(e)}")

    def add_quote(self):
        # إضافة اقتباس جديد
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField

        class QuoteContent(MDBoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"
                self.size_hint_y = None
                self.height = "150dp"

                self.text_field = MDTextField(
                    hint_text="اقتباس اليوم",
                    multiline=True,
                    max_height="100dp"
                )
                self.add_widget(self.text_field)

                self.image_url_field = MDTextField(
                    hint_text="رابط صورة (اختياري)"
                )
                self.add_widget(self.image_url_field)

        content = QuoteContent()

        quote_dialog = MDDialog(
            title="تحديث اقتباس اليوم",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: quote_dialog.dismiss()
                ),
                MDFlatButton(
                    text="إضافة",
                    on_release=lambda x: self.submit_quote(content.text_field.text, content.image_url_field.text,
                                                           quote_dialog)
                )
            ],
        )
        quote_dialog.open()

    def submit_quote(self, text, image_url, dialog):
        # إضافة الاقتباس
        if not text.strip():
            app = MDApp.get_running_app()
            app.show_snackbar("يرجى كتابة الاقتباس")
            return

        self.data_service.add_quote(
            text=text,
            image_url=image_url if image_url.strip() else None
        )

        dialog.dismiss()

        app = MDApp.get_running_app()
        app.show_snackbar("تم تحديث اقتباس اليوم بنجاح")

    def send_general_notification(self):
        # إرسال إشعار عام
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField

        class NotificationContent(MDBoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"
                self.size_hint_y = None
                self.height = "150dp"

                self.title_field = MDTextField(
                    hint_text="عنوان الإشعار"
                )
                self.add_widget(self.title_field)

                self.message_field = MDTextField(
                    hint_text="نص الإشعار",
                    multiline=True,
                    max_height="100dp"
                )
                self.add_widget(self.message_field)

        content = NotificationContent()

        notification_dialog = MDDialog(
            title="إرسال إشعار عام",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: notification_dialog.dismiss()
                ),
                MDFlatButton(
                    text="إرسال",
                    on_release=lambda x: self.submit_notification(content.title_field.text, content.message_field.text,
                                                                  [], notification_dialog)
                )
            ],
        )
        notification_dialog.open()

    def send_volunteers_notification(self):
        # إرسال إشعار للمتطوعين فقط
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField

        class NotificationContent(MDBoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"
                self.size_hint_y = None
                self.height = "150dp"

                self.title_field = MDTextField(
                    hint_text="عنوان الإشعار"
                )
                self.add_widget(self.title_field)

                self.message_field = MDTextField(
                    hint_text="نص الإشعار",
                    multiline=True,
                    max_height="100dp"
                )
                self.add_widget(self.message_field)

        content = NotificationContent()

        notification_dialog = MDDialog(
            title="إرسال إشعار للمتطوعين",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: notification_dialog.dismiss()
                ),
                MDFlatButton(
                    text="إرسال",
                    on_release=lambda x: self.submit_volunteers_notification(content.title_field.text,
                                                                             content.message_field.text,
                                                                             notification_dialog)
                )
            ],
        )
        notification_dialog.open()

    def submit_volunteers_notification(self, title, message, dialog):
        # إرسال إشعار للمتطوعين فقط
        if not title.strip() or not message.strip():
            app = MDApp.get_running_app()
            app.show_snackbar("يرجى تعبئة عنوان ونص الإشعار")
            return

        # الحصول على قائمة معرفات المتطوعين
        users = self.auth_service._load_users()
        volunteer_ids = [user.id for user in users if user.user_type == UserType.VOLUNTEER]

        self.submit_notification(title, message, volunteer_ids, dialog)

    def submit_notification(self, title, message, target_users, dialog):
        # إرسال الإشعار
        if not title.strip() or not message.strip():
            app = MDApp.get_running_app()
            app.show_snackbar("يرجى تعبئة عنوان ونص الإشعار")
            return

        self.notification_service.create_notification(
            title=title,
            message=message,
            notification_type="general",
            target_users=target_users
        )

        dialog.dismiss()

        app = MDApp.get_running_app()
        if target_users:
            app.show_snackbar(f"تم إرسال الإشعار إلى {len(target_users)} مستخدم")
        else:
            app.show_snackbar("تم إرسال الإشعار إلى جميع المستخدمين بنجاح")

    def send_election_reminder(self):
        # إرسال تذكير بيوم الانتخابات
        users = self.auth_service._load_users()
        voters = [user for user in users if user.user_type != UserType.GUEST]

        total_sent = 0

        for voter in voters:
            self.notification_service.send_election_day_reminder(voter.center, voter.id)
            total_sent += 1

        app = MDApp.get_running_app()
        app.show_snackbar(f"تم إرسال تذكير بيوم الانتخابات إلى {total_sent} مستخدم")

    def logout(self):
        # تسجيل الخروج من لوحة التحكم
        self.manager.current = "auth"