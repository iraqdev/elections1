from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.tab import MDTabsBase
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from datetime import datetime, timedelta
from models.user import UserType
from utils.auth_service import AuthService
from utils.data_service import DataService
from utils.notification_service import NotificationService
import threading

Builder.load_string("""
<Tab>:
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

<HomeScreen>:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "الحملة الانتخابية"
            left_action_items: [["menu", lambda x: app.root.toggle_nav_drawer()]]
            right_action_items: [["bell", lambda x: root.show_notifications()], ["logout", lambda x: root.logout()]]

        MDTabs:
            id: tabs
            tab_indicator_height: dp(3)
            tab_indicator_type: "line"
            background_color: app.theme_cls.primary_light

        MDBottomNavigation:
            id: bottom_nav

            MDBottomNavigationItem:
                name: 'home'
                text: 'الرئيسية'
                icon: 'home'

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)

                    MDLabel:
                        text: "العد التنازلي ليوم الانتخابات"
                        halign: 'center'
                        size_hint_y: None
                        height: dp(50)

                    MDLabel:
                        id: countdown_label
                        text: "00:00:00:00"
                        halign: 'center'
                        font_style: 'H4'
                        size_hint_y: None
                        height: dp(70)

                    ScrollView:
                        MDList:
                            id: news_list
                            padding: dp(10)

            MDBottomNavigationItem:
                name: 'map'
                text: 'الفعاليات'
                icon: 'map'

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)

                    MDLabel:
                        text: "خريطة الجولات والمناسبات"
                        halign: 'center'
                        size_hint_y: None
                        height: dp(50)

                    ScrollView:
                        MDList:
                            id: events_list
                            padding: dp(10)

            MDBottomNavigationItem:
                name: 'quote'
                text: 'اقتباسات'
                icon: 'format-quote-close'

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)

                    MDLabel:
                        text: "اقتباس اليوم"
                        halign: 'center'
                        size_hint_y: None
                        height: dp(50)

                    MDCard:
                        orientation: 'vertical'
                        padding: dp(20)
                        size_hint: None, None
                        size: root.width - dp(40), dp(200)
                        pos_hint: {'center_x': .5, 'center_y': .5}
                        elevation: 4

                        MDLabel:
                            id: quote_text
                            text: "سنقوم بالعمل معًا من أجل مستقبل أفضل لنا جميعًا."
                            halign: 'center'
                            font_style: 'Body1'

                        MDFlatButton:
                            text: "مشاركة الاقتباس"
                            size_hint_x: None
                            pos_hint: {'center_x': .5}
                            on_release: root.share_quote()

            MDBottomNavigationItem:
                name: 'profile'
                text: 'الملف'
                icon: 'account'

                ScrollView:
                    MDList:
                        id: profile_list
                        padding: dp(10)

            MDBottomNavigationItem:
                name: 'emergency'
                text: 'الطوارئ'
                icon: 'alert'

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)

                    MDLabel:
                        text: "قسم الطوارئ ليوم الانتخابات"
                        halign: 'center'
                        size_hint_y: None
                        height: dp(50)

                    MDCard:
                        orientation: 'vertical'
                        padding: dp(20)
                        size_hint: None, None
                        size: root.width - dp(40), dp(200)
                        pos_hint: {'center_x': .5, 'center_y': .5}
                        elevation: 4

                        MDLabel:
                            text: "استخدم هذا القسم للإبلاغ عن مشاكل أثناء يوم الانتخابات أو للحصول على معلومات طارئة حول تغييرات مراكز الاقتراع"
                            halign: 'center'

                        MDRaisedButton:
                            text: "الإبلاغ عن مشكلة"
                            pos_hint: {'center_x': .5}
                            on_release: root.report_emergency()

                        MDFlatButton:
                            text: "تحقق من تغييرات مركز الاقتراع"
                            pos_hint: {'center_x': .5}
                            on_release: root.check_polling_center_changes()
""")


