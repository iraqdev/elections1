class SharingService:
    @staticmethod
    def share_to_platform(platform, content, title=""):
        """
        مشاركة المحتوى إلى منصة محددة

        المنصات المدعومة:
        - whatsapp
        - telegram
        - facebook
        - twitter
        - instagram
        - general (مشاركة عامة باستخدام نافذة مشاركة النظام)
        """
        try:
            from plyer import share
            from urllib.parse import quote
            import webbrowser

            # تنسيق المحتوى
            formatted_content = f"{title}\n\n{content}" if title else content

            if platform == "general":
                # مشاركة عامة باستخدام نافذة مشاركة النظام
                share.share(text=formatted_content)
            elif platform == "whatsapp":
                # مشاركة إلى واتساب
                encoded_content = quote(formatted_content)
                url = f"whatsapp://send?text={encoded_content}"
                webbrowser.open(url)
            elif platform == "telegram":
                # مشاركة إلى تيليجرام
                encoded_content = quote(formatted_content)
                url = f"https://t.me/share/url?url=&text={encoded_content}"
                webbrowser.open(url)
            elif platform == "facebook":
                # مشاركة إلى فيسبوك
                encoded_content = quote(formatted_content)
                url = f"https://www.facebook.com/sharer/sharer.php?u=&quote={encoded_content}"
                webbrowser.open(url)
            elif platform == "twitter":
                # مشاركة إلى تويتر
                encoded_content = quote(formatted_content)
                url = f"https://twitter.com/intent/tweet?text={encoded_content}"
                webbrowser.open(url)
            elif platform == "instagram":
                # (ملاحظة: مشاركة النصوص مباشرة إلى إنستغرام غير متاحة حالياً من خلال الويب)
                # يمكن استخدام نافذة المشاركة العامة بدلاً من ذلك
                share.share(text=formatted_content)
            else:
                # إذا كانت المنصة غير معروفة، استخدم المشاركة العامة
                share.share(text=formatted_content)

            return True
        except Exception as e:
            print(f"Error sharing: {e}")
            return False

    @staticmethod
    def show_share_dialog(content, title=""):
        """
        عرض مربع حوار للمشاركة مع خيارات المنصات المختلفة
        """
        from kivymd.app import MDApp
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDFlatButton, MDIconButton

        class ShareContent(MDBoxLayout):
            def __init__(self, content, title, **kwargs):
                super().__init__(**kwargs)
                self.content = content
                self.title = title
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.padding = "12dp"

                # إضافة العنوان
                from kivymd.uix.label import MDLabel
                self.add_widget(
                    MDLabel(
                        text="مشاركة عبر",
                        halign="center",
                        size_hint_y=None,
                        height="40dp"
                    )
                )

                # إضافة صف لأزرار المشاركة
                buttons_row1 = MDBoxLayout(
                    orientation="horizontal",
                    spacing="12dp",
                    size_hint_y=None,
                    height="56dp"
                )

                # إضافة أزرار المشاركة
                whatsapp_button = MDIconButton(
                    icon="whatsapp",
                    on_release=lambda x: self.share_to("whatsapp")
                )
                buttons_row1.add_widget(whatsapp_button)

                telegram_button = MDIconButton(
                    icon="telegram",
                    on_release=lambda x: self.share_to("telegram")
                )
                buttons_row1.add_widget(telegram_button)

                facebook_button = MDIconButton(
                    icon="facebook",
                    on_release=lambda x: self.share_to("facebook")
                )
                buttons_row1.add_widget(facebook_button)

                twitter_button = MDIconButton(
                    icon="twitter",
                    on_release=lambda x: self.share_to("twitter")
                )
                buttons_row1.add_widget(twitter_button)

                self.add_widget(buttons_row1)

                # صف ثاني لأزرار إضافية
                buttons_row2 = MDBoxLayout(
                    orientation="horizontal",
                    spacing="12dp",
                    size_hint_y=None,
                    height="56dp"
                )

                general_button = MDIconButton(
                    icon="share-variant",
                    on_release=lambda x: self.share_to("general")
                )
                buttons_row2.add_widget(general_button)

                self.add_widget(buttons_row2)

            def share_to(self, platform):
                SharingService.share_to_platform(platform, self.content, self.title)
                app = MDApp.get_running_app()
                app.show_snackbar(f"جاري المشاركة عبر {platform}")

                # إغلاق مربع الحوار
                if hasattr(self.parent.parent.parent, "dismiss"):
                    self.parent.parent.parent.dismiss()

        content_widget = ShareContent(content, title)

        dialog = MDDialog(
            title="مشاركة المحتوى",
            type="custom",
            content_cls=content_widget,
            buttons=[
                MDFlatButton(
                    text="إلغاء",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )

        dialog.open()