# Proje haritası (9 Kasım 2026)

Bu not, yeni bir şirket programı eklerken güncel kodu hızlıca bulmak için hazırlandı. Kaynak olarak çalışan webview uygulamasının kodu esas alındı. `README.md` büyük ölçüde eski Tkinter mimarisini anlatıyor; güncel giriş noktası `app.py`.

## Mimari ve veri akışı

```text
app.py / main()
  └─ pywebview penceresi → gui_web/index.html + style.css + app.js
                              │
                              └─ window.pywebview.api → app.py / Api
                                                        ├─ core/*.py
                                                        ├─ rust_core (Restock)
                                                        └─ Settings/ (ayarlar, hafıza, SQLite)
```

- `gui_web/index.html`: sol menü (`data-view`) ve her programın `id="view-..."` ekranı. İlk açık ekran Restock.
- `gui_web/style.css`: ortak görünüm, temalar ve duyarlı yerleşim.
- `gui_web/app.js`: menü geçişleri, dosya seçme/sürükleme, form doğrulama, ayar editörleri, işlem günlüğü/sonuç gösterimi ve programlara özel olay işleyicileri. Ayrı bir JavaScript derleme sistemi yok; tek dosya doğrudan HTML'e yükleniyor.
- `app.py / Api`: JS'ye açılan Python köprüsü. Dosya iletişim kutuları, ayar/hafıza, uzun işlemlerin başlatılması, ilerleme olayları, FBA veritabanı işlemleri ve güncelleme burada bağlanıyor.
- `core/`: çoğu programın dosya işleme mantığı. Restock ekranı doğrudan `rust_core.process_restock` çağırıyor; `core/restock_processor.py` mevcut olsa da bu ekranın güncel işlem yolu değil.
- `core/title_cleaner.py` başlık temizleme kurallarını, `core/title_workbook.py` kaynak Excel'in diğer hücrelerini koruyarak `New Title` sütunu ekleme veya mevcut sütunu yenileme işini yürütür.
- Title Cleaner tek sayfalı, ilk satırında `Title` başlığı olan düz `.xlsx` dışa aktarımlarını kabul eder; kaynak hücrelerin değer/biçimlerini korur, karmaşık Excel öğelerini veya hücre başvurulu formülleri desteklemediğinde açık hata verir.
- Title Cleaner'da “Override the original file” varsayılan açıktır; açıksa çıktı klasörü gizlenir ve geçici, doğrulanmış `.xlsx` aynı klasörde atomik olarak kaynak dosyanın yerine geçer. Kapalıysa seçilen klasöre yeni dosya yazılır. `New Title` zaten `Title` yanında varsa yeniden hesaplanıp aynı sütunda güncellenir. `Note` sütunu işlemde okunmaz veya değiştirilmez.
- 11 Kasım 2026 çalışan geri bildirimi: paket/adet kalıntıları, tanıtım ifadeleri ve gereksiz özellikler çıkarılır; gerçek ağırlık/hacim, aroma/tarif, renk/model ve ayırt edici bileşenler korunur. `Tea bags` ifadesi ayrıca çıkarılır. Mantar kahvesindeki Reishi/Lion's Mane/Chaga/Turkey Tail/Cordyceps gibi ayırt edici bileşenler korunur. Bu iki tercih kullanıcıyla netleştirildi.
- Amazon arama başlığı hedefi (11 Kasım 2026): ürünün çekirdek adı + çeşidi/kokusu + anlamlı ölçüsü kalmalı. `Baking Soda Free`, `Aluminum Free`, `Non-Irritating`, `Safely and Effectively Fights Odor` gibi aramayı genişleten özellik ve fayda cümleleri çıkarılır; `Natural` çekirdek ürün adındaysa korunur. Marka adındaki `Free` korunur, diğer `Free` özellikleri çıkarılır. Kullanıcının son kararıyla `New Title` en fazla 100 karakterdir. Uzun başlıklarda önce SEO/kullanım cümleleri ve tekrarlar ayıklanır; ölçü ve ayırt edici çeşit/bileşenler önceliklendirilir. Çok uzun özgün ürün adları bu sınıra sözcük sınırında kısaltılabilir.
- Temizleyici Python standart kitaplığındaki düzenli ifadeler ve başlık bölümlerini puanlayan hafif kurallardan oluşur; yeni NLP modeli veya paket bağımlılığı eklenmedi. Mevcut örnek `New Title` verileri tutarsız olduğundan bunlarla eğitilecek küçük bir model hataları da öğrenebilir. Gerçek Amazon arama isabeti henüz ölçülmedi; sonraki iyileştirmeler için insan onaylı eşleşme örnekleri gerekir.
- 11 Kasım hız ölçümü: 52.394 satırlı dosyada Excel okuma/yazma tabanı yaklaşık 14,8 saniye, eski toplam yaklaşık 38 saniye idi. Marka eşleştirmesi önbelleği ve gereksiz düzenli ifade taramalarını atlama ile toplam yaklaşık 24,2 saniyeye indi; 52.394 satırın `New Title` çıktısı önceki sürümle birebir karşılaştırıldı. Rust'a taşıma bu aşamada yapılmadı; kalan maliyetin büyük bölümü Excel okuma/yazma ve kuralların yalnızca yaklaşık 9 saniyelik kısmıdır.
- Title Cleaner ekranının yerleşimi diğer araçlarla aynı tutuldu. Alttaki mevcut konsol kaynak dosya/çıkış türü, sütun doğrulaması, 2.000 satırlık ilerleme, kaydetme, özet, dosya yolu ve toplam süre adımlarını gösterir. `process_title_cleaner` sonuç sözlüğündeki `stats` alanı bu özet için kullanılır.
- `rust_core/src/lib.rs`: PyO3 ile Python'a açılan Rust Restock motoru. `.github/workflows/release.yml` bunu `maturin` ile derleyip kuruyor.
- Sürümün tek kaynağı kökteki `VERSION` dosyasıdır (`1.3.17` gibi, `v` öneki olmadan). `app.py` çalışma anında, `installer.iss` derleme anında bunu okur; `gui_web/app.js` iki sürüm etiketini Python API'den doldurur. `build_webview.spec`, `version.txt` şablonundan Windows EXE sürüm kaynağını üretir ve `VERSION` dosyasını pakete ekler. Release iş akışı etiketin `v` + `VERSION` ile eşleşmesini denetler.

