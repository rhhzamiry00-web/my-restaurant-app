from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.card import MDCard 
from kivymd.uix.label import MDLabel
from kivymd.uix.fitimage import FitImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton 
from kivymd.uix.gridlayout import MDGridLayout
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import json
import os
from datetime import datetime

# تابع اصلی برای اصلاح متن فارسی
def get_farsi(text):
    if not text or text.strip() == "": return ""
    try:
        reshaped_text = reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text

def save_order_to_history(order_data):
    file_path = 'history.json'
    history = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
            except:
                history = []
    history.append(order_data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

class Tab(MDFloatLayout, MDTabsBase):
    pass

class FoodCard(MDCard):
    def __init__(self, name, price, image_path, **kwargs):
        super().__init__(**kwargs)
        self.food_name = name
        self.food_price = price
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = ("160dp", "280dp")
        self.padding = "8dp"
        self.spacing = "4dp"
        self.radius = [15, ]
        self.elevation = 2
        
        self.add_widget(FitImage(source=image_path, radius=[15, 15, 0, 0], size_hint_y=2.5))
        self.add_widget(MDLabel(text=get_farsi(name), font_name="Vazir", halign="center", bold=True))
        self.add_widget(MDLabel(text=get_farsi(price + " تومان"), font_name="Vazir", halign="center", theme_text_color="Secondary", font_style="Caption"))

        controls = MDBoxLayout(orientation="horizontal", spacing="10dp", adaptive_size=True, pos_hint={"center_x": .5})
        btn_plus = MDIconButton(icon="plus-circle", theme_text_color="Custom", text_color=(0.9, 0.1, 0.1, 1))
        btn_plus.bind(on_release=lambda x: self.update_count(1))
        self.lbl_count = MDLabel(text="0", halign="center", adaptive_width=True)
        btn_minus = MDIconButton(icon="minus-circle", theme_text_color="Custom", text_color=(0.5, 0.5, 0.5, 1))
        btn_minus.bind(on_release=lambda x: self.update_count(-1))
        
        controls.add_widget(btn_plus)
        controls.add_widget(self.lbl_count)
        controls.add_widget(btn_minus)
        self.add_widget(controls)

    def update_count(self, delta):
        app = MDApp.get_running_app()
        try:
            unit_price = int(str(self.food_price).replace(',', '').replace('،', '').strip())
        except:
            unit_price = 0

        if self.food_name not in app.cart:
            app.cart[self.food_name] = {"count": 0, "price": unit_price}
        
        old_count = app.cart[self.food_name]["count"]
        new_count = max(0, old_count + delta)
        
        if new_count > 0:
            app.cart[self.food_name]["count"] = new_count
        else:
            new_count = 0
            if self.food_name in app.cart:
                del app.cart[self.food_name]

        self.lbl_count.text = str(new_count)

KV = '''
ScreenManager:
    WelcomeScreen:
    MenuScreen:
    CartScreen:
    HistoryScreen:

<WelcomeScreen>:
    name: 'welcome'
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDLabel:
            text: root.get_text("ریحون")
            halign: "center"
            pos_hint: {"center_y": .7}
            font_style: "H2"
            font_name: "Vazir"
            theme_text_color: "Custom"
            text_color: 0.9, 0.1, 0.1, 1
        MDLabel:
            text: root.get_text("به فست فود ریحون خوش آمدید")
            font_name: "Vazir"
            halign: "center"
            pos_hint: {"center_y": .45}
            font_style: "H5"
        MDRaisedButton:
            text: root.get_text("ورود به منوی غذا")
            font_name: "Vazir"
            pos_hint: {"center_x": .5, "center_y": .35} # موقعیت دکمه اول
            size_hint: .7, .08
            md_bg_color: 0.9, 0.1, 0.1, 1
            on_release: root.manager.current = 'menu'

        # دکمه دوم (تاریخچه)
        MDRaisedButton:
            text: root.get_text("مشاهده تاریخچه سفارشات")
            font_name: "Vazir"
            pos_hint: {"center_x": .5, "center_y": .22} # پایین‌تر از دکمه اول قرار گرفت
            size_hint: .7, .08
            md_bg_color: 0.3, 0.3, 0.3, 1
            on_release: root.manager.current = 'history'
<MenuScreen>:
    name: 'menu'
    # استفاده از لایه FloatLayout برای اینکه دکمه روی بقیه قرار بگیرد
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1

        MDBoxLayout:
            orientation: 'vertical'
            pos_hint: {"top": 1}
            MDTopAppBar:
                title: root.get_text("منوی ریحون")
                font_name: "Vazir"
                anchor_title: "right"
                md_bg_color: 0.9, 0.1, 0.1, 1
                left_action_items: [["arrow-left", lambda x: root.go_back()]]
            MDTabs:
                id: tabs
                # این بخش برای اطمینان از فضای کافی دکمه است
                Tab:
                    title: root.get_text("پیتزا")
                    ScrollView:
                        MDGridLayout:
                            id: pizza_grid
                            cols: 2
                            padding: ["10dp", "10dp", "10dp", "80dp"] # پدینگ پایین اضافه شد
                            spacing: "10dp"
                            adaptive_height: True
                Tab:
                    title: root.get_text("برگر")
                    ScrollView:
                        MDGridLayout:
                            id: burger_grid
                            cols: 2
                            padding: ["10dp", "10dp", "10dp", "80dp"] # پدینگ پایین اضافه شد
                            spacing: "10dp"
                            adaptive_height: True
                Tab:
                    title: root.get_text("پاستا")
                    ScrollView:
                        MDGridLayout:
                            id: pasta_grid
                            cols: 2
                            padding: ["10dp", "10dp", "10dp", "80dp"]
                            spacing: "10dp"
                            adaptive_height: True
                Tab:
                    title: root.get_text("سالاد")
                    ScrollView:
                        MDGridLayout:
                            id: salad_grid
                            cols: 2
                            padding: ["10dp", "10dp", "10dp", "80dp"]
                            spacing: "10dp"
                            adaptive_height: True
        
        # دکمه سبد خرید با پارامترهای اجباری برای نمایش
        # استفاده از دکمه متنی به جای آیکون برای اطمینان از دیده شدن
        MDRaisedButton:
            text: root.get_text("سبد خرید")
            font_name: "Vazir"
            md_bg_color: 0.9, 0.1, 0.1, 1
            text_color: 1, 1, 1, 1
            size_hint: None, None
            size: "100dp", "50dp"
            pos_hint: {"center_x": .18, "center_y": .12}
            on_release: root.manager.current = 'cart'
            elevation: 1.5

<CartScreen>:
    name: 'cart'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        
        MDTopAppBar:
            title: root.get_text("تایید نهایی سفارش")
            font_name: "Vazir"
            anchor_title: "right"
            md_bg_color: 0.9, 0.1, 0.1, 1
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "15dp"

                MDLabel:
                    text: root.get_text("لیست سفارشات شما")
                    font_name: "Vazir"
                    halign: "right"
                    bold: True
                    adaptive_height: True

                # --- اصلاح جدول برای جلوگیری از روی هم افتادن متن‌ها ---
                MDGridLayout:
                    id: cart_table
                    cols: 3
                    adaptive_height: True
                    row_default_height: "40dp"  # ارتفاع ثابت برای هر سطر
                    row_force_default: True
                    spacing: "10dp"

                MDSeparator:

                # --- بخش نام با پیش‌نمایش زنده ---
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    spacing: "5dp"
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        adaptive_height: True
                        MDLabel:
                            id: name_preview
                            text: ""
                            font_name: "Vazir"
                            halign: "left"
                            theme_text_color: "Error"
                            font_style: "Caption"
                        MDLabel:
                            text: root.get_text("نام و نام خانوادگی:")
                            font_name: "Vazir"
                            halign: "right"
                            adaptive_height: True

                    MDTextField:
                        id: user_name
                        mode: "rectangle"
                        font_name: "Vazir"
                        on_text: name_preview.text = root.get_text(self.text)
                        size_hint_y: None
                        height: "48dp"

                # --- بخش آدرس با پیش‌نمایش زنده ---
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    spacing: "5dp"

                    MDBoxLayout:
                        orientation: 'horizontal'
                        adaptive_height: True
                        MDLabel:
                            id: addr_preview
                            text: ""
                            font_name: "Vazir"
                            halign: "left"
                            theme_text_color: "Error"
                            font_style: "Caption"
                        MDLabel:
                            text: root.get_text("آدرس دقیق ارسال:")
                            font_name: "Vazir"
                            halign: "right"
                            adaptive_height: True

                    MDTextField:
                        id: user_address
                        mode: "rectangle"
                        multiline: True
                        font_name: "Vazir"
                        on_text: addr_preview.text = root.get_text(self.text)
                        size_hint_y: None
                        height: "80dp"

                MDLabel:
                    id: total_price_label
                    text: ""
                    font_name: "Vazir"
                    halign: "center"
                    font_style: "H6"
                    theme_text_color: "Error"

                MDRaisedButton:
                    text: root.get_text("ثبت و پرداخت نهایی")
                    font_name: "Vazir"
                    size_hint_x: 1
                    height: "50dp"
                    md_bg_color: 0, 0.6, 0, 1
                    on_release: root.process_payment()
<HistoryScreen>:
    name: 'history'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1
        MDTopAppBar:
            title: root.get_text("تاریخچه سفارشات")
            font_name: "Vazir"
            anchor_title: "right"
            md_bg_color: 0.9, 0.1, 0.1, 1
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        ScrollView:
            MDBoxLayout:
                id: history_list
                orientation: 'vertical'
                adaptive_height: True
                padding: "15dp"
                spacing: "15dp"
'''

class WelcomeScreen(Screen):
    def get_text(self, text): return get_farsi(text)

class MenuScreen(Screen):
    def get_text(self, text): return get_farsi(text)
    def go_back(self): self.manager.current = 'welcome'
    
    def on_enter(self):
        # پر کردن پیتزاها
        if 'pizza_grid' in self.ids:
            self.ids.pizza_grid.clear_widgets()
            self.ids.pizza_grid.add_widget(FoodCard("پیتزا مخصوص", "280000", "pizza1.jpg"))
            self.ids.pizza_grid.add_widget(FoodCard("پیتزا پپرونی", "240000", "pizza2.jpg"))
        
        # پر کردن برگرها
        if 'burger_grid' in self.ids:
            self.ids.burger_grid.clear_widgets()
            self.ids.burger_grid.add_widget(FoodCard("چیز برگر", "210000", "burger1.jpg"))
            self.ids.burger_grid.add_widget(FoodCard("دوبل برگر", "290000", "burger2.jpg"))

        # پر کردن پاستاها (جدید)
        if 'pasta_grid' in self.ids:
            self.ids.pasta_grid.clear_widgets()
            self.ids.pasta_grid.add_widget(FoodCard("پاستا آلفردو", "260000", "pasta1.jpg"))
            self.ids.pasta_grid.add_widget(FoodCard("پاستا گوشت", "310000", "pasta2.jpg"))

        # پر کردن سالادها (جدید)
        if 'salad_grid' in self.ids:
            self.ids.salad_grid.clear_widgets()
            self.ids.salad_grid.add_widget(FoodCard("سالاد سزار", "180000", "salad1.jpg"))
            self.ids.salad_grid.add_widget(FoodCard("سالاد فصل", "95000", "salad2.jpg"))
from kivy.clock import Clock # حتما این خط را در بالای کل فایل (بخش importها) اضافه کن

class CartScreen(Screen):
    def get_text(self, text): return get_farsi(text)
    def go_back(self): self.manager.current = 'menu'
    
    def on_enter(self):
        app = MDApp.get_running_app()
        self.ids.cart_table.clear_widgets()
        total_sum = 0
        if not app.cart:
            self.ids.cart_table.add_widget(MDLabel(text=get_farsi("سبد خرید خالی است"), font_name="Vazir", halign="right"))
        else:
            for name, info in app.cart.items():
                qty = info['count']
                price = info['price']
                line_total = qty * price
                total_sum += line_total
                self.ids.cart_table.add_widget(MDLabel(text=f"{line_total:,}", halign="left", font_name="Vazir"))
                self.ids.cart_table.add_widget(MDLabel(text=f"x{qty}", halign="center", font_name="Vazir"))
                self.ids.cart_table.add_widget(MDLabel(text=get_farsi(name), font_name="Vazir", halign="right"))
        self.ids.total_price_label.text = get_farsi(f"جمع کل: {total_sum:,} تومان")

    def process_payment(self):
        # تست سریع: اگر این پرینت را در کنسول دیدی یعنی دکمه سالم است
        print("Payment button clicked!") 
        
        app = MDApp.get_running_app()
        
        # نمایش مستقیم دیالوگ بدون پیچیدگی
        from kivymd.uix.dialog import MDDialog
        
        # اگر سبد خالی باشد، فقط یک پیام ساده بده و خارج شو
        if not app.cart:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=get_farsi("سبد خرید شما خالی است!"), font_name="Vazir").open()
            return

        self.payment_dialog = MDDialog(
            title=get_farsi("در حال ثبت"),
            text=get_farsi("سفارش شما در حال ارسال است..."),
            auto_dismiss=False
        )
        self.payment_dialog.open()
        
        # فراخوانی مرحله بعد بعد از ۲ ثانیه
        Clock.schedule_once(self.show_success, 2)

    def show_success(self, dt):
        if hasattr(self, 'payment_dialog'):
            self.payment_dialog.dismiss()
            
        import random
        tracking_code = random.randint(11200, 99800)
        
        # --- بخش جدید برای ذخیره تاریخچه ---
        app = MDApp.get_running_app()
        order_info = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tracking_code": tracking_code,
            "total_price": self.ids.total_price_label.text
        }
        save_order_to_history(order_info)
        # ----------------------------------

        from kivymd.uix.dialog import MDDialog
        self.success_dialog = MDDialog(
            title=get_farsi("سفارش با موفقیت ثبت شد"),
            text=get_farsi(f"ممنون از اعتماد شما\n\nشماره پیگیری: {tracking_code}"),
            buttons=[
                MDRaisedButton(
                    text=get_farsi("بازگشت به منو"),
                    font_name="Vazir",
                    on_release=self.final_reset
                )
            ]
        )
        self.success_dialog.open()

    def final_reset(self, *args):
        self.success_dialog.dismiss()
        app = MDApp.get_running_app()
        app.cart = {} # خالی کردن سبد
        self.manager.current = 'menu' # برگشت به منو

