# NeuralBoard (AI Smart Clipboard)

NeuralBoard adalah aplikasi Windows Desktop (berjalan di background) yang dirancang untuk menjadi asisten "Smart Paste" Anda. Aplikasi ini mengambil isi *clipboard* (teks yang disalin), mengirimkannya ke *Artificial Intelligence* (AI) dengan kepribadian tertentu, lalu menimpa dan mem-*paste* teks tersebut secara otomatis ke tempat kursor Anda berada.

## ✨ Fitur Utama
* **Magic Paste (`Ctrl + Alt + V`)**: *Copy* teks apapun, tekan tombol ajaib ini, dan teks barunya akan otomatis di-*paste* (ditempel).
* **Multiple AI Providers**: Mendukung integrasi mulus dengan:
  * OpenAI (`gpt-4o-mini`, `gpt-4o`, dll)
  * Google Gemini (`gemini-1.5-flash`, `gemini-1.5-pro`, dll)
  * ZhipuAI / GLM (`glm-4-flash`)
  * OpenRouter (untuk mengakses ribuan model bebas)
* **Personality Modes**: 
  * 🛠 **Code Fixer**: Input berupa kode error/bug -> Output menjadi kode yang sudah dikoreksi tanpa *markdown*.
  * ✍ **Grammar Polish**: Input tulisan kasar/acak-acakan -> Output menjadi bahasa baku dan formal.
  * 📝 **Summarizer**: Input bacaan panjang -> Output rangkuman dalam tepat 3 *bullet points*.
  * 💼 **Professional Email**: Input kalimat instruksi kasual -> Output email bisnis yang sopan profesional.
* **Realtime Activity Log**: Secara interaktif menangkap pembaruan *(update)* pada clipboard dan melaporkan proses AI.
* **Auto-Save Settings**: Konfigurasi model lokal disimpan aman di `settings.json`.
* **Flet GUI**: Antarmuka *Dark Mode* modern yang ringan.

## 🛠️ Tech Stack
* **Python 3**
* **GUI**: Flet (Framework UI Flutter-based untuk Python)
* **System Hooks**: `keyboard` (untuk mendeteksi dan menginjeksi input `Ctrl+Alt+V` dan `Ctrl+V secara global).
* **Clipboard Manager**: `pyperclip` (untuk membaca dan menimpa *clipboard* Windows).
* **AI API Clients**: `openai`, `google-generativeai`, `requests`.

---

## 🚀 Cara Menjalankan (Development)

### Prasyarat
Sistem Windows 10/11 dengan Python 3 ter-*install*. Disarankan menjalankan di dalam Virtual Environment (venv).

### Instalasi
1. *Clone* repositori atau *download* folder ini.
2. Buka Terminal di folder tersebut dan jalankan instalasi *requirements*:
   ```cmd
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi (Disarankan menjalankan terminal sebagai Administrator agar *library* `keyboard` mendapatkan hak akses penuh `Hook` di Windows):
   ```cmd
   python main.py
   ```

### Penggunaan Aplikasi
1. Saat aplikasi terbuka, centang **Toggle "Enable Smart Paste (Ctrl+Alt+V)"**.
2. Pilih mode kepribadian *(Personality Mode)*.
3. Pilih Provider AI dan masukkan Nama Model beserta API Key-nya.
4. Tekan **Save Settings**.
5. Tutup aplikasi atau pinggirkan jendela. *Copy* (Ctrl+C) teks apa saja, arahkan kursor ke tempat mengetik, lalu lepaskan **Ctrl+Alt+V**.
6. Pantau *Activity Log* untuk status sukses.

---

## 📦 Build Menjadi `.exe` (Standalone Aplikasi Windows)
Anda dapat mem-*build* aplikasi ini menjadi versi `.exe` agar bisa dijalankan di komputer Windows yang belum ter-*install* Python.

1. Buka folder lewat terminal. Pastikan `pyinstaller` sudah di-*install*:
   ```cmd
   pip install pyinstaller
   ```
2. Jalankan perintah kompilasi dari `flet pack`:
   ```cmd
   flet pack main.py --name "NeuralBoard" --hidden-import "keyboard" --hidden-import "pyperclip" --hidden-import "google.generativeai" --hidden-import "openai" --hidden-import "ai_handler"
   ```
3.  Tunggu sekitar 1–3 menit, cari **NeuralBoard.exe** yang baru saja dicetak ke dalam folder `dist/` !

*(Catatan: Jangan tambahkan `settings.json` ke Git agar API Key rahasia tidak bocor).* 
