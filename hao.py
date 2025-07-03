import sys
import os
import json
import platform
import ctypes

from PyQt5.QtCore import QUrl, Qt, QTimer, QRect
from PyQt5.QtGui import (
    QIcon, QPalette, QColor, QDesktopServices, QGuiApplication,
    QFontMetrics, QPainter
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QTabWidget, QWidget,
    QVBoxLayout, QAction, QHBoxLayout, QSizePolicy, QStyleFactory, QStyle,
    QMenu, QToolButton, QMessageBox, QTabBar, QStyleOptionTab
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEnginePage, QWebEngineFullScreenRequest, QWebEngineSettings
)
from style import apply_fusion_style, get_palette

# --- DPI/Scaling Awareness ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

app = QApplication(sys.argv)
primary_screen = QGuiApplication.primaryScreen()
system_dpi = primary_screen.logicalDotsPerInch() if primary_screen else 96
system_scaling = system_dpi / 96.0 if system_dpi else 1.0

apply_fusion_style(app)

# --- Theme Detection ---
def apply_theme():
    global is_dark
    if default_theme == "System":
        is_dark = detect_windows_dark()
    elif default_theme == "Dark":
        is_dark = True
    else:
        is_dark = False
    app.setPalette(get_palette(is_dark))

# --- Constants and Globals ---
SEARCH_ENGINES = {
    "Bing": "https://www.bing.com/search?q={}",
    "Google": "https://www.google.com/search?q={}",
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
}
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".hao_browser_settings.json")
DEFAULTS = {
    "search_engine": "Bing",
    "homepage": "https://www.msn.com",
    "newtab": "https://www.msn.com",
    "theme": "System",
    "region": "US",
    "activation_key": "",
    "history": [],
    "browser_zoom": 100,
}
activation_key = ""
history = []
browser_zoom = DEFAULTS["browser_zoom"]

# --- Settings Persistence ---
def load_settings():
    global default_search_engine, default_homepage, default_newtab, default_theme, default_region, activation_key, history
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            default_search_engine = data.get("default_search_engine", DEFAULTS["search_engine"])
            default_homepage = data.get("default_homepage", DEFAULTS["homepage"])
            default_newtab = data.get("default_newtab", DEFAULTS["newtab"])
            default_theme = data.get("default_theme", DEFAULTS["theme"])
            default_region = data.get("default_region", DEFAULTS["region"])
            activation_key = data.get("activation_key", DEFAULTS["activation_key"])
            history = data.get("history", [])
            browser_zoom = data.get("browser_zoom", DEFAULTS["browser_zoom"])
    except Exception:
        default_search_engine = DEFAULTS["search_engine"]
        default_homepage = DEFAULTS["homepage"]
        default_newtab = DEFAULTS["newtab"]
        default_theme = DEFAULTS["theme"]
        default_region = DEFAULTS["region"]
        activation_key = DEFAULTS["activation_key"]
        history = []
        browser_zoom = DEFAULTS["browser_zoom"]

def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "default_search_engine": default_search_engine,
                "default_homepage": default_homepage,
                "default_newtab": default_newtab,
                "default_theme": default_theme,
                "default_region": default_region,
                "activation_key": activation_key,
                "history": history[-200:],
                "browser_zoom": browser_zoom,
            }, f)
    except Exception:
        pass

# --- Theme Detection ---
def detect_windows_dark():
    if platform.system() == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            pass
    return False

# --- Main Window ---
class HaoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._user_fullscreen = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
                self._user_fullscreen = False
            else:
                self.showFullScreen()
                self._user_fullscreen = True
        else:
            super().keyPressEvent(event)

window = HaoMainWindow()
window.setWindowTitle("Hao Browser 1.0 Beta 1 | The best in the universe")
window.setWindowIcon(QIcon("resources/app.png"))

def update_window_title():
    if activation_key != "ILLUM-INATI6-666":
        window.setWindowTitle("UNACTIVATED LICENSE | Hao Browser 1.0 Beta 1 | The best in the universe")
    else:
        window.setWindowTitle("Hao Browser 1.0 Beta 1 | The best in the universe")

# --- Toolbar and Address Bar ---
def get_icon(name, fallback):
    icon = QIcon.fromTheme(name)
    if icon.isNull():
        icon = window.style().standardIcon(fallback)
    return icon

