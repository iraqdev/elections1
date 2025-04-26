from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

Builder.load_string("""
<AdminLoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(50)

            MDLabel:
                text: "لوحة تحكم المشرف"
                halign: 'center'
                font_style: 'H5'

        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(20)
            padding: [0, dp(50), 0, 0]

            Image:
                source: 'assets/images/admin_logo.png'
                size_hint_y: None
                height: dp(150)

            MDTextField:
                id: username_field
                hint_text: "اسم المستخدم"
                helper_text: "أدخل اسم المستخدم الخاص بك"
                helper_text_mode: "on_focus"
                icon_right: "account"
                icon_right_color: app.theme_cls.primary_color
                pos_hint: {'center_x': .5}
                size_hint_x: None
                width: dp(300)

            MDTextField:
                id: password_field
                hint_text: "كلمة المرور"
                helper_text: "أدخل كلمة المرور الخاصة بك"
                helper_text_mode: "on_focus"
                icon_right: "key"
                icon_right_color: app.theme_cls.primary_color
                pos_hint: {'center_x': .5}
                size_hint_x: None
                width: dp(300)
                password: True

            Widget:
                size_hint_y: None
                height: dp(50)

            MDRaisedButton:
                text: "تسجيل الدخول"
                pos_hint: {'center_x': .5}
                size_hint_x: None
                width: dp(200)
                on_release: root.login()

            MDFlatButton:
                text: "العودة للتطبيق"
                pos_hint: {'center_x': .5}
                on_release: root.go_back()
""")


class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def login(self):
        username = self.ids.username_field.text.strip()
        password = self.ids.password_field.text.strip()

        # في تطبيق حقيقي، سيتم التحقق من قاعدة بيانات المشرفين
        # هنا نستخدم بيانات ثابتة للتوضيح
        if username == "admin" and password == "admin123":
            self.manager.current = "admin_panel"
        else:
            self.show_error_dialog("خطأ في تسجيل الدخول", "اسم المستخدم أو كلمة المرور غير صحيحة")

    def show_error_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="حسنًا",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def go_back(self):
        self.manager.current = "auth"