## Ekran → köprü → iş mantığı

| Ekran (`data-view`) | `Api` girişi | İş mantığı / görev |
| --- | --- | --- |
| `restock` | `run_restock` | `rust_core.process_restock`; stok, export ve restock dosyalarını birleştirme |
| `futureprice` | `run_future_price` | `core/future_price_updater.py`; gelecek fiyat dosyası |
| `ordercreate` | `run_order_create` | `core/order_creator.py`; sipariş formları, `Settings/Template/Template.xlsx` |
| `shipment` | `run_shipment_creator` | `core/shipment_creator.py`; sevkiyat oluşturma |
| `tsv` | `run_tsv` | `core/tsv_converter.py`; TSV dosyalarını Excel'e toplama |
| `converter` | `run_converter` | `core/converter.py`; CSV/Excel/metin dönüşümü |
| `titlecleaner` | `run_title_cleaner` | `core/title_cleaner.py` + `core/title_workbook.py`; `New Title` ekleme/yenileme ve isteğe bağlı kaynak dosyaya yazma |
| `costupdater` | `run_costupdater` | `core/cost_updater.py`; V1/V2 maliyet hesaplama |
| `fba` (menüde “Expration”) | `inv_*` yöntemleri | `core/fba_inventory.py`; master/picklist/AMZ stok, FIFO, SQLite ve Excel raporu |
| `invoice` | `run_invoice` | `core/invoice_processor.py`; fatura verisi işleme |
| `invoicefinder` | `run_invoice_finder_date_mode`, `run_invoice_finder_upc_mode` | `core/invoice_finder.py`; fatura/PDF eşleştirme |
| `extractor` | `run_pk_extractor` | `core/pk_extractor.py`; ürün adından paket adedi çıkarma |
| `expiration` (menüde gizli) | `run_expiration` | `core/expiration_processor.py`; 2D Workflow tarih sorgulama |
| `settings` | `get_settings`, `save_settings` vb. | Yerel ayar düzenleme |
| `updates` | `run_check_for_updates`, `run_download_update` vb. | `core/updater_service.py`; GitHub sürüm ve kurulum güncellemesi |