toolbar = QToolBar()
toolbar.setMovable(False)
bar_container = QWidget()
bar_layout = QHBoxLayout()
bar_layout.setContentsMargins(0, 0, 0, 0)
bar_layout.setSpacing(8)
url_bar = QLineEdit()
url_bar.setPlaceholderText("Search or enter address and press Enter…")
url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
bar_layout.addWidget(url_bar)
bar_container.setLayout(bar_layout)
toolbar.addWidget(bar_container)

back_action = QAction(get_icon("go-previous", QStyle.SP_ArrowBack), "", window)
forward_action = QAction(get_icon("go-next", QStyle.SP_ArrowForward), "", window)
refresh_action = QAction(get_icon("view-refresh", QStyle.SP_BrowserReload), "", window)
home_action = QAction(QIcon("resources/home.png"), "Home", window)
new_tab_action = QAction(get_icon("tab-new", QStyle.SP_FileDialogNewFolder), "New Tab", window)
toolbar.addAction(back_action)
toolbar.addAction(forward_action)
toolbar.addAction(refresh_action)
toolbar.addAction(home_action)
toolbar.addAction(new_tab_action)

menu_button = QToolButton()
menu_button.setText("…")
menu_button.setPopupMode(QToolButton.InstantPopup)
menu = QMenu()
settings_action = QAction("Settings", window)
history_action = QAction("History", window)
about_action = QAction("About", window)
zoom_menu = QMenu("Website Zoom", window)
zoom_levels = [50, 75, 100, 125, 150, 200]
zoom_actions = []
def set_zoom(level):
    browser = tabs.currentWidget()
    if isinstance(browser, QWebEngineView):
        browser.setZoomFactor(level / 100.0)
        for act, zl in zip(zoom_actions, zoom_levels):
            act.setChecked(zl == level)
for zl in zoom_levels:
    act = QAction(f"{zl}%", window, checkable=True)
    act.triggered.connect(lambda checked, zl=zl: set_zoom(zl))
    zoom_menu.addAction(act)
    zoom_actions.append(act)
zoom_actions[2].setChecked(True)
menu.addMenu(zoom_menu)
menu.addAction(settings_action)
menu.addAction(history_action)
menu.addAction(about_action)
menu_button.setMenu(menu)
toolbar.addWidget(menu_button)

copilot_action = QAction(QIcon(), "Copilot", window)
copilot_action.setToolTip("Ask Greg (AI Assistant)")
copilot_action.setIconText("AI")
toolbar.insertAction(menu_button.defaultAction() if hasattr(menu_button, 'defaultAction') else None, copilot_action)

# --- Tab Widget and MarqueeTabBar ---
class MarqueeTabBar(QTabBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offsets = dict()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_offsets)
        self.timer.start(30)
        self.setMouseTracking(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.handle_tab_close)

    def handle_tab_close(self, index):
        parent = self.parent()
        if hasattr(parent, 'tabCloseRequested'):
            parent.tabCloseRequested.emit(index)

    def update_offsets(self):
        for i in range(self.count()):
            rect = self.tabRect(i)
            text = self.tabText(i)
            metrics = QFontMetrics(self.font())
            text_width = metrics.width(text)
            available = rect.width() - 24
            if text_width > available:
                self.offsets.setdefault(i, 0)
                self.offsets[i] += 1.5
                if self.offsets[i] > text_width + 32:
                    self.offsets[i] = 0
            else:
                self.offsets[i] = 0
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        for i in range(self.count()):
            rect = self.tabRect(i)
            text = self.tabText(i)
            metrics = QFontMetrics(self.font())
            text_width = metrics.width(text)
            available = rect.width() - 24
            if text_width > available:
                offset = self.offsets.get(i, 0)
                painter.save()
                painter.setClipRect(rect)
                painter.setPen(self.tabTextColor(i))
                x1 = rect.left() + 12 - offset
                x2 = x1 + text_width + 32
                y = rect.top()
                h = rect.height()
                painter.drawText(x1, y, text_width, h, int(Qt.AlignVCenter), text)
                painter.drawText(x2, y, text_width, h, int(Qt.AlignVCenter), text)
                painter.restore()
        for i in range(self.count()):
            opt = QStyleOptionTab()
            self.initStyleOption(opt, i)
            close_rect = self.tabButton(i, QTabBar.RightSide)
            if close_rect is None:
                tab_rect = self.tabRect(i)
                btn_size = 18
                btn_x = tab_rect.right() - btn_size - 6
                btn_y = tab_rect.center().y() - btn_size // 2
                btn_rect = QRect(btn_x, btn_y, btn_size, btn_size)
                painter.save()
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(90, 178, 255, 180) if self.tabAt(self.mapFromGlobal(Qt.QCursor.pos())) == i else QColor(120,120,120,80))
                painter.drawEllipse(btn_rect)
                painter.setPen(QColor('#fff'))
                painter.setFont(self.font())
                painter.drawText(btn_rect, Qt.AlignCenter, '✕')
                painter.restore()

    def mousePressEvent(self, event):
        for i in range(self.count()):
            tab_rect = self.tabRect(i)
            btn_size = 18
            btn_x = tab_rect.right() - btn_size - 6
            btn_y = tab_rect.center().y() - btn_size // 2
            btn_rect = QRect(btn_x, btn_y, btn_size, btn_size)
            if btn_rect.contains(event.pos()):
                self.handle_tab_close(i)
                return
        super().mousePressEvent(event)

