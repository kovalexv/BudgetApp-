from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import matplotlib.pyplot as plt
import io, os, json

# ========= VARIABLES =========
transactions = []
subscriptions = []
current_user = None
SAVE_DIR = "sauvegardes"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# ========= OUTILS =========
def draw_background(widget, color):
    with widget.canvas.before:
        Color(*color)
        widget.rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda w, v: setattr(widget.rect, 'size', w.size))
    widget.bind(pos=lambda w, v: setattr(widget.rect, 'pos', w.pos))

def make_title(text):
    return Label(text=text, font_size=50, size_hint=(1, 0.15), bold=True, color=(1,1,1,1))

def make_button(text, callback, color_bg=(0.2, 0.5, 0.8, 1)):
    return Button(
        text=text,
        size_hint=(1, 0.15),
        font_size=40,
        background_normal="",
        background_color=color_bg,
        color=(1,1,1,1),
        on_release=callback
    )

def make_label(text, color=(1,1,1,1), font_size=40):
    return Label(text=text, color=color, font_size=font_size, size_hint_y=None, height=60)

def save_data():
    global transactions, subscriptions, current_user
    if current_user:
        path = os.path.join(SAVE_DIR, f"{current_user}.json")
        data = {"transactions": transactions, "subscriptions": subscriptions}
        with open(path, "w") as f:
            json.dump(data, f)

def load_data(user):
    global transactions, subscriptions
    path = os.path.join(SAVE_DIR, f"{user}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            transactions = data.get("transactions", [])
            subscriptions = data.get("subscriptions", [])
    else:
        transactions = []
        subscriptions = []

# ========= SCREENS =========
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=40, spacing=30)
        draw_background(layout, (0.2, 0.2, 0.2, 1))

        layout.add_widget(make_title("Connexion"))

        self.username_input = TextInput(hint_text="Nom d'utilisateur", font_size=40, size_hint=(1, 0.2))
        layout.add_widget(self.username_input)

        layout.add_widget(make_button("Se connecter", self.login, (0.3,0.6,0.9,1)))

        # Bouton pour choisir un utilisateur existant
        layout.add_widget(make_button("Choisir un utilisateur existant", 
                                      lambda x: setattr(self.manager, 'current', 'user_list'),
                                      color_bg=(0.5,0.5,0.5,1)))

        self.add_widget(layout)

    def login(self, instance):
        global current_user
        user = self.username_input.text.strip()
        if user:
            current_user = user
            load_data(user)
            self.manager.current = "home"

class UserListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        draw_background(layout, (0.2, 0.2, 0.5, 1))

        layout.add_widget(make_title("Choisir un utilisateur"))

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        layout.add_widget(make_button("⬅ Retour", lambda x: setattr(self.manager, 'current', 'login')))
        self.add_widget(layout)

        self.bind(on_enter=lambda x: self.update_user_list())

    def update_user_list(self):
        self.grid.clear_widgets()
        if os.path.exists(SAVE_DIR):
            files = [f.replace(".json","") for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
            for user in files:
                btn = make_button(user, lambda x, u=user: self.select_user(u), color_bg=(0.3,0.6,0.9,1))
                self.grid.add_widget(btn)

    def select_user(self, user):
        global current_user
        current_user = user
        load_data(user)
        self.manager.current = "home"

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        draw_background(layout, (0.1, 0.4, 0.7, 1))

        layout.add_widget(make_title("Gestion de Budget"))

        layout.add_widget(make_button("➕ Ajouter une dépense", lambda x: setattr(self.manager, 'current', 'add_expense')))
        layout.add_widget(make_button("💰 Ajouter un revenu", lambda x: setattr(self.manager, 'current', 'add_income')))
        layout.add_widget(make_button("📋 Voir les transactions", lambda x: setattr(self.manager, 'current', 'transactions')))
        layout.add_widget(make_button("🏦 Gérer les prélèvements", lambda x: setattr(self.manager, 'current', 'subscriptions')))
        layout.add_widget(make_button("📊 Résumé", lambda x: setattr(self.manager, 'current', 'summary')))

        # Bouton changer d'utilisateur
        layout.add_widget(make_button("🔄 Changer d'utilisateur", lambda x: setattr(self.manager, 'current', 'login'), (0.6,0.6,0.6,1)))

        self.add_widget(layout)

# ===== Ajouter dépense =====
class AddExpenseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        draw_background(layout, (0.7, 0.2, 0.2, 1))
        layout.add_widget(make_title("Nouvelle dépense"))
        self.name_input = TextInput(hint_text="Nom de la dépense", font_size=40, size_hint=(1, 0.15))
        self.amount_input = TextInput(hint_text="Montant", input_filter="float", font_size=40, size_hint=(1, 0.15))
        layout.add_widget(self.name_input)
        layout.add_widget(self.amount_input)
        layout.add_widget(make_button("Enregistrer", self.save_expense))
        layout.add_widget(make_button("⬅ Retour", lambda x: setattr(self.manager, 'current', 'home')))
        self.add_widget(layout)

    def save_expense(self, instance):
        name = self.name_input.text.strip()
        amount = self.amount_input.text.strip()
        if name and amount:
            try:
                transactions.append({"name": name, "amount": -abs(float(amount))})
                save_data()
                self.name_input.text = ""
                self.amount_input.text = ""
                self.manager.current = "home"
            except ValueError:
                pass

# ===== Ajouter revenu =====
class AddIncomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        draw_background(layout, (0.2, 0.7, 0.2, 1))
        layout.add_widget(make_title("Nouveau revenu"))
        self.name_input = TextInput(hint_text="Nom du revenu", font_size=40, size_hint=(1, 0.15))
        self.amount_input = TextInput(hint_text="Montant", input_filter="float", font_size=40, size_hint=(1, 0.15))
        layout.add_widget(self.name_input)
        layout.add_widget(self.amount_input)
        layout.add_widget(make_button("Enregistrer", self.save_income))
        layout.add_widget(make_button("⬅ Retour", lambda x: setattr(self.manager, 'current', 'home')))
        self.add_widget(layout)

    def save_income(self, instance):
        name = self.name_input.text.strip()
        amount = self.amount_input.text.strip()
        if name and amount:
            try:
                transactions.append({"name": name, "amount": abs(float(amount))})
                save_data()
                self.name_input.text = ""
                self.amount_input.text = ""
                self.manager.current = "home"
            except ValueError:
                pass

# ===== Transactions =====
class TransactionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        draw_background(layout, (0.2, 0.2, 0.5, 1))
        layout.add_widget(make_title("Transactions"))
        self.scroll = ScrollView(size_hint=(1, 0.75))
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        layout.add_widget(make_button("⬅ Retour", lambda x: setattr(self.manager, 'current', 'home')))
        self.add_widget(layout)

    def on_enter(self):
        self.update_list()

    def update_list(self):
        self.grid.clear_widgets()
        for i, t in enumerate(transactions):
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=20)
            color = (1,0,0,1) if t["amount"] < 0 else (0,1,0,1)
            label = make_label(f"{t['name']} : {t['amount']} €", color=color)
            btn_del = Button(
                text="❌", size_hint_x=0.3,
                background_normal="",
                background_color=(0.8,0,0,1),
                color=(1,1,1,1),
                on_release=lambda x, idx=i: self.delete_transaction(idx)
            )
            box.add_widget(label)
            box.add_widget(btn_del)
            self.grid.add_widget(box)

    def delete_transaction(self, index):
        if 0 <= index < len(transactions):
            transactions.pop(index)
            save_data()
            self.update_list()

