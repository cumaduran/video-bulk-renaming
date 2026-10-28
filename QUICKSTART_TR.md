# EpisodeFlow — Türkçe hızlı başlangıç

Bu proje video dosyalarını **içeriklerini değiştirmeden** bölüm numarasına göre yeniden adlandırır.

## Windows uygulamasını çalıştırma

1. GitHub'a projeyi yükledikten sonra **Actions → Build Windows EXE → Run workflow** aç.
2. İşlem tamamlanınca `EpisodeFlow-Windows-...` adlı dosyayı indir.
3. Dosyayı ZIP'ten çıkartıp `EpisodeFlow.exe` dosyasına çift tıkla.
4. Klasörü seç, `ANI_ROTA_*(x)*_4K` şablonunu gir, önce önizlemeyi kontrol et.
5. **Dosyaları yeniden adlandır** butonuna tıkla. Son işlemi **Geri Al** ile tersine çevirebilirsin.

## Windows bilgisayarında kaynak kodu çalıştırma

```powershell
cd C:\Projects\video-bulk-renaming
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py
```

## EXE'yi kendin üretmek

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

`dist\EpisodeFlow.exe` oluşur. ZIP dosyasındaki proje kaynak kodudur; hazır EXE değildir. EXE derlemesi Windows ortamında ya da GitHub Actions'da yapılır.

## GitHub'a gönderme

İstersen tek komutla **özel** depo oluşturup push yapabilirsin (önce `gh auth login`):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_github.ps1
```

Elle yapmak için:

```powershell
cd C:\Projects\video-bulk-renaming
git init
git add .
git commit -m "feat: EpisodeFlow initial release"
git branch -M main
gh auth login
gh repo create video-bulk-renaming --private --source . --remote origin --push
```

**Dikkat:** Uygulama bölüm numarasını dosya adından bulur. Çakışan veya belirsiz isimleri değişmeden bırakır. Önce dosyaların kopyasında dene.


## Geliştirici ve GitHub sürümü

**Geliştirici:** [@cumaduran](https://github.com/cumaduran) (Cuma Duran). Uygulamanın alt kısmındaki geliştirici bağlantısına tıklayarak profili açabilirsiniz.

**İndirilebilir GitHub Release oluşturma:** Kodları GitHub'a gönderdikten sonra deponuzda **Actions → Build Windows EXE → Run workflow** yoluna gidin. `Release tag` alanına `v1.0.0` yazıp **Run workflow** düğmesine basın. Başarılı Windows derlemesinden sonra **Releases** bölümünde `EpisodeFlow.exe`, `EpisodeFlow-Windows.zip` ve doğrulama için `SHA256SUMS.txt` bulunur. Sadece derleme yapmak istiyorsanız `Release tag` alanını boş bırakın.

Herkesin indirebilmesi için GitHub deponuz **Public** olmalıdır. Kaynak kod ZIP dosyasının kendisi `.exe` değildir. İlk EXE'nin gerçek Windows makinede test edilmesi önerilir.
