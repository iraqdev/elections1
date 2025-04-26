import os

from models.user import UserType

os.environ['KIVY_GL_BACKEND'] = 'sdl2'
os.environ['KIVY_TEXT_DIRECTION'] = 'rtl'
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock

from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer
# استيراد الشاشات
from screens.auth_screen import AuthScreen
from screens.register_screen import RegisterScreen
from screens.volunteer_register_screen import VolunteerRegisterScreen
from screens.home_screen import HomeScreen
from screens.live_stream_screen import LiveStreamScreen
from screens.admin.admin_login_screen import AdminLoginScreen
from screens.admin.admin_panel_screen import AdminPanelScreen
from kivy.resources import resource_add_path
import os

# تعيين الخطوط للتطبيق بشكل صحيح
from kivy.core.text import LabelBase
LabelBase.register(name="Cairo",
                   fn_regular="assets/fonts/Cairo-Regular.ttf",
                   fn_bold="assets/fonts/Cairo-Bold.ttf")

# ضبط إعدادات اللغة العربية
from kivy.config import Config
Config.set('kivy', 'default_font', ['Cairo', 'assets/fonts/Cairo-Regular.ttf'])
Config.set('kivy', 'log_level', 'info')
Config.set('graphics', 'multisamples', '0')
Config.set('input', 'mouse', 'mouse')

# تعريف drawer التنقل
Builder.load_string("""
<NavigationDrawerContent>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)

    MDBoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(150)
        padding: dp(10)

        Image:
            source: 'assets/images/logo.png'

        MDLabel:
            text: "الحملة الانتخابية"
            halign: 'right'  # تغيير من 'center' إلى 'right'
            font_style: 'H6'
            font_name: 'Cairo'  # أضف هذا السطر
            size_hint_y: None
            height: dp(30)

    MDSeparator:

    ScrollView:
        MDList:
            id: drawer_list
""")

# تحميل ملف تنسيق الخطوط العربية
Builder.load_file('arabic_text.kv')


class NavigationDrawerContent(BoxLayout):
    pass


