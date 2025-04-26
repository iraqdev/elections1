from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from utils.auth_service import AuthService

Builder.load_string("""
<RegisterScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)

            MDIconButton:
                icon: 'arrow-right'
                on_release: root.go_back()

            MDLabel:
                text: "تسجيل"
                halign: 'center'
                font_style: 'H5'

            Widget:
                size_hint_x: None
                width: dp(48)

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                padding: [0, dp(20), 0, dp(20)]
                size_hint_y: None
                height: self.minimum_height

                MDTextField:
                    id: name_field
                    hint_text: "الاسم"
                    helper_text: "أدخل الاسم كاملاً"
                    helper_text_mode: "on_focus"
                    required: True
                    line_color_normal: app.theme_cls.primary_color
                    line_color_focus: app.theme_cls.primary_color
                    font_name: "assets/fonts/Cairo-Regular.ttf"

                MDTextField:
                    id: id_number_field
                    hint_text: "رقم البطاقة"
                    helper_text: "أدخل رقم البطاقة الشخصية"
                    helper_text_mode: "on_focus"
                    required: True
                    input_filter: 'int'
                    line_color_normal: app.theme_cls.primary_color
                    line_color_focus: app.theme_cls.primary_color
                    font_name: "assets/fonts/Cairo-Regular.ttf"

                MDTextField:
                    id: center_field
                    hint_text: "المركز"
                    helper_text: "أدخل اسم المركز الانتخابي"
                    helper_text_mode: "on_focus"
                    required: True
                    line_color_normal: app.theme_cls.primary_color
                    line_color_focus: app.theme_cls.primary_color
                    font_name: "assets/fonts/Cairo-Regular.ttf"

                MDTextField:
                    id: address_field
                    hint_text: "العنوان"
                    helper_text: "أدخل العنوان بالتفصيل"
                    helper_text_mode: "on_focus"
                    required: True
                    multiline: True
                    line_color_normal: app.theme_cls.primary_color
                    line_color_focus: app.theme_cls.primary_color
                    font_name: "assets/fonts/Cairo-Regular.ttf"

                MDTextField:
                    id: phone_field
                    hint_text: "رقم الهاتف"
                    helper_text: "أدخل رقم الهاتف"
                    helper_text_mode: "on_focus"
                    required: True
                    input_filter: 'int'
                    line_color_normal: app.theme_cls.primary_color
                    line_color_focus: app.theme_cls.primary_color
                    font_name: "assets/fonts/Cairo-Regular.ttf"

                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(50)
                    padding: [0, dp(20), 0, 0]

                    MDRaisedButton:
                        text: "التقاط صورة الهوية"
                        size_hint_x: 1
                        on_release: root.capture_id_image()
                        md_bg_color: app.theme_cls.primary_light

                Widget:
                    size_hint_y: None
                    height: dp(20)

                MDRaisedButton:
                    text: "تسجيل"
                    size_hint_x: 1
                    height: dp(50)
                    md_bg_color: app.theme_cls.primary_color
                    on_release: root.register()
""")


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()
        self.captured_id_data = None

    def go_back(self):
        self.manager.current = "auth"

    def capture_id_image(self):
        # هنا يجب تنفيذ وظيفة التقاط صورة الهوية واستخدام OCR
        try:
            from utils.ocr_service import OCRService
            from plyer import filechooser
            import threading

            def pick_image(path):
                if not path:
                    return

                app = MDApp.get_running_app()
                app.show_snackbar("جاري معالجة صورة الهوية...")

                # معالجة الصورة في خيط منفصل لتجنب تجميد واجهة المستخدم
                def process_image():
                    ocr_service = OCRService()
                    self.captured_id_data = ocr_service.extract_id_info(path[0])

                    # تحديث الحقول في الواجهة الرئيسية
                    def update_ui():
                        if self.captured_id_data["name"]:
                            self.ids.name_field.text = self.captured_id_data["name"]
                        if self.captured_id_data["id_number"]:
                            self.ids.id_number_field.text = self.captured_id_data["id_number"]
                        if self.captured_id_data["address"]:
                            self.ids.address_field.text = self.captured_id_data["address"]
                        app.show_snackbar("تم استخراج البيانات من صورة الهوية")

                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: update_ui(), 0)

                threading.Thread(target=process_image).start()

            filechooser.open_file(on_selection=pick_image, filters=[("Image Files", "*.jpg", "*.jpeg", "*.png")])

        except Exception as e:
            app = MDApp.get_running_app()
            app.show_snackbar(f"خطأ: {str(e)}")

    def register(self):
        name = self.ids.name_field.text.strip()
        id_number = self.ids.id_number_field.text.strip()
        center = self.ids.center_field.text.strip()
        address = self.ids.address_field.text.strip()
        phone = self.ids.phone_field.text.strip()

        if not name or not id_number or not center or not address or not phone:
            app = MDApp.get_running_app()
            app.show_snackbar("جميع الحقول مطلوبة")
            return

        try:
            new_user = self.auth_service.register(
                name=name,
                id_number=id_number,
                center=center,
                address=address,
                phone_number=phone
            )

            app = MDApp.get_running_app()
            app.current_user = new_user
            app.show_snackbar("تم التسجيل بنجاح")
            self.manager.current = "home"

        except ValueError as e:
            app = MDApp.get_running_app()
            app.show_snackbar(str(e))
        except Exception as e:
            app = MDApp.get_running_app()
            app.show_snackbar(f"خطأ: {str(e)}")