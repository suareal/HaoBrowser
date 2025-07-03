from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QStyleFactory

def apply_fusion_style(app):
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setFont(QApplication.font())

def get_palette(is_dark):
    palette = QPalette()
    if is_dark:
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(220, 220, 220))
        palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
    else:
        palette.setColor(QPalette.Window, QColor(246, 247, 250))
        palette.setColor(QPalette.WindowText, QColor(34, 34, 34))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(233, 233, 239))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(34, 34, 34))
        palette.setColor(QPalette.Text, QColor(34, 34, 34))
        palette.setColor(QPalette.Button, QColor(246, 247, 250))
        palette.setColor(QPalette.ButtonText, QColor(34, 34, 34))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(58, 140, 255))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    return palette