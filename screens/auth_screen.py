from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from utils.auth_service import AuthService

# تعريف تصميم الواجهة باستخدام Kivy Language
Builder.load_string("""
<AuthScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

        MDBoxLayout:
            size_hint_y: None
            height: dp(50)

            MDLabel:
                text: "الحملة الانتخابية"
                halign: 'center'
                font_style: 'H4'

        Image:
            source: 'assets/images/logo.png'
            size_hint_y: None
            height: dp(200)

        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(15)
            padding: [0, dp(20), 0, 0]

            MDRaisedButton:
                text: "تسجيل"
                size_hint_x: 1
                height: dp(50)
                md_bg_color: app.theme_cls.primary_color
                on_release: root.go_to_register()

            MDRaisedButton:
                text: "تسجيل كمتطوع"
                size_hint_x: 1
                height: dp(50)
                md_bg_color: app.theme_cls.primary_color
                on_release: root.go_to_volunteer_register()

            MDRaisedButton:
                text: "دخول كضيف"
                size_hint_x: 1
                height: dp(50)
                md_bg_color: 0.5, 0.5, 0.5, 1
                on_release: root.login_as_guest()
""")


class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()

    def go_to_register(self):
        self.manager.current = "register"

    def go_to_volunteer_register(self):
        self.manager.current = "volunteer_register"

    def login_as_guest(self):
        guest_user = self.auth_service.login_as_guest()
        app = MDApp.get_running_app()
        app.current_user = guest_user
        app.show_snackbar("تم تسجيل الدخول كضيف")
        self.manager.current = "home"