tabs = QTabWidget()
tabs.setTabsClosable(True)
tabs.setTabPosition(QTabWidget.South)
tabs.setTabBar(MarqueeTabBar())

central_widget = QWidget()
central_layout = QVBoxLayout()
central_layout.setContentsMargins(0, 0, 0, 0)
central_layout.setSpacing(0)
central_layout.addWidget(tabs)
central_layout.addWidget(toolbar)
central_widget.setLayout(central_layout)
window.setCentralWidget(central_widget)

# --- Custom WebEnginePage ---
class CustomWebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        new_browser = add_new_tab()
        return new_browser.page()

# --- Fullscreen Video Support ---
fullscreen_browser = None
fullscreen_index = None
fullscreen_old_geometry = None
fullscreen_old_parent = None

def handle_fullscreen_request(request):
    global fullscreen_browser, fullscreen_index, fullscreen_old_geometry, fullscreen_old_parent
    request.accept()
    browser = request.originatingPage().view()
    if request.toggleOn():
        fullscreen_index = tabs.indexOf(browser)
        fullscreen_browser = browser
        fullscreen_old_geometry = browser.geometry()
        fullscreen_old_parent = browser.parentWidget()
        tabs.removeTab(fullscreen_index)
        browser.setParent(window)
        browser.show()
        window.setCentralWidget(browser)
        toolbar.hide()
        tabs.hide()
        window.showFullScreen()
    else:
        browser.setParent(fullscreen_old_parent)
        browser.showNormal()
        window.showNormal()
        window.setCentralWidget(central_widget)
        if fullscreen_index is not None:
            tabs.insertTab(fullscreen_index, browser, browser.windowTitle())
            tabs.setCurrentIndex(fullscreen_index)
        toolbar.show()
        tabs.show()
        fullscreen_browser = None
        fullscreen_index = None
        fullscreen_old_geometry = None
        fullscreen_old_parent = None

# --- Tab Management ---
def add_new_tab(url=None):
    if activation_key != "ILLUM-INATI6-666" and tabs.count() >= 2:
        QMessageBox.warning(window, "The Product is Unactivated", "Hao Browser 1.0 Beta is Unactivated\n\nPlease activate the browser with genuine hao key to open more than 2 tabs.")
        return None
    browser = QWebEngineView()
    browser.setPage(CustomWebEnginePage(browser))
    profile = browser.page().profile()
    user_agent = profile.httpUserAgent()
    system = platform.system()
    if system == "Windows":
        pass
    elif system == "Darwin":
        user_agent = user_agent.replace("Windows NT 10.0", "Macintosh; Intel Mac OS X 10_15_7")
    elif system == "Linux":
        user_agent = user_agent.replace("Windows NT 10.0", "X11; Linux x86_64")
    elif system == "HaoOS":
        user_agent = user_agent.replace("Windows NT 10.0", "HaoOS; AMD Hao 1_0_0")
    profile.setHttpUserAgent(user_agent)
    browser.setZoomFactor(browser_zoom / 100.0)  # <-- Use selected text size
    browser.page().fullScreenRequested.connect(handle_fullscreen_request)
    browser.setUrl(QUrl(url if url else default_newtab))
    i = tabs.addTab(browser, "New Tab")
    tabs.setCurrentIndex(i)
    browser.urlChanged.connect(lambda q, browser=browser: update_urlbar(q, browser))
    browser.loadFinished.connect(lambda _, browser=browser: update_tab_title(browser))
    browser.iconChanged.connect(lambda icon, browser=browser: update_tab_icon(browser, icon))
    return browser