class ElectionCampaignApp(MDApp):
    dark_mode = BooleanProperty(False)
    current_user = None

    def build(self):
        Window.size = (360, 640)
        Window.borderless = False
        Window.right_to_left = False

        self.theme_cls.primary_palette = "Blue"

        # تعيين الخط الافتراضي للتطبيق
        self.theme_cls.font_styles["H1"] = ["Cairo", 96, False, -1.5]
        self.theme_cls.font_styles["H2"] = ["Cairo", 60, False, -0.5]
        self.theme_cls.font_styles["H3"] = ["Cairo", 48, False, 0]
        self.theme_cls.font_styles["H4"] = ["Cairo", 34, False, 0.25]
        self.theme_cls.font_styles["H5"] = ["Cairo", 24, False, 0]
        self.theme_cls.font_styles["H6"] = ["Cairo", 20, False, 0.15]
        self.theme_cls.font_styles["Subtitle1"] = ["Cairo", 16, False, 0.15]
        self.theme_cls.font_styles["Subtitle2"] = ["Cairo", 14, True, 0.1]
        self.theme_cls.font_styles["Body1"] = ["Cairo", 16, False, 0.5]
        self.theme_cls.font_styles["Body2"] = ["Cairo", 14, False, 0.25]
        self.theme_cls.font_styles["Button"] = ["Cairo", 14, True, 1.25]
        self.theme_cls.font_styles["Caption"] = ["Cairo", 12, False, 0.4]
        self.theme_cls.font_styles["Overline"] = ["Cairo", 10, True, 1.5]

        # تعيين لون خلفية التطبيق
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"

        # إنشاء navigation drawer
        self.navigation_drawer = MDNavigationDrawer()
        self.navigation_drawer_content = NavigationDrawerContent()
        self.navigation_drawer.add_widget(self.navigation_drawer_content)

        # إنشاء مدير الشاشات
        self.sm = ScreenManager()

        # إضافة الشاشات
        self.sm.add_widget(AuthScreen(name="auth"))
        self.sm.add_widget(RegisterScreen(name="register"))
        self.sm.add_widget(VolunteerRegisterScreen(name="volunteer_register"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(LiveStreamScreen(name="live_stream"))
        self.sm.add_widget(AdminLoginScreen(name="admin_login"))
        self.sm.add_widget(AdminPanelScreen(name="admin_panel"))

        # التحقق من وجود مستخدم مسجل سابقاً
        from utils.auth_service import AuthService
        auth_service = AuthService()
        user = auth_service.get_current_user()

        if user:
            self.current_user = user
            self.sm.current = "home"
        else:
            self.sm.current = "auth"

        # تحديث قائمة التنقل
        self.update_navigation_drawer()

        return self.sm

    def update_navigation_drawer(self):
        # تحديث قائمة التنقل في الـ drawer
        drawer_list = self.navigation_drawer_content.ids.drawer_list
        drawer_list.clear_widgets()

        from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

        # الصفحة الرئيسية
        home_item = OneLineIconListItem(
            text="الصفحة الرئيسية",
            on_release=lambda x: self.navigate_to("home")
        )
        home_item.add_widget(IconLeftWidget(icon="home"))
        drawer_list.add_widget(home_item)

        # البث المباشر
        live_item = OneLineIconListItem(
            text="البث المباشر",
            on_release=lambda x: self.navigate_to("live_stream")
        )
        live_item.add_widget(IconLeftWidget(icon="video"))
        drawer_list.add_widget(live_item)

        # قسم الطوارئ
        emergency_item = OneLineIconListItem(
            text="قسم الطوارئ",
            on_release=lambda x: self.navigate_to_tab("home", "emergency")
        )
        emergency_item.add_widget(IconLeftWidget(icon="alert"))
        drawer_list.add_widget(emergency_item)

        # لوحة تحكم المشرف (تظهر فقط للمشرف)
        if self.current_user and hasattr(self.current_user,
                                         'user_type') and self.current_user.user_type == UserType.ADMIN:
            admin_item = OneLineIconListItem(
                text="لوحة التحكم",
                on_release=lambda x: self.navigate_to("admin_panel")
            )
            admin_item.add_widget(IconLeftWidget(icon="shield-account"))
            drawer_list.add_widget(admin_item)
        else:
            # للوصول إلى لوحة التحكم للتجربة
            admin_login_item = OneLineIconListItem(
                text="تسجيل دخول المشرف",
                on_release=lambda x: self.navigate_to("admin_login")
            )
            admin_login_item.add_widget(IconLeftWidget(icon="shield-account"))
            drawer_list.add_widget(admin_login_item)

        # تسجيل الخروج (يظهر فقط إذا كان المستخدم مسجل الدخول)
        if self.current_user:
            from utils.auth_service import AuthService
            auth_service = AuthService()

            logout_item = OneLineIconListItem(
                text="تسجيل الخروج",
                on_release=lambda x: self.logout()
            )
            logout_item.add_widget(IconLeftWidget(icon="logout"))
            drawer_list.add_widget(logout_item)

    def navigate_to(self, screen_name):
        # الانتقال إلى شاشة محددة
        self.sm.current = screen_name
        self.navigation_drawer.set_state("close")

    def navigate_to_tab(self, screen_name, tab_name):
        # الانتقال إلى شاشة محددة وعلامة تبويب محددة
        self.sm.current = screen_name

        # إذا كان طلب التنقل إلى قسم الطوارئ
        if screen_name == "home" and tab_name == "emergency":
            # تأكد من أن الشاشة الرئيسية قد تم تحميلها
            home_screen = self.sm.get_screen("home")
            # انتقل إلى علامة تبويب الطوارئ
            if hasattr(home_screen.ids, 'bottom_navigation'):
                home_screen.ids.bottom_navigation.switch_tab(tab_name)

        # إغلاق القائمة الجانبية
        self.navigation_drawer.set_state("close")
        # تحديث الواجهة
        Clock.schedule_once(lambda dt: None, 0.1)

    def logout(self):
        # تسجيل الخروج
        from utils.auth_service import AuthService
        auth_service = AuthService()
        auth_service.logout()

        self.current_user = None
        self.sm.current = "auth"
        self.navigation_drawer.set_state("close")
        self.update_navigation_drawer()

    def toggle_nav_drawer(self):
        # فتح/غلق drawer التنقل
        self.navigation_drawer.set_state("open" if self.navigation_drawer.state == "close" else "close")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.theme_cls.theme_style = "Dark" if self.dark_mode else "Light"

    def show_snackbar(self, text):
        Snackbar(
            text=text,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=(Window.width - (dp(10) * 2)) / Window.width,
            duration=3,
            font_name="Cairo",
        ).open()

    def show_dialog(self, title, text, ok_button_text="موافق", callback=None):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text=ok_button_text,
                    font_name="Cairo",
                    on_release=lambda x: self.dismiss_dialog(dialog, callback)
                )
            ]
        )
        dialog.open()

    def dismiss_dialog(self, dialog, callback=None):
        dialog.dismiss()
        if callback:
            callback()


if __name__ == "__main__":
    ElectionCampaignApp().run()