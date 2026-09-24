"""Google Maps'ten işletme bilgisi çeken Selenium yardımcıları.

Seçiciler mümkün olduğunca dilden bağımsızdır (data-item-id, role, href),
böylece Google arayüz metinlerini değiştirse bile veri çekme çalışmaya devam eder.
"""

import html
import os
import re
import sys
import time
from urllib.parse import quote_plus, urljoin, urlparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait

ARAMA_URL = "https://www.google.com/maps/search/{}?hl=tr"
YER_SECICI = 'a[href*="/maps/place/"]'
SUTUNLAR = ["İşletme", "Kategori", "Puan", "Yorum Sayısı", "Adres", "Link", "Telefon", "Mail", "Google Maps"]

EPOSTA_DESENI = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
YOKSAYILAN_EPOSTA = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", "example.com", "sentry", "wixpress.com")
ILETISIM_KELIMELERI = ("iletisim", "iletişim", "contact", "bize-ulasin", "bize ulaşın")
LISTE_SONU_METINLERI = ("Listenin sonuna", "end of the list")


def dosya_yolu(goreli_yol):
    """Program klasöründeki (veya PyInstaller paketindeki) bir dosyanın yolunu bulur."""
    adaylar = [os.path.abspath(goreli_yol)]
    if getattr(sys, "frozen", False):
        adaylar.append(os.path.join(os.path.dirname(sys.executable), goreli_yol))
    if hasattr(sys, "_MEIPASS"):
        adaylar.append(os.path.join(sys._MEIPASS, goreli_yol))
    for aday in adaylar:
        if os.path.exists(aday):
            return aday
    return None


def tarayici_olustur(gorunmez=True):
    """Önce Firefox'u (program klasöründeki taşınabilir sürüm veya sistemdeki), olmazsa Chrome'u açar.

    Sürücü (geckodriver/chromedriver) bulunamazsa Selenium Manager otomatik indirir.
    """
    hatalar = []
    try:
        secenekler = FirefoxOptions()
        firefox = dosya_yolu(os.path.join("firefox", "firefox.exe"))
        if firefox:
            secenekler.binary_location = firefox
        if gorunmez:
            secenekler.add_argument("--headless")
        secenekler.add_argument("--width=1920")
        secenekler.add_argument("--height=1080")
        secenekler.set_preference("intl.accept_languages", "tr-TR, tr")
        surucu = dosya_yolu("geckodriver.exe")
        servis = FirefoxService(executable_path=surucu) if surucu else FirefoxService()
        return webdriver.Firefox(service=servis, options=secenekler)
    except WebDriverException as hata:
        hatalar.append("Firefox: {}".format(hata.msg or hata))

    try:
        secenekler = ChromeOptions()
        if gorunmez:
            secenekler.add_argument("--headless=new")
        secenekler.add_argument("--window-size=1920,1080")
        secenekler.add_argument("--lang=tr-TR")
        secenekler.add_experimental_option("prefs", {"intl.accept_languages": "tr-TR,tr"})
        return webdriver.Chrome(options=secenekler)
    except WebDriverException as hata:
        hatalar.append("Chrome: {}".format(hata.msg or hata))

    raise RuntimeError("Tarayıcı başlatılamadı. Firefox veya Chrome kurulu olmalı.\n" + "\n".join(hatalar))


# ---------------------------------------------------------------- arama sonuçları

def cerez_onayla(driver):
    """Google'ın çerez onay sayfası çıkarsa kabul eder."""
    if "consent." not in driver.current_url:
        return
    for buton in driver.find_elements(By.TAG_NAME, "button"):
        metin = (buton.text or buton.get_attribute("aria-label") or "").lower()
        if "kabul et" in metin or "accept all" in metin:
            buton.click()
            WebDriverWait(driver, 10).until(lambda d: "consent." not in d.current_url)
            return


def _benzersiz(liste):
    return list(dict.fromkeys(oge for oge in liste if oge))


def _liste_sonu_mu(driver):
    return any(driver.find_elements(By.XPATH, "//span[contains(., '{}')]".format(metin))
               for metin in LISTE_SONU_METINLERI)


def isletme_linkleri(driver, sorgu, calisiyor=lambda: True, log=print, en_fazla=0, bekleme=1.5):
    """Arama sonuç listesini sonuna kadar kaydırır ve işletme sayfası linklerini döndürür."""
    driver.get(ARAMA_URL.format(quote_plus(sorgu)))
    cerez_onayla(driver)

    try:
        WebDriverWait(driver, 20).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, 'div[role="feed"]') or "/maps/place/" in d.current_url)
    except TimeoutException:
        log("Sonuç listesi yüklenmedi. Arama teriminizi kontrol edin.")
        return []

    listeler = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"]')
    if not listeler:
        log("Tek sonuç bulundu, doğrudan işletme sayfası açıldı.")
        return [driver.current_url]
    liste = listeler[0]

    onceki, ayni_tur = -1, 0
    while calisiyor():
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", liste)
        time.sleep(bekleme)
        adet = len(liste.find_elements(By.CSS_SELECTOR, YER_SECICI))
        if adet != onceki:
            log("{} işletme yüklendi...".format(adet))
            onceki, ayni_tur = adet, 0
        else:
            ayni_tur += 1
        if _liste_sonu_mu(driver) or ayni_tur >= 5 or (en_fazla and adet >= en_fazla):
            break

    linkler = _benzersiz(a.get_attribute("href") for a in liste.find_elements(By.CSS_SELECTOR, YER_SECICI))
    return linkler[:en_fazla] if en_fazla else linkler