def update_urlbar(q, browser):
    if tabs.currentWidget() == browser:
        url_str = q.toString()
        url_bar.setText(url_str)
        if url_str and (not history or history[-1] != url_str):
            history.append(url_str)
            save_settings()

def update_tab_title(browser):
    i = tabs.indexOf(browser)
    if i != -1:
        tabs.setTabText(i, browser.page().title())

def update_tab_icon(browser, icon):
    i = tabs.indexOf(browser)
    if i != -1:
        tabs.setTabIcon(i, icon)

# --- UI Dialogs ---
def show_about():
    status = ("Activated" if activation_key == "ILLUM-INATI6-666" else "Unactivated")
    QMessageBox.about(window, "About Hao Browser", f"Hao Browser\nThe best browser in the universe that no one knows.\n\nCreated by Hao, Made in Glorious Kingdom of Thailand. \n\nActivation Status: {status}\n\n© 2025 Hao Team (World Conquer Team) • Crafted with AI")

def show_copilot_dialog():
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
    dialog = QDialog(window)
    dialog.setWindowTitle("Greg (AI Assistant)")
    dialog.resize(400, 220)
    layout = QVBoxLayout()
    label = QLabel("Greg is coming soon!\n\nThis is a placeholder for the AI assistant, Greg!\nMade by glorious Hao team in the great nation of Thailand.\n\nIn the future, you will be able to ask questions and get help here.")
    label.setWordWrap(True)
    layout.addWidget(label)
    ok_btn = QPushButton("OK")
    ok_btn.clicked.connect(dialog.accept)
    layout.addWidget(ok_btn)
    dialog.setLayout(layout)
    dialog.exec_()

def show_history():
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel
    dialog = QDialog(window)
    dialog.setWindowTitle("History")
    layout = QVBoxLayout()
    label = QLabel("Browsing History:")
    layout.addWidget(label)
    list_widget = QListWidget()
    for url in reversed(history):
        list_widget.addItem(url)
    layout.addWidget(list_widget)
    open_btn = QPushButton("Open")
    layout.addWidget(open_btn)
    def open_selected():
        selected = list_widget.currentItem()
        if selected:
            url_bar.setText(selected.text())
            handle_url_or_search()
            dialog.accept()
    open_btn.clicked.connect(open_selected)
    dialog.setLayout(layout)
    dialog.exec_()

def apply_text_size_to_all_tabs():
    for i in range(tabs.count()):
        widget = tabs.widget(i)
        if isinstance(widget, QWebEngineView):
            widget.setZoomFactor(browser_zoom / 100.0)