class HistoryScreen(Screen):
    def get_text(self, text): return get_farsi(text)
    def go_back(self): self.manager.current = 'welcome'

    def on_enter(self):
        self.ids.history_list.clear_widgets()
        if os.path.exists('history.json'):
            with open('history.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
                for order in reversed(history):
                    # ساخت کارت برای هر سفارش
                    card = MDCard(orientation='vertical', padding="10dp", 
                                  size_hint_y=None, height="120dp", elevation=1, radius=[15,])
                    
                    # جدا کردن متن ریال/تومان از عدد برای نمایش درست
                    price_text = order['total_price'].replace("جمع کل:", "").strip()
                    
                    # اضافه کردن ویجت‌ها با اصلاح چیدمان
                    card.add_widget(MDLabel(text=get_farsi(f"تاریخ: {order['date']}"), font_name="Vazir", bold=True))
                    card.add_widget(MDLabel(text=get_farsi(f"کد پیگیری: {order['tracking_code']}"), font_name="Vazir"))
                    
                   
                    card.add_widget(MDLabel(text=price_text, font_name="Vazir", theme_text_color="Error", bold=True))
                    
                    self.ids.history_list.add_widget(card)
        else:
            self.ids.history_list.add_widget(MDLabel(text=get_farsi("هنوز سفارشی ثبت نشده است"), font_name="Vazir", halign="center"))

class ReyhoonApp(MDApp):
    def build(self):
        self.cart = {} 
        LabelBase.register(name="Vazir", fn_regular="Vazir.ttf")
        self.theme_cls.font_styles.update({
            "H2": ["Vazir", 60, False, 0],
            "H5": ["Vazir", 24, False, 0],
            "H6": ["Vazir", 20, False, 0],
            "Button": ["Vazir", 14, True, 1.25],
            "Body1": ["Vazir", 16, False, 0],
            "Caption": ["Vazir", 12, False, 0],
        })
        self.theme_cls.primary_palette = "Red"
        return Builder.load_string(KV)
    
    def on_start(self):
        # این کد تمام تب‌ها را پیدا کرده و فونتشان را به وزیر تغییر می‌دهد
        try:
            # دسترسی به تب‌های موجود در منو
            menu_screen = self.root.get_screen('menu')
            tabs = menu_screen.ids.tabs
            for tab in tabs.get_tab_list():
                for child in tab.walk():
                    # اگر ویجت قابلیت تغییر فونت داشت، آن را روی وزیر تنظیم کن
                    if hasattr(child, 'font_name'):
                        child.font_name = "Vazir"
        except Exception as e:
            print(f"Error fixing tab fonts: {e}")

if __name__ == '__main__':
    ReyhoonApp().run()