# ---------------------------------------------------------------- işletme sayfası

def _nitelik(kapsam, secici, nitelik):
    ogeler = kapsam.find_elements(By.CSS_SELECTOR, secici)
    return (ogeler[0].get_attribute(nitelik) or "").strip() if ogeler else ""


def _baslik(driver):
    for h1 in driver.find_elements(By.TAG_NAME, "h1"):
        metin = h1.text.strip()
        if metin and metin not in ("Sonuçlar", "Results"):
            return metin
    return ""


def _etiket_temizle(etiket):
    # "Adres: Atatürk Cd. No:1" -> "Atatürk Cd. No:1"
    return etiket.split(":", 1)[1].strip() if ":" in etiket else etiket.strip()


def isletme_bilgisi(driver, url, zaman_asimi=10):
    driver.get(url)
    WebDriverWait(driver, zaman_asimi).until(_baslik)
    ana = driver.find_elements(By.CSS_SELECTOR, 'div[role="main"]')
    kapsam = ana[0] if ana else driver

    puan = yorum = ""
    etiketler = driver.execute_script(
        "var k = arguments[0] || document;"
        "return Array.from(k.querySelectorAll(\"[role='img'][aria-label], span[aria-label]\"))"
        ".map(function (e) { return e.getAttribute('aria-label'); });", ana[0] if ana else None)
    for etiket in etiketler:
        etiket = etiket or ""
        if not puan:
            eslesme = re.match(r"^\s*(\d[.,]\d)\s", etiket)
            if eslesme:
                puan = eslesme.group(1).replace(".", ",")
                continue
        if not yorum:
            eslesme = re.match(r"^\s*([\d.,]+)\s+(yorum|review)", etiket, re.I)
            if eslesme:
                yorum = re.sub(r"[.,]", "", eslesme.group(1))
        if puan and yorum:
            break

    adres = _etiket_temizle(_nitelik(kapsam, 'button[data-item-id="address"]', "aria-label"))
    site = _nitelik(kapsam, 'a[data-item-id="authority"]', "href")
    telefon = _etiket_temizle(_nitelik(kapsam, 'button[data-item-id^="phone:tel:"]', "aria-label"))
    if not telefon:
        telefon = _nitelik(kapsam, 'button[data-item-id^="phone:tel:"]', "data-item-id").replace("phone:tel:", "")
    kategori = ""
    kategoriler = kapsam.find_elements(By.CSS_SELECTOR, 'button[jsaction*="category"]')
    if kategoriler:
        kategori = kategoriler[0].text.strip()

    return {
        "İşletme": _baslik(driver),
        "Kategori": kategori,
        "Puan": puan,
        "Yorum Sayısı": yorum,
        "Adres": adres,
        "Link": site,
        "Telefon": telefon,
        "Mail": "",
        "Google Maps": url,
    }


# ---------------------------------------------------------------- e-posta

def epostalari_ayikla(sayfa):
    bulunan = []
    for eposta in EPOSTA_DESENI.findall(html.unescape(sayfa)):
        eposta = eposta.lower().strip(".")
        if not any(parca in eposta for parca in YOKSAYILAN_EPOSTA):
            bulunan.append(eposta)
    return _benzersiz(bulunan)


def _sayfa_ac(driver, url):
    try:
        driver.get(url)
    except TimeoutException:
        pass  # Sayfa tam yüklenmese de o ana kadarki içerik kullanılabilir
    return driver.page_source


def eposta_bul(driver, site, zaman_asimi=15):
    """İşletmenin web sitesinde, gerekirse iletişim sayfasında e-posta arar."""
    driver.set_page_load_timeout(zaman_asimi)
    try:
        epostalar = epostalari_ayikla(_sayfa_ac(driver, site))
        if not epostalar:
            alan = urlparse(driver.current_url).netloc
            baglantilar = driver.execute_script(
                "return Array.from(document.links).map(function (a) { return [a.href, a.textContent]; });")
            for href, yazi in baglantilar:
                metin = "{} {}".format(href, yazi).lower()
                if any(kelime in metin for kelime in ILETISIM_KELIMELERI) and urlparse(href).netloc == alan:
                    epostalar = epostalari_ayikla(_sayfa_ac(driver, urljoin(site, href)))
                    break
        return ", ".join(epostalar[:3])
    except WebDriverException:
        return ""
    finally:
        driver.set_page_load_timeout(60)
