import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, QDateEdit
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from cryptography.fernet import Fernet
import os
import base64


def generate_key(password):
    key = base64.urlsafe_b64encode(password.ljust(32).encode("utf-8")[:32])
    return key


def encrypt_data(name, surname, expiry_date, password):
    key = generate_key(password)
    cipher = Fernet(key)
    data = f"{name}|{surname}|{expiry_date}"
    encrypted_data = cipher.encrypt(data.encode("utf-8"))
    return encrypted_data.decode("utf-8")


class LicenseKeyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kolay Kontak Lisans Anahtarı Oluşturucu")
        self.setWindowIcon(QIcon(self.resource_path("kolaykontak.ico")))
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        self.resize(screen_size.width() // 2, screen_size.height() // 2)
        self.password = "s8J$Bz7pLq#kT9Wx"
        self.initUI()
        self.apply_dark_theme()
    def resource_path(self,relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    def initUI(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.name_label = QLabel("İsim:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.surname_label = QLabel("Soyisim:")
        self.surname_input = QLineEdit()
        layout.addWidget(self.surname_label)
        layout.addWidget(self.surname_input)

        self.expiry_date_label = QLabel("Son Geçerlilik Tarihi:")
        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setDate(QDate.currentDate().addMonths(6))  # Varsayılan olarak 1 yıl sonrası
        layout.addWidget(self.expiry_date_label)
        layout.addWidget(self.expiry_date_input)

        self.license_key_label = QLabel("Lisans Anahtarı:")
        self.license_key_output = QTextEdit()
        self.license_key_output.setReadOnly(True)
        layout.addWidget(self.license_key_label)
        layout.addWidget(self.license_key_output)

        self.generate_button = QPushButton("Lisans Anahtarı Oluştur")
        self.generate_button.clicked.connect(self.generate_license_key)
        layout.addWidget(self.generate_button)

        self.setCentralWidget(central_widget)

    def generate_license_key(self):
        name = self.name_input.text().strip()
        surname = self.surname_input.text().strip()
        expiry_date = self.expiry_date_input.date().toString("yyyy-MM-dd")
        password = self.password

        if not name or not surname:
            self.license_key_output.setPlainText("İsim ve soyisim alanlarını doldurun!")
            return

        try:
            license_key = encrypt_data(name, surname, expiry_date, password)
            self.license_key_output.setPlainText(license_key)
        except Exception as e:
            self.license_key_output.setPlainText(f"Hata: {e}")

    def apply_dark_theme(self):
        dark_stylesheet = """
        QMainWindow {
            background-color: #1e1e2e;  /* Koyu arka plan */
            color: #dcd6f7;  /* Açık yazı */
        }
        QLabel {
            color: #c9b8ff;  /* Soluk mor yazı */
            font-size: 12pt;
        }
        QLineEdit, QDateEdit {
            background-color: #2c2c3d;  /* Koyu gri */
            color: #ffffff;
            border: 1px solid #5e4b7a;
            border-radius: 5px;
            padding: 5px;
        }
        QTextEdit {
            background-color: #2c2c3d;  /* Koyu gri */
            color: #ffffff;
            border: 1px solid #5e4b7a;
            border-radius: 5px;
            padding: 8px;
        }
        QPushButton {
            background-color: #3c2a4d;  /* Koyu mor buton */
            color: #ffffff;
            border: 1px solid #5e4b7a;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 11pt;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5e4b7a;  /* Hover için parlak mor */
        }
        QPushButton:pressed {
            background-color: #482d61;  /* Basıldığında koyu mor */
        }
        QCalendarWidget QAbstractItemView {
            background-color: #2c2c3d;  /* Takvim arka planı */
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_stylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicenseKeyApp()
    window.show()
    sys.exit(app.exec_())