## Ortak sözleşmeler

- Menü öğesindeki `data-view="x"` ile ekranın `id="view-x"` değeri eşleşir. `app.js` aktif sınıflarını değiştirir; bazı ekranlara geçerken ayarları yeniden okur.
- `FileDropZone` dosya seçimi ve liste durumunu yönetir. Python tarafındaki `bind_dropzones()` sürüklenen gerçek dosya yollarını `files-dropped` olayıyla JS'ye iletir.
- Standart uzun iş akışı: JS girişi kontrol eder → `prepareJobUI(prefix)` → `api().run_...(...)`. `Api` tek iş için `_job_lock` alır, daemon thread başlatır, `job-log` ve `job-done` olayları yayınlar. JS'deki `TOOLS` listesi, çalışan butona göre günlüğü/sonucu doğru ekrana bağlar. İptal, `_cancel_event` ve işlemde çağrılan progress callback aracılığıyla işbirlikçi biçimde çalışır.
- FBA ekranı farklı bir akış izler: `inv_*` çağrıları sözlük sonucu döndürür; veriler `Settings/fba_inventory.db` içindeki `shipment_items` ve `amazon_stock` tablolarında tutulur. SQLite WAL ve busy timeout kullanılır.
- Ayar dosyaları ve son kullanılan yollar `Settings/` altında. Varsayılan JSON içerikleri `app.py / DEFAULT_SETTINGS` içinde; `ensure_default_settings()` yalnızca eksik dosyaları oluşturur. `last_paths.json` form yolları/tercihleri, `window_state.json` pencere durumu içindir. 2D Workflow parolası `keyring` içinde, kullanıcı adı hafıza dosyasında tutulur.
- Çıktılar ilgili programın seçilen klasörüne yazılır; PK Extractor çıktıyı kaynak dosyanın yanına yazar. Dosya biçimleri ve zorunlu sütunlar `core` fonksiyonlarında belirlenir.

## Yeni program eklerken bakılacak yerler

1. Girdi dosyası biçimini, sütunları, ayarları, çıktı adını/klasörünü ve hata davranışını netleştir; işlem mantığını uygun bir `core/<program>.py` modülünde tut.
2. `gui_web/index.html` içine menü öğesi ve `view-<id>` ekranı ekle; `gui_web/style.css` içindeki ortak bileşenleri kullan.
3. `gui_web/app.js` içinde dosya alanını, form kontrolünü ve çalıştırma olayını bağla. Uzun işlemse `TOOLS` listesi ile `prepareJobUI`/`job-log`/`job-done` akışına dahil et.
4. `app.py / Api` içine JS'den çağrılan yöntem ekle; uzun işlem için kilit/thread/ilerleme/iptal/sonuç sözleşmesini izle. Yeni ayar dosyası gerekiyorsa `DEFAULT_SETTINGS` ve ilgili editörü bağla.
5. Gerekirse paketlemeyi (`build_webview.spec`, `requirements.txt`, Rust bağımlılığı) ve sürüm akışını (`BUILD.md`, `RELEASE.md`, `installer.iss`) güncelle; iş mantığı için anlamlı test ekle.

## Mevcut yapıda dikkat edilecekler

- `main.py` ve `gui/` eski Tkinter uygulamasına ait ve `.gitignore` içinde; yeni webview programı için doğru entegrasyon yeri değiller. `*.bak`, derleme klasörleri ve kullanıcı verisi de kaynak kod referansı olarak alınmamalı.
- `app.py` ve `gui_web/app.js` çok sayıda özelliği tek dosyada topluyor; yeni program eklerken menü, ekran, köprü ve işlem kaydının tümünü eşleştirmek gerekiyor.
- `app.py` Rust modülünü koşulsuz import ediyor. CI derlemeden önce `maturin` ile kuruyor; yerel `build_shared.bat` içinde bu derleme adımı görünmüyor. Yerel çalışma/derleme ortamında modülün kurulu olduğunu doğrulamak gerekir.
- İnceleme başlangıcında `app.py` içinde kullanıcıya ait mevcut değişiklik vardı: `webview.start(debug=True, ...)`. Bu not için o dosya değiştirilmedi.