# ===== Prélèvements =====
class SubscriptionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)
        draw_background(layout, (0.5, 0.2, 0.5, 1))
        layout.add_widget(make_title("Prélèvements"))
        self.name_input = TextInput(hint_text="Nom", font_size=40, size_hint=(1, 0.15))
        self.amount_input = TextInput(hint_text="Montant", input_filter="float", font_size=40, size_hint=(1, 0.15))
        self.day_input = TextInput(hint_text="Jour du mois (1-31)", input_filter="int", font_size=40, size_hint=(1, 0.15))
        layout.add_widget(self.name_input)
        layout.add_widget(self.amount_input)
        layout.add_widget(self.day_input)
        layout.add_widget(make_button("Ajouter prélèvement", self.add_subscription))
        self.scroll = ScrollView(size_hint=(1, 0.55))
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        layout.add_widget(make_button("⬅ Retour", lambda x: setattr(self.manager, 'current', 'home')))
        self.add_widget(layout)

    def on_enter(self):
        self.update_list()

    def add_subscription(self, instance):
        name = self.name_input.text.strip()
        amount = self.amount_input.text.strip()
        day = self.day_input.text.strip()
        if name and amount and day:
            try:
                subscriptions.append({"name": name, "amount": float(amount), "day": int(day)})
                save_data()
                self.name_input.text = ""
                self.amount_input.text = ""
                self.day_input.text = ""
                self.update_list()
            except ValueError:
                pass

    def update_list(self):
        self.grid.clear_widgets()
        for i, s in enumerate(subscriptions):
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=10)
            label = make_label(f"{s['name']} : {s['amount']} € (le {s['day']})")
            btn_del = Button(
                text="X", size_hint_x=0.3,
                background_normal="",
                background_color=(0.8,0,0,1),
                color=(1,1,1,1),
                on_release=lambda x, idx=i: self.delete_subscription(idx)
            )
            box.add_widget(label)
            box.add_widget(btn_del)
            self.grid.add_widget(box)

    def delete_subscription(self, index):
        if 0 <= index < len(subscriptions):
            subscriptions.pop(index)
            save_data()
            self.update_list()

# ===== Résumé =====
class SummaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        draw_background(layout, (0.9, 0.6, 0.2, 1))
        layout.add_widget(make_title("Résumé"))
        self.summary_label = Label(text="", font_size=20, size_hint=(1, 0.25), color=(1,1,1,1), markup=True)
        layout.add_widget(self.summary_label)
        self.graph = Image(size_hint=(1, 0.5))
        layout.add_widget(self.graph)
        layout.add_widget(make_button("⬅ Retour", lambda x: setattr(self.manager, 'current', 'home')))
        self.add_widget(layout)
        self.bind(on_enter=lambda x: self.update_summary())

    def update_summary(self):
        total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
        total_expense = abs(sum(t["amount"] for t in transactions if t["amount"] < 0))
        total_subs = sum(s["amount"] for s in subscriptions)
        balance = total_income - (total_expense + total_subs)

        self.summary_label.text = (
            f"[size=40]Revenus : {total_income} €[/size]\n\n\n"
            f"[size=40]Dépenses : {total_expense} €[/size]\n\n\n"
            f"[size=40]Prélèvements : {total_subs} €[/size]\n\n\n\n"
            f"[size=60]Solde : {balance} €[/size]\n"
        )

        labels = ["Revenus", "Dépenses", "Prélèvements"]
        values = [total_income, total_expense, total_subs]

        plt.clf()
        plt.bar(labels, values, color=["green", "red", "purple"])
        plt.title("Répartition Budget")
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        self.graph.texture = CoreImage(buf, ext="png").texture
        buf.close()

# ===== APPLICATION =====
class BudgetApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(UserListScreen(name="user_list"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddExpenseScreen(name="add_expense"))
        sm.add_widget(AddIncomeScreen(name="add_income"))
        sm.add_widget(TransactionScreen(name="transactions"))
        sm.add_widget(SubscriptionScreen(name="subscriptions"))
        sm.add_widget(SummaryScreen(name="summary"))
        return sm

if __name__ == "__main__":
    BudgetApp().run()
