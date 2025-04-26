from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
import threading

Builder.load_string("""
<LiveStreamScreen>:
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "البث المباشر"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(20)

            Image:
                id: stream_image
                source: "assets/images/live_placeholder.png"
                size_hint_y: None
                height: dp(250)

            MDLabel:
                id: stream_title
                text: "لا يوجد بث مباشر حالياً"
                halign: 'center'
                font_style: 'H6'
                size_hint_y: None
                height: dp(40)

            MDLabel:
                id: stream_description
                text: "سيتم إعلامك عند بدء البث المباشر القادم"
                halign: 'center'
                size_hint_y: None
                height: dp(60)

            MDSeparator:

            MDLabel:
                text: "التعليقات"
                font_style: 'H6'
                size_hint_y: None
                height: dp(40)

            ScrollView:
                MDList:
                    id: comments_list
                    padding: dp(10)

            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(60)
                spacing: dp(10)

                MDTextField:
                    id: comment_field
                    hint_text: "أضف تعليقاً..."
                    helper_text: "اكتب تعليقك هنا"
                    helper_text_mode: "on_focus"
                    multiline: False

                MDIconButton:
                    icon: "send"
                    on_release: root.add_comment()
""")


class LiveStreamScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.comments = []
        self.current_stream = None

    def on_enter(self):
        # تحميل البث المباشر الحالي إن وجد
        self.load_stream()

        # تحميل التعليقات
        self.load_comments()

    def load_stream(self):
        # في تطبيق حقيقي، ستقوم بالاتصال بخادم البث المباشر
        # هنا نقوم بمحاكاة وجود بث مباشر

        # التحقق مما إذا كان هناك بث مباشر حالياً
        is_live = False

        if is_live:
            self.ids.stream_title.text = "بث مباشر: لقاء مع المرشح"
            self.ids.stream_description.text = "حوار مباشر حول برنامج الحملة الانتخابية والرد على أسئلة الناخبين"
            # في تطبيق حقيقي، ستقوم بتحميل البث المباشر من خادم البث
        else:
            self.ids.stream_title.text = "لا يوجد بث مباشر حالياً"
            self.ids.stream_description.text = "سيتم إعلامك عند بدء البث المباشر القادم"

    def load_comments(self):
        # تحميل التعليقات
        self.comments = [
            {"user": "أحمد", "text": "متى سيبدأ البث القادم؟"},
            {"user": "فاطمة", "text": "لدي سؤال حول برنامج الحملة الانتخابية"},
            {"user": "محمد", "text": "شكراً على البث السابق، كان مفيداً جداً"}
        ]

        # عرض التعليقات في القائمة
        self.update_comments_list()

    def update_comments_list(self):
        # تحديث قائمة التعليقات
        self.ids.comments_list.clear_widgets()

        from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget

        for comment in self.comments:
            item = TwoLineAvatarListItem(
                text=comment["user"],
                secondary_text=comment["text"]
            )

            avatar = ImageLeftWidget(source="assets/images/user_avatar.png")
            item.add_widget(avatar)

            self.ids.comments_list.add_widget(item)

    def add_comment(self):
        # إضافة تعليق جديد
        comment_text = self.ids.comment_field.text.strip()

        if not comment_text:
            return

        app = MDApp.get_running_app()
        user_name = app.current_user.name if app.current_user else "ضيف"

        # إضافة التعليق الجديد
        self.comments.append({
            "user": user_name,
            "text": comment_text
        })

        # تحديث القائمة
        self.update_comments_list()

        # مسح حقل التعليق
        self.ids.comment_field.text = ""

        # في تطبيق حقيقي، ستقوم بإرسال التعليق إلى خادم البث المباشر

    def go_back(self):
        # العودة إلى الشاشة السابقة
        self.manager.current = "home"