class Tab(FloatLayout, MDTabsBase):
    pass


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()
        self.data_service = DataService()
        self.notification_service = NotificationService()
        self.notifications_dialog = None
        self.election_date = datetime(2025, 10, 15)  # تاريخ الانتخابات المفترض

    def on_enter(self):
        # تحديث واجهة المستخدم عند الدخول إلى الشاشة
        app = MDApp.get_running_app()
        if not app.current_user:
            app.current_user = self.auth_service.get_current_user()

        # تهيئة البيانات
        self.update_countdown()
        self.load_news()
        self.load_events()
        self.load_daily_quote()
        self.load_profile_info()

        # بدء تحديث العد التنازلي
        from kivy.clock import Clock
        self.countdown_event = Clock.schedule_interval(lambda dt: self.update_countdown(), 1)

    def on_leave(self):
        # إيقاف تحديث العد التنازلي عند مغادرة الشاشة
        from kivy.clock import Clock
        if hasattr(self, 'countdown_event'):
            Clock.unschedule(self.countdown_event)

    def update_countdown(self):
        # حساب الوقت المتبقي حتى الانتخابات
        now = datetime.now()
        time_delta = self.election_date - now

        if time_delta.total_seconds() <= 0:
            self.ids.countdown_label.text = "حان وقت الانتخابات!"
            return

        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.ids.countdown_label.text = f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"

    def load_news(self):
        # تحميل أحدث الأخبار
        def load_data():
            news = self.data_service.get_news(limit=5)

            from kivymd.uix.list import ThreeLineAvatarListItem, ImageLeftWidget
            from kivy.clock import Clock

            def update_ui(dt):
                # حذف العناصر القديمة
                self.ids.news_list.clear_widgets()

                for news_item in news:
                    item = ThreeLineAvatarListItem(
                        text=news_item.title,
                        secondary_text=news_item.content[:100] + "..." if len(
                            news_item.content) > 100 else news_item.content,
                        tertiary_text=news_item.date.strftime("%Y-%m-%d %H:%M"),
                        on_release=lambda x, n=news_item: self.show_news_details(n)
                    )

                    if news_item.image_url:
                        item.add_widget(ImageLeftWidget(source=news_item.image_url))

                    self.ids.news_list.add_widget(item)

            Clock.schedule_once(update_ui)

        threading.Thread(target=load_data).start()

    def show_news_details(self, news):
        # عرض تفاصيل الخبر المحدد
        from kivymd.uix.dialog import MDDialog

        dialog = MDDialog(
            title=news.title,
            text=news.content,
            buttons=[
                MDFlatButton(
                    text="غلق",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="مشاركة",
                    on_release=lambda x: self.share_content(news.title, news.content)
                )
            ],
        )
        dialog.open()

    def load_events(self):
        # تحميل الفعاليات القادمة
        def load_data():
            events = self.data_service.get_events(limit=10)

            from kivymd.uix.list import ThreeLineAvatarListItem, ImageLeftWidget
            from kivy.clock import Clock

            def update_ui(dt):
                # حذف العناصر القديمة
                self.ids.events_list.clear_widgets()

                for event in events:
                    item = ThreeLineAvatarListItem(
                        text=event.title,
                        secondary_text=event.description[:100] + "..." if len(
                            event.description) > 100 else event.description,
                        tertiary_text=f"{event.date.strftime('%Y-%m-%d %H:%M')} | {event.location.name}",
                        on_release=lambda x, e=event: self.show_event_details(e)
                    )

                    if event.image_url:
                        item.add_widget(ImageLeftWidget(source=event.image_url))

                    self.ids.events_list.add_widget(item)

            Clock.schedule_once(update_ui)

        threading.Thread(target=load_data).start()

    def show_event_details(self, event):
        # عرض تفاصيل الفعالية المحددة
        from kivymd.uix.dialog import MDDialog

        dialog = MDDialog(
            title=event.title,
            text=f"{event.description}\n\nالتاريخ: {event.date.strftime('%Y-%m-%d %H:%M')}\nالمكان: {event.location.name}",
            buttons=[
                MDFlatButton(
                    text="غلق",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="إضافة إلى التقويم",
                    on_release=lambda x: self.add_to_calendar(event)
                )
            ],
        )
        dialog.open()

    def add_to_calendar(self, event):
        # إضافة الفعالية إلى تقويم الجهاز
        try:
            from plyer import calendar
            calendar.add_event(
                name=event.title,
                begin=event.date,
                end=event.date + timedelta(hours=2),
                location=event.location.name,
                description=event.description
            )
            app = MDApp.get_running_app()
            app.show_snackbar("تمت إضافة الفعالية إلى التقويم")
        except Exception as e:
            app = MDApp.get_running_app()
            app.show_snackbar(f"حدث خطأ: {str(e)}")

    def load_daily_quote(self):
        # تحميل اقتباس اليوم
        def load_data():
            quote = self.data_service.get_daily_quote()

            from kivy.clock import Clock

            def update_ui(dt):
                if quote:
                    self.ids.quote_text.text = quote.text

            Clock.schedule_once(update_ui)

        threading.Thread(target=load_data).start()

    def share_quote(self):
        # مشاركة اقتباس اليوم
        quote_text = self.ids.quote_text.text
        self.share_content("اقتباس اليوم", quote_text)

    def share_content(self, title, content):
        # مشاركة محتوى (اقتباس، خبر، إلخ)
        try:
            from plyer import share
            share.share(text=f"{title}\n\n{content}\n\nمشاركة من تطبيق الحملة الانتخابية")
            app = MDApp.get_running_app()
            app.show_snackbar("تم فتح نافذة المشاركة")
        except Exception as e:
            app = MDApp.get_running_app()
            app.show_snackbar(f"حدث خطأ: {str(e)}")

    def load_profile_info(self):
        # تحميل معلومات الملف الشخصي
        app = MDApp.get_running_app()
        if not app.current_user:
            return

        from kivymd.uix.list import OneLineIconListItem, IconLeftWidget, TwoLineIconListItem

        # حذف العناصر القديمة
        self.ids.profile_list.clear_widgets()

        # إضافة معلومات المستخدم
        user = app.current_user

        # الاسم
        name_item = TwoLineIconListItem(
            text="الاسم",
            secondary_text=user.name,
        )
        name_item.add_widget(IconLeftWidget(icon="account"))
        self.ids.profile_list.add_widget(name_item)

        # نوع المستخدم
        user_type_text = ""
        if user.user_type == UserType.REGULAR:
            user_type_text = "مستخدم عادي"
        elif user.user_type == UserType.VOLUNTEER:
            user_type_text = "متطوع"

            # نوع التطوع (إذا كان متطوع)
            volunteer_type_text = ""
            if user.volunteer_type is not None:
                if user.volunteer_type.value == 0:
                    volunteer_type_text = "ميداني"
                elif user.volunteer_type.value == 1:
                    volunteer_type_text = "تصميم"
                elif user.volunteer_type.value == 2:
                    volunteer_type_text = "نشر"

                vol_type_item = TwoLineIconListItem(
                    text="نوع التطوع",
                    secondary_text=volunteer_type_text,
                )
                vol_type_item.add_widget(IconLeftWidget(icon="account-group"))
                self.ids.profile_list.add_widget(vol_type_item)
        else:
            user_type_text = "ضيف"

        user_type_item = TwoLineIconListItem(
            text="نوع المستخدم",
            secondary_text=user_type_text,
        )
        user_type_item.add_widget(IconLeftWidget(icon="account-details"))
        self.ids.profile_list.add_widget(user_type_item)

        # إظهار المعلومات الإضافية فقط للمستخدمين المسجلين (غير الضيوف)
        if user.user_type != UserType.GUEST:
            # رقم البطاقة
            id_item = TwoLineIconListItem(
                text="رقم البطاقة",
                secondary_text=user.id_number,
            )
            id_item.add_widget(IconLeftWidget(icon="card-account-details"))
            self.ids.profile_list.add_widget(id_item)

            # المركز
            center_item = TwoLineIconListItem(
                text="المركز",
                secondary_text=user.center,
            )
            center_item.add_widget(IconLeftWidget(icon="office-building-marker"))
            self.ids.profile_list.add_widget(center_item)

            # العنوان
            address_item = TwoLineIconListItem(
                text="العنوان",
                secondary_text=user.address,
            )
            address_item.add_widget(IconLeftWidget(icon="map-marker"))
            self.ids.profile_list.add_widget(address_item)

            # رقم الهاتف
            phone_item = TwoLineIconListItem(
                text="رقم الهاتف",
                secondary_text=user.phone_number,
            )
            phone_item.add_widget(IconLeftWidget(icon="phone"))
            self.ids.profile_list.add_widget(phone_item)

            # النقاط
            points_item = TwoLineIconListItem(
                text="النقاط",
                secondary_text=str(user.points),
            )
            points_item.add_widget(IconLeftWidget(icon="star"))
            self.ids.profile_list.add_widget(points_item)

        # زر تسجيل الخروج
        logout_item = OneLineIconListItem(
            text="تسجيل الخروج",
            on_release=lambda x: self.logout()
        )
        logout_item.add_widget(IconLeftWidget(icon="logout"))
        self.ids.profile_list.add_widget(logout_item)

        # زر تبديل الوضع الليلي/النهاري
        mode_text = "تفعيل الوضع الليلي" if not app.dark_mode else "تفعيل الوضع النهاري"
        mode_item = OneLineIconListItem(
            text=mode_text,
            on_release=lambda x: self.toggle_dark_mode()
        )
        mode_item.add_widget(IconLeftWidget(icon="theme-light-dark"))
        self.ids.profile_list.add_widget(mode_item)

    def toggle_dark_mode(self):
        # تبديل الوضع الليلي/النهاري
        app = MDApp.get_running_app()
        app.toggle_dark_mode()
        self.load_profile_info()  # إعادة تحميل قائمة الملف الشخصي لتحديث نص زر الوضع الليلي/النهاري

    def show_notifications(self):
        # عرض الإشعارات
        app = MDApp.get_running_app()
        user_id = app.current_user.id if app.current_user and app.current_user.user_type != UserType.GUEST else None

        def load_notifications():
            notifications = self.notification_service.get_notifications_for_user(user_id)

            from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
            from kivymd.uix.dialog import MDDialog
            from kivy.clock import Clock

            def update_ui(dt):
                items = []

                if not notifications:
                    self.notifications_dialog = MDDialog(
                        title="الإشعارات",
                        text="لا توجد إشعارات",
                        buttons=[
                            MDFlatButton(
                                text="غلق",
                                on_release=lambda x: self.notifications_dialog.dismiss()
                            )
                        ],
                    )
                    self.notifications_dialog.open()
                    return

                for notification in notifications:
                    icon = "bell"
                    if notification.notification_type == "urgent":
                        icon = "bell-alert"
                    elif notification.notification_type == "election_day":
                        icon = "calendar-alert"

                    item = TwoLineAvatarIconListItem(
                        text=notification.title,
                        secondary_text=notification.message
                    )
                    item.add_widget(IconLeftWidget(icon=icon))
                    items.append(item)

                from kivymd.uix.list import MDList
                from kivy.uix.scrollview import ScrollView

                scroll = ScrollView()
                list_view = MDList()

                for item in items:
                    list_view.add_widget(item)

                scroll.add_widget(list_view)

                self.notifications_dialog = MDDialog(
                    title="الإشعارات",
                    type="custom",
                    content_cls=scroll,
                    buttons=[
                        MDFlatButton(
                            text="غلق",
                            on_release=lambda x: self.notifications_dialog.dismiss()
                        )
                    ],
                )
                self.notifications_dialog.open()

            Clock.schedule_once(update_ui)

        threading.Thread(target=load_notifications).start()

    def logout(self):
        # تسجيل الخروج
        self.auth_service.logout()
        app = MDApp.get_running_app()
        app.current_user = None
        app.sm.current = "auth"

    def report_emergency(self):
        # الإبلاغ عن مشكلة طارئة
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.textfield import MDTextField

        class EmergencyContent(MDBoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"
                self.size_hint_y = None
                self.height = "120dp"

                self.text_field = MDTextField(
                    hint_text="وصف المشكلة",
                    multiline=True,
                    max_height="100dp"
                )
                self.add_widget(self.text_field)

        content = EmergencyContent()

        dialog = MDDialog(
            title="الإبلاغ عن مشكلة",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="إرسال",
                    on_release=lambda x: self.submit_emergency_report(content.text_field.text, dialog)
                )
            ],
        )
        dialog.open()

    def submit_emergency_report(self, report_text, dialog):
        # إرسال بلاغ الطوارئ
        if not report_text.strip():
            app = MDApp.get_running_app()
            app.show_snackbar("يرجى كتابة وصف للمشكلة")
            return

        # في تطبيق حقيقي، سيتم إرسال البلاغ إلى خادم
        # هنا نقوم بإنشاء إشعار محلي للمشرفين

        title = "بلاغ طارئ"
        self.notification_service.create_notification(
            title=title,
            message=report_text,
            notification_type="urgent"
        )

        dialog.dismiss()

        app = MDApp.get_running_app()
        app.show_snackbar("تم إرسال البلاغ بنجاح")

        # إضافة نقاط للمستخدم إذا كان مسجلاً
        if app.current_user and app.current_user.user_type != UserType.GUEST:
            self.auth_service.add_user_points(app.current_user.id, 5)
            app.show_snackbar("تمت إضافة 5 نقاط لحسابك")
            self.load_profile_info()  # تحديث عرض النقاط

    def check_polling_center_changes(self):
        # التحقق من تغييرات مركز الاقتراع
        app = MDApp.get_running_app()

        if not app.current_user or app.current_user.user_type == UserType.GUEST:
            app.show_snackbar("يرجى تسجيل الدخول أولاً للتحقق من مركز الاقتراع الخاص بك")
            return

        # في تطبيق حقيقي، سيتم التحقق من قاعدة بيانات مراكز الاقتراع
        # هنا نستخدم مركز المستخدم المخزن مسبقاً

        from kivymd.uix.dialog import MDDialog

        dialog = MDDialog(
            title="مركز الاقتراع",
            text=f"مركز الاقتراع الخاص بك هو: {app.current_user.center}\nلم يتم تسجيل أي تغييرات على مركز الاقتراع الخاص بك.",
            buttons=[
                MDFlatButton(
                    text="حسنًا",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()