<div align="center">

# 📍 KolayKontak — Google Maps Veri Çekici

**Google Maps'te aradığınız işletmelerin adını, puanını, adresini, telefonunu, web sitesini ve e-postasını tek tıkla Excel'e aktarın.**

![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/arayüz-PyQt5-41CD52?logo=qt&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4-43B02A?logo=selenium&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

[Özellikler](#-özellikler) •
[Kurulum](#-kurulum) •
[Kullanım](#-kullanım) •
[Sorun giderme](#-sorun-giderme)

</div>

---

## ✨ Özellikler

- 🔎 **Tek aramayla tüm liste.** "Ankara Mobilya" gibi bir arama yazın. Program sonuç listesini sonuna kadar kaydırıp bütün işletmeleri toplar.
- 📋 **9 alan.** İşletme adı, kategori, puan, yorum sayısı, adres, web sitesi, telefon, e-posta ve Google Maps linki.
- 📧 **Akıllı e-posta bulma.** İşletmenin web sitesini tarar. Ana sayfada e-posta yoksa "İletişim" sayfasına da bakar. Görsel dosya adı gibi sahte eşleşmeleri eler.
- 🎯 **Sınır koyma.** En fazla kaç işletme çekileceğini belirleyebilirsiniz. E-posta aramasını kapatarak çekmeyi hızlandırabilirsiniz.
- 💾 **Excel'e kayıt.** Tarama bitince ya da sürerken kaydedebilirsiniz. Tarama sırasında kaydetmeyi başlatırsanız her yeni işletme dosyaya anında eklenir.
- ⏹️ **Anında durdurma.** Durdur düğmesi arayüzü dondurmaz ve o ana kadar toplanan veriler tabloda kalır.
- 🌗 **Karanlık ve aydınlık tema.**
- 🔐 **Lisans sistemi.** Süreli lisans anahtarıyla çalışır.

## 📥 Kurulum

### 1. Gerekenler

- Python 3.8 veya üzeri
- **Firefox** ya da **Google Chrome**. Program önce Firefox'u, bulamazsa Chrome'u kullanır.

### 2. Paketler

```bash
git clone https://github.com/battalkoc/Google-Maps-Veri-Cek.git
cd Google-Maps-Veri-Cek
pip install -r requirements.txt
```

Tarayıcı sürücüsünü (geckodriver/chromedriver) ayrıca indirmeniz gerekmez. Selenium ilk çalıştırmada uygun sürümü kendisi indirir.

### 3. Ek dosyalar

Program simgesi (`kolaykontak.ico`), açılış görseli (`kolaykontak.jpeg`) ve isteğe bağlı taşınabilir Firefox paketi Google Drive'dadır:
[Ek dosyaları indir](https://drive.google.com/file/d/1uO9QctoWsEK86f7PyVpTbf6zSJR0h0x_/view?usp=sharing)

<details>
<summary><b>Taşınabilir Firefox kullanmak (isteğe bağlı)</b></summary>

Bilgisayarda Firefox kurulu değilse, taşınabilir sürümü ve `geckodriver.exe` dosyasını program klasörüne koyun:

```text
Google-Maps-Veri-Cek/
├── firefox/firefox.exe
├── geckodriver.exe
└── kolaykontak.py
```

</details>

## 🚀 Kullanım

```bash
python kolaykontak.py
```

1. **Lisans Bilgileri** sayfasında lisans anahtarınızı girip **Doğrula** düğmesine basın. Anahtar bir kez girildikten sonra hatırlanır.
2. **İşletme Bul** sayfasında arama terimini yazın. Örnek: `İstanbul Bağcılar Su`, `Konya Diş Hekimi`.
3. İsterseniz **En fazla işletme** sınırını belirleyin ve **mail ara** seçeneğini açın ya da kapatın.
4. **Ara** düğmesine basın. Bulunan işletmeler tabloya canlı olarak eklenir.
5. **Verileri Kaydet** ile sonuçları `.xlsx` dosyasına aktarın.

### Excel çıktısı

| İşletme | Kategori | Puan | Yorum Sayısı | Adres | Link | Telefon | Mail | Google Maps |
|---|---|---|---|---|---|---|---|---|
| Mobilya Evi | Mobilya mağazası | 4,6 | 312 | Atatürk Cd. No:1, Ankara | https://… | 0312 555 00 00 | info@… | https://www.google.com/maps/place/… |

## 🛠️ Proje yapısı

```text
├── kolaykontak.py          # Ana uygulama (PyQt5 arayüzü)
├── maps_veri.py            # Google Maps veri çekme mantığı (Selenium)
├── lisans_olusturucu.py    # Lisans anahtarı üretme aracı
└── requirements.txt
```

### Tek dosya .exe oluşturma (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon kolaykontak.ico --add-data "kolaykontak.ico;." --add-data "kolaykontak.jpeg;." kolaykontak.py
```

## 🩺 Sorun giderme

<details>
<summary><b>"Tarayıcı başlatılamadı"</b></summary>

Firefox ya da Chrome kurulu olmalıdır. İnternet bağlantınız sürücü indirmeyi engelliyorsa geckodriver'ı elle indirip program klasörüne `geckodriver.exe` adıyla koyun.

</details>

<details>
<summary><b>"Sonuç listesi yüklenmedi"</b></summary>

Arama terimini Google Maps'te elle deneyin. Çok genel ya da hatalı aramalar sonuç döndürmeyebilir. Kısa sürede çok fazla arama yaptıysanız Google geçici olarak doğrulama isteyebilir. Biraz bekleyip tekrar deneyin.

</details>

<details>
<summary><b>Bazı alanlar boş geliyor</b></summary>

Her işletme bütün bilgileri Google Maps'e girmemiştir. Web sitesi olmayan işletmeler için e-posta aranamaz.

</details>

## ⚠️ Yasal uyarı

Toplanan veriler kişisel veri içerebilir. Verileri **6698 sayılı KVKK** kapsamında işlemek sizin sorumluluğunuzdadır. Bu verilerle SMS, e-posta veya WhatsApp üzerinden **ticari ileti** göndermek için alıcıların önceden onayı gerekir (6563 sayılı Kanun ve İYS). Google Maps'in kullanım koşullarını da göz önünde bulundurun.
