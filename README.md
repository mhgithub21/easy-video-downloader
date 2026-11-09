# Easy Video Downloader

সহজ, ওপেন সোর্স ভিডিও ডাউনলোডার (GUI) — [yt-dlp](https://github.com/yt-dlp/yt-dlp) দিয়ে তৈরি।
A simple, open-source video downloader with a graphical interface, powered by yt-dlp.

## ফিচার / Features
- লিংক পেস্ট করে ক্লিক করলেই ডাউনলোড (একসাথে অনেক লিংক)
- কোয়ালিটি বাছাই (Best / 1080p / 720p / 480p / 360p) ও MP3 অডিও
- প্লেলিস্ট সাপোর্ট, প্রগ্রেস বার
- ডার্ক মোড, ডাউনলোড হিস্ট্রি, অ্যাপ আইকন
- Windows, macOS, Linux **এবং Android (APK)**

## ব্যবহার (সবচেয়ে সহজ উপায়)
1. [Releases](../../releases) পেজ থেকে নিজের সিস্টেমের ফাইল ডাউনলোড করে চালান।

## সোর্স থেকে চালানো
1. [Python 3.9+](https://www.python.org/downloads/) ইন্সটল করুন (Windows-এ "Add Python to PATH" টিক দিন)।
2. প্রজেক্ট ডাউনলোড করুন:
   ```bash
   git clone https://github.com/mhgithub21/easy-video-downloader.git
   cd easy-video-downloader
   ```
3. চালান:
   - **Windows:** `run_windows.bat` এ ডাবল ক্লিক
   - **Mac/Linux:** `./run_mac_linux.sh`
   - অথবা:
     ```bash
     pip install -r requirements.txt
     python app.py
     ```

> Linux-এ Tkinter না থাকলে: `sudo apt install python3-tk`

## 📱 Android অ্যাপ
`android/` ফোল্ডারে Kivy দিয়ে বানানো Android সংস্করণ আছে।
1. [Releases](../../releases) থেকে `.apk` ডাউনলোড করুন।
2. ফোনে খুলে ইন্সটল করুন (Settings থেকে "Install unknown apps" অনুমতি দিতে হবে)।
3. লিংক পেস্ট করে Download চাপুন। ফাইল `Download/EasyVideoDownloader` ফোল্ডারে সেভ হয়
   (অনুমতি না পেলে অ্যাপের নিজস্ব ফোল্ডারে)।

নিজে APK বানাতে: GitHub-এ tag push করুন (নিচে দেখুন) অথবা Actions ট্যাব থেকে "Build Android APK" চালান।

**সীমাবদ্ধতা:** Android-এ ffmpeg নেই, তাই শুধু একক ফাইল ফরম্যাট (সাধারণত সর্বোচ্চ 720p) ও m4a অডিও পাওয়া যায়, MP3 কনভার্ট হয় না।
iOS সংস্করণ নেই (Apple-এর সাইনিং ও নিয়মের কারণে ওপেন সোর্স হিসেবে বিতরণ কঠিন)।

## ffmpeg (ডেস্কটপের জন্য — MP3 ও হাই-কোয়ালিটির জন্য প্রয়োজনীয় — MP3 ও হাই-কোয়ালিটির জন্য)
ffmpeg ছাড়া MP3 কনভার্ট ও আলাদা ভিডিও+অডিও জোড়া লাগানো যায় না।
- Windows: `winget install ffmpeg`
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## আপডেট (সাইট বদলালে ডাউনলোড ফেইল হলে)
```bash
pip install -U yt-dlp
```

## .exe / APK বানানো
`v1.0.0` নামে tag push করলে GitHub Actions নিজেই Windows/Mac/Linux ফাইল ও Android APK বানিয়ে Releases-এ দেবে:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## আইনি সতর্কতা / Disclaimer
শুধু নিজের ভিডিও, পাবলিক ডোমেইন/Creative Commons বা অনুমতিপ্রাপ্ত কনটেন্ট ডাউনলোড করুন।
প্রতিটি ওয়েবসাইটের Terms of Service ও কপিরাইট আইন মেনে চলা ব্যবহারকারীর দায়িত্ব। 
এই সফটওয়্যার "as is" দেওয়া হয়েছে, ডেভেলপার কোনো দায় নেবে না।

## Contributing
Issue ও Pull Request স্বাগত। লাইসেন্স: [MIT](LICENSE)
