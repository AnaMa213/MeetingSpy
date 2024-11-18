import sys
print(sys.executable)

import os
print("Répertoire courant :", os.getcwd())

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QThread
print("PySide6 fonctionne correctement.")

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
)
from PySide6.QtCore import QThread, Signal