def show_settings():
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit
    dialog = QDialog(window)
    dialog.setWindowTitle("Settings")
    dialog.resize(480, 380)
    layout = QVBoxLayout()
    label = QLabel("Default Search Engine:")
    combo = QComboBox()
    combo.addItems(SEARCH_ENGINES.keys())
    combo.setCurrentText(default_search_engine)
    layout.addWidget(label)
    layout.addWidget(combo)
    homepage_label = QLabel("Default Homepage:")
    homepage_edit = QLineEdit(default_homepage)
    layout.addWidget(homepage_label)
    layout.addWidget(homepage_edit)
    newtab_label = QLabel("Default New Tab Website:")
    newtab_edit = QLineEdit(default_newtab)
    layout.addWidget(newtab_label)
    layout.addWidget(newtab_edit)
    theme_label = QLabel("Theme:")
    theme_combo = QComboBox()
    theme_combo.addItems(["System", "Light", "Dark"])
    theme_combo.setCurrentText(default_theme)
    layout.addWidget(theme_label)
    layout.addWidget(theme_combo)
    region_label = QLabel("Region (for website detection):")
    region_combo = QComboBox()
    region_list = [
        ("United States", "US"),
        ("United Kingdom", "GB"),
        ("Germany", "DE"),
        ("France", "FR"),
        ("Japan", "JP"),
        ("Occupied Area of the Republic of China", "CN"),
        ("Republic of China", "TW"),
        ("Kingdom of Thailand", "TH"),
        ("Vietnam", "VN"),
        ("Indonesia", "ID"),
        ("Singapore", "SG"),
        ("Malaysia", "MY"),
        ("Philippines", "PH"),
        ("Australia", "AU"),
        ("Canada", "CA"),
        ("Brazil", "BR"),
        ("Ukrainian Russia", "RU"),
        ("Ukraine", "UA"),
        ("Yugoslavia", "YU"),
        ("South Korea", "KR"),
        ("Joint Occupied Territory of Cambodia (Thailand, Vietnam, and Laos)", "KH"),
        ("Palestine", "PS"),
        ("Iran", "IR"),
        ("Iraq", "IQ"),
        ("Syrian Arab Republic", "SY"),
        ("Other", "")
    ]
    for name, code in region_list:
        region_combo.addItem(name, code)
    try:
        idx = [code for _, code in region_list].index(default_region)
        region_combo.setCurrentIndex(idx)
    except Exception:
        region_combo.setCurrentIndex(0)
    layout.addWidget(region_label)
    layout.addWidget(region_combo)
    activation_label = QLabel("Activation Key:")
    layout.addWidget(activation_label)
    activation_desc = QLabel()
    buy_key_btn = None
    if activation_key != "ILLUM-INATI6-666":
        buy_key_btn = QPushButton("Buy Key")
        def open_buy_key():
            QDesktopServices.openUrl(QUrl("https://karnhao.github.io/my-portfolio"))
        buy_key_btn.clicked.connect(open_buy_key)
    def show_change_key():
        nonlocal change_key_btn
        if change_key_btn is not None:
            layout.removeWidget(change_key_btn)
            change_key_btn.deleteLater()
            change_key_btn = None
        layout.insertWidget(layout.indexOf(activation_desc), activation_edit)
        activation_edit.setText(activation_key)
        activation_edit.show()
        dialog.adjustSize()
    def do_activate():
        nonlocal activation_edit, activation_desc, activate_btn
        key = activation_edit.text().strip()
        if key == "ILLUM-INATI6-666":
            activation_desc.setText("The product is activate using Hao genuine key.")
            activation_edit.hide()
            activate_btn.hide()
            global activation_key
            activation_key = key
            save_settings()
            update_window_title()
            change_key_btn = QPushButton("Change Key")
            layout.insertWidget(layout.indexOf(activation_desc), change_key_btn)
            change_key_btn.clicked.connect(show_change_key)
            if buy_key_btn is not None:
                try:
                    layout.removeWidget(buy_key_btn)
                    buy_key_btn.deleteLater()
                except Exception:
                    pass
        else:
            activation_desc.setText("Invalid activation key.")
    if activation_key == "ILLUM-INATI6-666":
        activation_desc.setText("The product is activate using Hao genuine key.")
        change_key_btn = QPushButton("Change Key")
        layout.addWidget(change_key_btn)
        activation_edit = QLineEdit(activation_key)
        activation_edit.setPlaceholderText("Enter activation key...")
        activation_edit.hide()
        change_key_btn.clicked.connect(show_change_key)
    else:
        change_key_btn = None
        activation_edit = QLineEdit(activation_key)
        activation_edit.setPlaceholderText("Enter activation key...")
        layout.addWidget(activation_edit)
        activate_btn = QPushButton("Activate")
        layout.addWidget(activate_btn)
        activate_btn.clicked.connect(do_activate)
        if buy_key_btn is not None:
            layout.addWidget(buy_key_btn)
        activation_desc.setText("")
    layout.addWidget(activation_desc)

    # --- Add Zoom Option ---
    text_size_label = QLabel("Default Zoom:")
    text_size_combo = QComboBox()
    text_size_options = [75, 90, 100, 110, 125, 150, 175, 200]
    for size in text_size_options:
        text_size_combo.addItem(f"{size}%", size)
    try:
        idx = text_size_options.index(browser_zoom)
        text_size_combo.setCurrentIndex(idx)
    except Exception:
        text_size_combo.setCurrentIndex(2)  # Default to 100%
    layout.addWidget(text_size_label)
    layout.addWidget(text_size_combo)

    ok_btn = QPushButton("OK")
    layout.addWidget(ok_btn)
    dialog.setLayout(layout)
    def save_and_close():
        global default_search_engine, default_homepage, default_newtab, default_theme, default_region, activation_key, browser_zoom
        default_search_engine = combo.currentText()
        default_homepage = homepage_edit.text().strip() or DEFAULTS["homepage"]
        default_newtab = newtab_edit.text().strip() or DEFAULTS["newtab"]
        default_theme = theme_combo.currentText()
        default_region = region_combo.currentData() or "TH"
        browser_zoom = text_size_combo.currentData()  # <-- Save text size
        if activation_edit.isVisible():
            activation_key = activation_edit.text().strip()
        save_settings()
        apply_theme()
        apply_text_size_to_all_tabs()  # <-- Apply to all open tabs
        try:
            update_window_title()
        except Exception:
            pass
        dialog.accept()
    ok_btn.clicked.connect(save_and_close)
    dialog.exec_()

