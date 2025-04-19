from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, \
    QTextEdit, QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout,QStackedWidget, QProgressBar,QInputDialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from cryptography.fernet import Fernet
from datetime import datetime
import base64
import pandas as pd
import time
import os
import sys



class SeleniumThread(QThread):

    log_signal = pyqtSignal(str)
    liste_signal = pyqtSignal(list)
    progress_signal = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, search_query):
        super().__init__()
        self.search_query = search_query
        self._is_running = True

    def resource_path(self,relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def run(self):
        firefox_binary_path = "firefox/firefox.exe"
        gecko_driver_path = "geckodriver.exe"

        firefox_options = Options()
        firefox_options.binary_location = firefox_binary_path
        firefox_options.add_argument("--headless")

        service = Service(executable_path=gecko_driver_path,log_path=None)
        driver = webdriver.Firefox(service=service, options=firefox_options)
        if not self._is_running:
            return
        try:

            sayac = 0
            driver.get("https://www.google.com/maps/")
            self.log_signal.emit("Google Maps açıldı.")

            arama_metni = self.search_query
            if not arama_metni:
                self.log_signal.emit("Lütfen bir arama terimi girin.")
                return

            self.log_signal.emit(f"Arama yapılıyor: {arama_metni}")

            arama_kutusu = driver.find_element(By.ID, "searchboxinput")
            arama_kutusu.send_keys(arama_metni)

            ara_butonu = driver.find_element(By.ID, "searchbox-searchbutton")
            ara_butonu.click()

            time.sleep(5)

            sonuc_basligi = driver.find_element(By.XPATH, "//h1[contains(text(), 'Sonuçlar')]")
            location = sonuc_basligi.location
            size = sonuc_basligi.size

            x = location['x'] + size['width'] / 2
            y = location['y'] + size['height'] / 2

            actions = ActionChains(driver)
            actions.move_by_offset(x, y).click().perform()

            actions.move_by_offset(-x, -y).perform()
            if not self._is_running:
                return

            while True:
                try:

                    driver.find_element(By.XPATH, "//span[contains(text(), 'Listenin sonuna ulaştınız.')]")

                    break
                except:

                    actions.send_keys(Keys.SPACE).perform()
                    time.sleep(0.5)

            a_etiketleri = driver.find_elements(By.TAG_NAME, "a")
            href_list = [a.get_attribute("href") for a in a_etiketleri if a.get_attribute("href")]
            total = sum(1 for href in href_list if href.startswith("https://www.google.com/maps/place/"))
            self.log_signal.emit(f"{total} adet işletme bulundu!")
            processed = 0

            for href in href_list:
                if not self._is_running:
                    break

                if href.startswith("https://www.google.com/maps/place/"):
                    isletme1 = ""
                    puan1 = ""
                    adres1 = ""
                    link1 = ""
                    telefon1 = ""
                    mail1 = ""
                    link_var = False
                    driver.get(href)
                    try:
                        h1_element = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.TAG_NAME, "h1"))
                        )
                        self.log_signal.emit(f"İşletme: {h1_element.text}")
                        isletme1 = str(h1_element.text)
                    except:
                        pass
                    try:
                        span_element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[role="img"]'))
                        )
                        puan = span_element.get_attribute("aria-label")
                        if puan and "yıldızlı" in puan:
                            puan = puan.split(" ")[0].strip()
                            if puan:
                                self.log_signal.emit(f"Puan: {puan}")
                                puan1 = str(puan)
                    except Exception:
                        pass
                    try:
                        adres_element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-item-id="address"]'))
                        )
                        adres = adres_element.get_attribute("aria-label")
                        if adres and "Adres:" in adres:
                            adres = adres.split("Adres:")[1].strip()
                        self.log_signal.emit(f"Adres: {adres}")
                        adres1 = str(adres)
                    except:
                        pass
                    try:
                        link_element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-tooltip="Web sitesini aç"]'))
                        )
                        href_value = link_element.get_attribute("href")
                        if href_value:
                            self.log_signal.emit(f"Link: {href_value}")
                            link1 = str(href_value)
                            link_var = True
                    except Exception:
                        pass
                    try:
                        button_element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'button[data-tooltip="Telefon numarasını kopyala"]'))
                        )
                        aria_label_content = button_element.get_attribute("aria-label")
                        if aria_label_content and "Telefon:" in aria_label_content:
                            tel = aria_label_content.split("Telefon:")[1].strip()
                            self.log_signal.emit(tel)
                            telefon1 = str(tel)
                    except Exception:
                        pass
                    if link_var:
                        try:
                            driver.get(link1)
                            mail_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
                            for mail in mail_elements:
                                if mail.text.strip():
                                    self.log_signal.emit(f"Mail: {mail.text}")
                                    mail1 = str(mail.text)
                        except:
                            pass
                    self.log_signal.emit("-" * 40)
                    liste = [isletme1, puan1, adres1, link1, telefon1,mail1]
                    self.liste_signal.emit(liste)
                    processed += 1
                    self.progress_signal.emit(int((processed / total) * 100))



        except Exception as e:
            self.log_signal.emit(f"Hata oluştu: {e}")

        finally:
            driver.quit()
            self.log_signal.emit("Tarayıcı kapatıldı.")
            self.finished.emit()

    def stop(self):
        self._is_running = False


class GoogleMapsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kimlik = False
        self.Ana_dogruluma()
        self.setWindowTitle("KolayKontak")
        self.setWindowIcon(QIcon(self.resource_path("kolaykontak.ico")))
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        self.resize(screen_size.width() // 2, screen_size.height() // 2)

        self.start_image = QLabel(self)
        self.start_image.setPixmap(QPixmap(self.resource_path("kolaykontak.jpeg")))
        self.start_image.setScaledContents(True)
        self.start_image.setGeometry(self.rect())
        QTimer.singleShot(1000, self.initU)
    def initU(self):
        self.start_image.hide()
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.VeriCek())
        self.stacked_widget.addWidget(self.MesajAt())
        self.stacked_widget.addWidget(self.lisansSayfasi())
        self.stacked_widget.setCurrentIndex(2)

        button_duzeni = QHBoxLayout()
        self.isletme_button = QPushButton("🌐İşletme Bul🌐")
        self.isletme_button.clicked.connect(lambda: self.switch_page(2))
        button_duzeni.addWidget(self.isletme_button)
        self.mesaj_button = QPushButton("📨Mesaj Gönder📨")
        self.mesaj_button.clicked.connect(lambda: self.switch_page(2))
        button_duzeni.addWidget(self.mesaj_button)
        self.tema_button = QPushButton("Aydınlık Tema")
        self.tema_button.clicked.connect(self.tema_secim)
        button_duzeni.addWidget(self.tema_button)
        self.lisans_button = QPushButton("Lisans Bilgileri")
        self.lisans_button.clicked.connect(lambda: self.switch_page(2))
        button_duzeni.addWidget(self.lisans_button)
        self.layout.addLayout(button_duzeni)
        self.layout.addWidget(self.stacked_widget)
        self.design_dark()
        self.setCentralWidget(self.central_widget)
        self.initUI()
        self.thread = None
        self.current_file_path = None
        self.is_saving = False
        self.message_tekli=False
        self.message = ""
        self.phone_number = ""
        self.phone_numbers_list = []
    def initUI(self):
        if self.kimlik:
            self.stacked_widget.setCurrentIndex(0)
            self.isletme_button.clicked.connect(lambda: self.switch_page(0))
            self.mesaj_button.clicked.connect(lambda: self.switch_page(1))
    def lisansSayfasi(self):
        page = QWidget()
        layout = QVBoxLayout()

        key_layout = QHBoxLayout()
        self.key_label = QLabel("Lisans Anahtarı:")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Lisans Anahtarını Giriniz...")
        self.key_button = QPushButton("Doğrula")
        self.key_button.clicked.connect(self.lisans_button)
        self.license_info = QLabel("")
        self.license_info.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.license_info.setAlignment(Qt.AlignCenter)
        self.license_info.setHidden(True)

        key_layout.addWidget(self.key_label)
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(self.key_button)
        layout.addWidget(self.license_info,alignment=Qt.AlignCenter)
        layout.addLayout(key_layout)
        page.setLayout(layout)
        self.dosya_dogrulama()
        return page
    def dosya_dogrulama(self):
        if self.kimlik:
            self.lisans_bilgisi()
        else:
            self.license_info.setText("Kayıtlı bir lisans bulunamadı. Lütfen bir lisans anahtarı girin.")
            self.license_info.setHidden(False)
    def Ana_dogruluma(self):
        key = self.load_license()
        if key:
            deger = self.validate_license(key)
            if deger:
                self.kimlik=True
    def lisans_button(self):
        license_key = self.key_input.text()
        deger = self.validate_license(license_key)
        if deger:
            self.lisans_bilgisi()
            self.save_license(license_key)
            self.key_input.clear()
            self.kimlik=True
            self.initUI()



    def validate_license(self,license_key):

        try:
            password = "s8J$Bz7pLq#kT9Wx"
            decrypted_data = self.decrypt_data(license_key, password)
            self.name, self.surname, self.expiry_date = decrypted_data.split("|")
            self.expiry_date = datetime.strptime(self.expiry_date, "%Y-%m-%d")
            current_date = datetime.now()

            self.remaining_days = (self.expiry_date - current_date).days
            if self.remaining_days > 0:
                return True
        except:
            pass
        return False

    def get_license_file_path(self):

        appdata_path = os.getenv("APPDATA")
        license_folder = os.path.join(appdata_path, "KolayKontak")
        os.makedirs(license_folder, exist_ok=True)
        return os.path.join(license_folder, "license.key")
    def save_license(self, license_key):
        with open(self.get_license_file_path(), "w") as file:
            file.write(license_key)

    def load_license(self):
        if os.path.exists(self.get_license_file_path()):
            with open(self.get_license_file_path(), "r") as file:
                return file.read().strip()
        return None
    def lisans_bilgisi(self):
        self.license_info.setText(
            f"Lisans Geçerli:\n"
            f"İsim: {self.name}\n"
            f"Soyisim: {self.surname}\n"
            f"Lisans Bitiş Tarihi: {self.expiry_date.strftime('%Y-%m-%d')}\n"
            f"Kalan Gün: {self.remaining_days}"
        )
        self.license_info.setHidden(False)
    def decrypt_data(self,encrypted_data, password):
        key = self.generate_key(password)
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data.encode("utf-8")).decode("utf-8")
        return decrypted_data
    def generate_key(self,password):
        key = base64.urlsafe_b64encode(password.ljust(32).encode("utf-8")[:32])
        return key
    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
    def VeriCek(self):
        page = QWidget()
        layout = QVBoxLayout()
        giris_düzen = QHBoxLayout()
        self.label = QLabel("Aramak istediğiniz yeri girin:")
        giris_düzen.addWidget(self.label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Örn. Ankara Mobilya, İstanbul Bağcılar Su, Hastaneler")
        giris_düzen.addWidget(self.search_input)

        self.start_button = QPushButton("Ara")
        self.start_button.clicked.connect(self.start_selenium_thread)
        self.start_button.setEnabled(True)
        giris_düzen.addWidget(self.start_button)
        self.stop_button = QPushButton("Durdur")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_thread)
        giris_düzen.addWidget(self.stop_button)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.save_button = QPushButton("Verileri Kaydet")
        self.save_button.clicked.connect(self.save_data)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["İşletme", "Puan", "Adres", "Link", "Telefon","Mail"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(giris_düzen)
        layout.addWidget(self.result_output)
        layout.addWidget(self.save_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.table)
        page.setLayout(layout)
        return page
    def MesajAt(self):
        page = QWidget()
        layout = QVBoxLayout()
        self.message_label = QLabel("İletilecek Mesaj:")
        layout.addWidget(self.message_label)
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Mesajınızı buraya yazın...")


        button_layout = QHBoxLayout()
        self.single_button = QPushButton("Tekli Gönderim")
        self.single_button.clicked.connect(self.handle_single_message)
        button_layout.addWidget(self.single_button)

        self.bulk_button = QPushButton("Çoklu Gönderim")
        self.bulk_button.clicked.connect(self.handle_bulk_message)
        button_layout.addWidget(self.bulk_button)
        self.status_label = QLabel("")
        self.message_send_button = QPushButton("Mesajı Gönder")
        self.message_send_button.clicked.connect(self.message_send)
        layout.addWidget(self.message_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.message_send_button)
        page.setLayout(layout)
        return page
    def handle_single_message(self):
        phone_number, ok = QInputDialog.getText(
            self, "Tekli Gönderim", "Numarayı girin (0555 veya 0850 şeklinde girin):"
        )
        if ok and phone_number:
            self.phone_number = phone_number
            self.message = self.message_input.toPlainText()
            self.status_label.setText(f"Tekli gönderim için numara alındı: {self.phone_number}")
            self.message_tekli=True
    def handle_bulk_message(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            try:

                df = pd.read_excel(file_path)

                if "Telefon" in df.columns:
                    df["Telefon"] = df["Telefon"].astype(str)
                    df["Telefon"] = df["Telefon"].str.replace(r"[()\s-]", "", regex=True)
                    df = df[df["Telefon"].str.startswith(("05", "08"))]

                    self.phone_numbers_list = df["Telefon"].tolist()
                    self.message = self.message_input.toPlainText()

                    self.status_label.setText(
                        f"Çoklu gönderim için {len(self.phone_numbers_list)} geçerli numara alındı."
                    )
                    self.message_tekli=False
                else:
                    self.status_label.setText("Excel dosyasında 'Telefon' sütunu bulunamadı.")
            except Exception as e:
                self.status_label.setText(f"Hata: {str(e)}")
    def message_send(self):
        firefox_binary_path = "firefox/firefox.exe"
        gecko_driver_path = "geckodriver.exe"
        firefox_options = Options()
        firefox_options.binary_location = firefox_binary_path
        # firefox_options.add_argument("--headless")
        service = Service(executable_path=gecko_driver_path,log_path=None)
        driver = webdriver.Firefox(service=service, options=firefox_options)

        driver.get("https://web.whatsapp.com/")
        while True:
            try:
                a = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Yeni sohbet"]'))
                )
                break
            except:
                time.sleep(1)

        message = self.message
        if self.message_tekli:
            phone_number = self.phone_number
            whatsapp_link = f"https://web.whatsapp.com/send?phone=9{phone_number}&text={message.replace(' ', '%20')}"

            driver.get(whatsapp_link)
            time.sleep(1)
            while True:
                try:
                    gonder_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Gönder"]'))
                    )
                    gonder_button.click()

                    time.sleep(1)

                    driver.quit()
                    break
                except:
                    time.sleep(0.5)

        else:
            for phone_number in self.phone_numbers_list:

                whatsapp_link = f"https://web.whatsapp.com/send?phone=9{phone_number}&text={message.replace(' ', '%20')}"

                driver.get(whatsapp_link)
                time.sleep(1)
                while True:
                    try:
                        gonder_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Gönder"]'))
                        )
                        gonder_button.click()

                        time.sleep(1)

                        break
                    except:
                        time.sleep(0.5)

            driver.quit()
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    def log(self, message):
        self.result_output.append(message)
    def clear_all(self):
        self.result_output.clear()
        self.table.setRowCount(0)
        self.is_saving = False
        self.current_file_path = None
    def on_thread_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.is_saving and self.current_file_path:
            self.log(f"Tarama tamamlandı, {self.current_file_path} dosyası kapatıldı.")
            self.is_saving = False
            self.current_file_path = None
    def save_data(self):
        if self.is_saving:
            self.log(f"Zaten {self.current_file_path} dosyasına kayıt yapılıyor.")
            return
        if self.thread and self.thread.isRunning():
            file_path, _ = QFileDialog.getSaveFileName(self, "Verileri Kaydet", "", "Excel Files (*.xlsx)")
            if file_path:
                self.current_file_path = file_path
                self.is_saving = True
                self.log(f"Tarama devam ediyor, {file_path} dosyasına anlık veri kaydı başladı.")
                self.export_to_excel(file_path)
            return

        if not self.thread or not self.thread.isRunning():

            file_path, _ = QFileDialog.getSaveFileName(self, "Verileri Kaydet", "", "Excel Files (*.xlsx)")
            if file_path:
                self.log(f"Tarama tamamlandı, veriler {file_path} dosyasına kaydediliyor.")
                self.export_to_excel(file_path)
    def export_to_excel(self, file_path):
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        data = []

        for row in range(rows):
            row_data = []
            for column in range(columns):
                item = self.table.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        df = pd.DataFrame(data, columns=["İşletme", "Puan", "Adres", "Link", "Telefon","Mail"])
        df.to_excel(file_path, index=False)
        self.log(f"Veriler başarıyla {file_path} dosyasına kaydedildi.")
    def append_to_excel(self, file_path, rows):

        try:
            existing_df = pd.read_excel(file_path)
        except FileNotFoundError:

            existing_df = pd.DataFrame(columns=["İşletme", "Puan", "Adres", "Link", "Telefon","Mail"])

        new_df = pd.DataFrame(rows, columns=["İşletme", "Puan", "Adres", "Link", "Telefon","Mail"])
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        updated_df.to_excel(file_path, index=False)
    def design_dark(self):
        dark_mor_stylesheet = """
        QProgressBar {
            border: 2px solid #5e4b7a;
            border-radius: 5px;
            background-color: #2c2c3d;  /* Koyu gri-mor arka plan */
            text-align: center;  /* İlerleme yüzdesini ortalar */
            color: #dcd6f7;  /* Açık mor yazı rengi */
            font-size: 12px;
        }
        QProgressBar::chunk {
            background-color: #805ba7;  /* Parlak mor ilerleme rengi */
            border-radius: 5px;  /* İlerlemenin kenarları yuvarlatılmış */
        }
        QMainWindow {
            background-color: #1e1e2e;  /* Koyu arka plan rengi */
            color: #dcd6f7;  /* Açık mor yazı rengi */
        }

        QWidget {
            background-color: #1e1e2e;
            color: #dcd6f7;
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 12pt;
        }

        QLabel {
            color: #c9b8ff;  /* Soluk mor yazı rengi */
            font-size: 12pt;
        }

        QPushButton {
            background-color: #3c2a4d;  /* Koyu mor buton */
            color: #dcd6f7;  /* Açık yazı rengi */
            border: 1px solid #5e4b7a;
            border-radius: 8px;
            padding: 8px 16px;
        }

        QPushButton:hover {
            background-color: #5e4b7a;  /* Hover rengi (daha parlak mor) */
        }

        QPushButton:pressed {
            background-color: #482d61;  /* Basılınca rengi (daha koyu mor) */
        }

        QLineEdit {
            background-color: #2c2c3d;
            color: #dcd6f7;
            border: 1px solid #5e4b7a;
            border-radius: 5px;
            padding: 5px;
        }

        QTextEdit {
            background-color: #2c2c3d;
            color: #dcd6f7;
            border: 1px solid #5e4b7a;
            border-radius: 5px;
            padding: 8px;
        }

        QTableWidget {
            background-color: #2c2c3d;
            color: #dcd6f7;
            border: 1px solid #5e4b7a;
            gridline-color: #5e4b7a;
            selection-background-color: #482d61;
            selection-color: #ffffff;
        }

        QHeaderView::section {
            background-color: #3c2a4d;
            color: #dcd6f7;
            border: 1px solid #5e4b7a;
            padding: 5px;
        }

        QScrollBar:horizontal, QScrollBar:vertical {
            background: #2c2c3d;
            border: none;
            width: 8px;
            margin: 0;
        }

        QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
            background: #5e4b7a;
            border-radius: 4px;
        }

        QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {
            background: #805ba7;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
            border: none;
        }
        """
        self.setStyleSheet(dark_mor_stylesheet)
    def design_light(self):
        light_mor_stylesheet = """
        QProgressBar {
            border: 2px solid #8850c4;
            border-radius: 5px;
            background-color: #eceaff;  /* Daha belirgin açık arka plan */
            text-align: center;  /* Yüzdeyi ortala */
            color: #4b3066;  /* Daha koyu mor yazı */
            font-size: 12px;
        }
        QProgressBar::chunk {
            background-color: #8850c4;  /* Daha belirgin mor ilerleme rengi */
            border-radius: 5px;  /* İlerlemenin kenarları yuvarlatılmış */
        }
        QMainWindow {
            background-color: #ffffff;  /* Daha açık ve temiz görünüm */
            color: #3b2c53;  /* Belirgin koyu mor yazı */
        }

        QWidget {
            background-color: #ffffff;  /* Daha belirgin beyaz zemin */
            color: #3b2c53;
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 12pt;
        }

        QLabel {
            color: #4b3066;  /* Belirgin koyu yazı */
            font-size: 12pt;
        }

        QPushButton {
            background-color: #b59aff;  /* Daha belirgin açık mor buton */
            color: #ffffff;  /* Beyaz yazı */
            border: 1px solid #8850c4;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;  /* Yazıyı daha belirgin yapmak için */
        }

        QPushButton:hover {
            background-color: #a078df;  /* Daha koyu hover rengi */
        }

        QPushButton:pressed {
            background-color: #7d4bb3;  /* Daha koyu basılma rengi */
        }

        QLineEdit {
            background-color: #faf9ff;
            color: #3b2c53;
            border: 1px solid #8850c4;
            border-radius: 5px;
            padding: 5px;
        }

        QTextEdit {
            background-color: #faf9ff;
            color: #3b2c53;
            border: 1px solid #8850c4;
            border-radius: 5px;
            padding: 8px;
        }

        QTableWidget {
            background-color: #ffffff;
            color: #3b2c53;
            border: 1px solid #8850c4;
            gridline-color: #8850c4;
            selection-background-color: #b59aff;  /* Seçim için daha belirgin renk */
            selection-color: #ffffff;
        }

        QHeaderView::section {
            background-color: #d1b3f0;
            color: #3b2c53;
            border: 1px solid #8850c4;
            padding: 5px;
        }

        QScrollBar:horizontal, QScrollBar:vertical {
            background: #eceaff;  /* Daha açık kaydırma arka planı */
            border: none;
            width: 10px;
            margin: 0;
        }

        QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
            background: #b59aff;  /* Kaydırma çubuğu rengi */
            border-radius: 5px;
        }

        QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {
            background: #8850c4;  /* Daha koyu hover rengi */
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
            border: none;
        }
        """
        self.setStyleSheet(light_mor_stylesheet)
    def tema_secim(self):
        deger = self.tema_button.text()
        if deger=="Aydınlık Tema":
            self.tema_button.setText("Karanlık Tema")
            self.design_light()
        else:
            self.tema_button.setText("Aydınlık Tema")
            self.design_dark()
    def stop_thread(self):
        self.thread.stop()
        self.thread.wait()
        self.log("İşlem durduruldu!")
        self.on_thread_finished()
    def add_row(self, row_data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for column, data in enumerate(row_data):
            self.table.setItem(row, column, QTableWidgetItem(data))

        if self.is_saving and self.current_file_path:
            self.append_to_excel(self.current_file_path, [row_data])
    def start_selenium_thread(self):
        self.clear_all()
        search_query = self.search_input.text()
        if not search_query:
            self.log("Lütfen bir arama terimi girin.")
            return
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log("Tarayıcı başlatılıyor...")
        self.thread = SeleniumThread(search_query)
        self.thread.log_signal.connect(self.log)
        self.thread.liste_signal.connect(self.add_row)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.progress_signal.connect(self.update_progress_bar)
        self.thread.start()
    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoogleMapsApp()
    window.show()
    sys.exit(app.exec_())