# --- Signal Connections ---
settings_action.triggered.connect(show_settings)
history_action.triggered.connect(show_history)
about_action.triggered.connect(show_about)
copilot_action.triggered.connect(show_copilot_dialog)

def handle_url_or_search():
    text = url_bar.text().strip()
    if text:
        if text.startswith("http://") or text.startswith("https://") or "." in text or text.startswith("localhost"):
            if not text.startswith("http"):
                text = "http://" + text
            current_browser = tabs.currentWidget()
            if isinstance(current_browser, QWebEngineView):
                current_browser.setUrl(QUrl(text))
        else:
            search_url = SEARCH_ENGINES[default_search_engine].format(text.replace(' ', '+'))
            current_browser = tabs.currentWidget()
            if isinstance(current_browser, QWebEngineView):
                current_browser.setUrl(QUrl(search_url))

url_bar.returnPressed.connect(handle_url_or_search)

def on_tab_changed(i):
    try:
        browser = tabs.widget(i)
        if isinstance(browser, QWebEngineView):
            url_bar.setText(browser.url().toString())
        else:
            url_bar.setText("")
    except Exception:
        url_bar.setText("")

def on_tab_close(i):
    try:
        if tabs.count() > 1:
            tabs.removeTab(i)
        else:
            browser = tabs.widget(0)
            if isinstance(browser, QWebEngineView):
                browser.setUrl(QUrl(default_newtab))
                tabs.setTabText(0, "New Tab")
                tabs.setTabIcon(0, QIcon())
    except Exception:
        pass

tabs.currentChanged.connect(on_tab_changed)
tabs.tabCloseRequested.connect(on_tab_close)
new_tab_action.triggered.connect(lambda: add_new_tab())
home_action.triggered.connect(lambda: tabs.currentWidget().setUrl(QUrl(default_homepage)) if isinstance(tabs.currentWidget(), QWebEngineView) else None)
back_action.triggered.connect(lambda: tabs.currentWidget().back() if isinstance(tabs.currentWidget(), QWebEngineView) else None)
forward_action.triggered.connect(lambda: tabs.currentWidget().forward() if isinstance(tabs.currentWidget(), QWebEngineView) else None)
refresh_action.triggered.connect(lambda: tabs.currentWidget().reload() if isinstance(tabs.currentWidget(), QWebEngineView) else None)

# --- Startup ---
first_launch = not os.path.exists(SETTINGS_FILE)
load_settings()
apply_theme()
update_window_title()
add_new_tab()
apply_text_size_to_all_tabs()  # <-- Add this line
window.resize(1280, 800)
window.show()
if first_launch:
    QMessageBox.information(window, "Welcome to Hao Browser!", "Welcome to Hao Browser 1.0 Beta!\n\nThank you for trying the best browser in the universe.\n\nYou can customize your settings, theme, and more from the menu (⋯).\n\nDon't forget to activate the browser for full experience.\n\nEnjoy browsing!")
print(f"[HaoBrowser] System DPI: {system_dpi}, Scaling factor: {system_scaling}")
sys.exit(app.exec_())