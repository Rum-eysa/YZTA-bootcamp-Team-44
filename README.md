# YZTA Bootcamp - AI Destekli Staj Başvuru Platformu

<div align="center">

![YZTA Bootcamp](https://img.shields.io/badge/YZTA-Bootcamp-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Next.js](https://img.shields.io/badge/Next.js-14.2-black)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Yapay zeka destekli kişiselleştirilmiş CV ile önyazı oluşturma ve başvuru takip platformu**

[Ürün Özellikleri](#ürün-özellikleri) • [Sprint Planı](#sprint-planı) • [Mimari](#mimari) • [Hızlı Başlangıç](#hızlı-başlangıç) • [API Endpoint'leri](#api-endpointleri) • [Agent Sistemi](#agent-sistemi) • [Katkıda Bulunma](#katkıda-bulunma)

</div>

---

## Takım İsmi

Takım 44

## Takım Rolleri

| Rol | Kişi | GitHub | LinkedIn |
|-----|------|--------|----------|
| Product Owner | Rumeysa AĞIL | [![GitHub](https://img.shields.io/badge/GitHub-@Rum-eysa-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Rum-eysa) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-rumeysaagil-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rumeysaagil/) |
| Scrum Master | Serkan YILDIZ | [![GitHub](https://img.shields.io/badge/GitHub-@Serkan0YLDZ-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Serkan0YLDZ) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-serkan0yldz-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/serkan0yldz/) |
| Developer | Zeynep Maide DEMİR | [![GitHub](https://img.shields.io/badge/GitHub-@zeynepmaidedemir-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/zeynepmaidedemir) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-zeynep-maide-demir-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/zeynep-maide-demir/) |
| Developer | Filiz Buzkıran | [![GitHub](https://img.shields.io/badge/GitHub-@lizlavigne-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/lizlavigne) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-filizbuzkiran-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/filizbuzkiran) |

## Ürün İsmi

CareerTrack 

## Ürün Açıklaması

CareerTrack, iş ve staj arayan adaylar için yapay zeka destekli bir kariyer takip platformudur. İlan metnini analiz ederek aranan becerileri çıkarır, profil ile ilan arasındaki uygunluğu puanlar ve her başvuru için ATS uyumlu CV ile önyazı üretir. Adaylar belge dilini ve CV şablonunu ilana göre seçebilir; ister kayıt olmadan kullandıkları CV için ATS skorunu öğrenebilir, ister tüm başvurularını tek yerden yönetebilir.

## Problem Tanımı

Aynı dönemde birçok ilana başvuran adaylar, her pozisyonun farklı beklentilerine CV ve önyazıyı elle uyarlamak zorunda kalır. Bu iş hem zaman alır hem de hangi başvuruya öncelik verileceğini belirsizleştirir; süreç dosyalar, e-postalar ve notlar arasında dağılır. Sonuçta adaylar çoğu zaman genel bir CV ile ilerler veya başvurularını takip etmekte güçlük çeker.

## İş Değeri

- Her iş ilanı için CV ve önyazıyı kişiselleştirir.
- İlanda aranan beceri ve deneyimleri net şekilde ortaya çıkarır.
- Adayın ilana uygunluğunu puanlayarak hangi başvurulara öncelik verileceğini gösterir.
- Kayıt olmadan ATS uyumluluğunu ölçerek CV’nin ilk filtreyi geçme şansını artırır.
- Tüm başvuruları tek platformda takip ederek süreci düzenli hale getirir.

## Ürün Özellikleri

- **AI Destekli İlan Analizi** - Google Gemini ile iş ilanındaki beceri ve deneyim beklentilerini çıkarma.
- **Uygunluk Skoru** - Zorunlu, tercih, kıdem ve anlamsal boyutlarda ilan–profil eşleşme puanı.
- **Misafir ATS Kontrolü** - Kayıt olmadan PDF CV yükleyip Tasarım / Düzen / İçerik ATS skoru alma.
- **Kişiselleştirilmiş CV Üretimi** - Her ilana özel ATS uyumlu LaTeX CV; çoklu şablon, avatar ve edit prompt.
- **Belge Dili (TR/EN)** - İlan bazında CV ve önyazı dilini seçme.
- **Otomatik Önyazı** - İlan ve profil bilgisine göre önyazı; ekstra prompt ve yeniden üretim desteği.
- **Başvuru Takibi** - Başvurulan tüm iş ilanlarını tek yerden izleme ve yeniden analiz etme.
- **Güvenli Kimlik Doğrulama** - JWT tabanlı kimlik doğrulama ve bcrypt şifreleme.
- **Yüksek Performans** - Redis önbellekleme katmanı ile asenkron işleme.
- **İzlenebilirlik** - Yapılandırılmış loglama ve istek takibi.
- **Kurumsal Güvenlik** - CORS, hız sınırlama, güvenlik başlıkları ve giriş doğrulama.
- **Kapsamlı Testler** - Yüksek kapsamlı birim ve entegrasyon testleri.
- **Sürekli Entegrasyon / Dağıtım** - GitHub Actions ile otomatik test ve dağıtım; Railway + Vercel deploy.
- **Veritabanı Göçleri** - Alembic ile versiyon kontrollü şema değişiklikleri.
- **Modern Arayüz** - TailwindCSS ve Next.js ile duyarlı kullanıcı arayüzü.

## Hedef Kitle

- Staj ve iş arayan öğrenciler
- Birden fazla pozisyona eş zamanlı başvuran adaylar
- CV ve önyazısını her ilana göre uyarlamak isteyen kullanıcılar

## Ürün Backlog'u

Proje backlog bilgileri GitHub Projects üzerinden yönetilmektedir:

- [GitHub Projects Backlog](https://github.com/users/Rum-eysa/projects/6/views/1?groupedBy%5BcolumnId%5D=364119553)
- Sprint planları ve görev takibi burada güncellenmektedir
- Sprint 1 detayları için [Sprint 1](#sprint-1), Sprint 2 için [Sprint 2](#sprint-2), Sprint 3 için [Sprint 3](#sprint-3) bölümüne bakınız

## Sprint Planı

### Sprint 1

<details id="sprint-1">
<summary><strong>Sprint 1 detayları için tıklayın</strong></summary>

<br>

- **Product Backlog:** Backlog ve sprint görevleri [GitHub Projects](https://github.com/users/Rum-eysa/projects/6/views/1?groupedBy%5BcolumnId%5D=364119553) üzerinden yönetilmektedir. User story'ler `[US-00X]` formatında tanımlanmış; Status sütununda Todo, In Progress ve Done durumları takip edilmektedir.

  ![GitHub Project Board](docs/sprint-1/github-project-board.png)

- **Sprint Puanlaması:** Sprint 1 planı (19 Haziran – 5 Temmuz) toplam **62 story point** (12 user story). Story point'ler görev karmaşıklığına göre planlanmıştır (3–8 SP arası). Kod denetimi sonucu: **12 story tamamlandı** — kazanılan **62 / 62 SP (%100)**. 

  | Story | Başlık | SP | Öncelik | Durum | Kazanılan |
  | ----- | ------ | -- | ------- | ----- | --------- |
  | US-001 | Proje Altyapısı Kurulumu | 8 | must-have | ✅ Tamamlandı | 8 |
  | US-002 | Supabase Kurulumu | 5 | must-have | ✅ Tamamlandı | 5 |
  | US-003 | Veritabanı Şeması | 5 | must-have | ✅ Tamamlandı | 5 |
  | US-004 | SPIKE: LaTeX → PDF (Tectonic + Docker) | 8 | must-have | ✅ Tamamlandı | 8 |
  | US-005 | Authentication Sistemi | 5 | must-have | ✅ Tamamlandı | 5 |
  | US-006 | Frontend: Ana Layout + Header + Sidebar | 5 | must-have | ✅ Tamamlandı | 5 |
  | US-007 | Frontend: Login & Register Sayfaları | 5 | must-have | ✅ Tamamlandı | 5 |
  | US-008 | Frontend: Kullanıcı Profil Formu | 5 | high | ✅ Tamamlandı | 5 |
  | US-009 | Frontend: İlan Girişi (metin / URL) | 3 | must-have | ✅ Tamamlandı | 3 |
  | US-010 | Seed Verisi | 3 | high | ✅ Tamamlandı | 3 |
  | US-011 | Temel Agent Sınıfı + Logging Framework | 5 | high | ✅ Tamamlandı | 5 |
  | US-012 | Gemini API İstemci Wrapper'ı | 5 | must-have | ✅ Tamamlandı | 5 |
  |  | **Toplam** | **62** |  | **12 tamamlandı** | **62** |

  **Özet:** Planlanan 62 SP’nin tamamı kazanıldı (**62 / 62, %100**). Sprint 1 kapsamı dışında erken tamamlanan bonus işler: 4 AI agent modülü, `POST /api/analyze`, MinIO depolama (~62 pytest).

- **Daily Scrum:** Ekip 2 günde bir Slack Huddle üzerinden senkron toplantı yapmıştır. 

  *AI / Backend ilerleme paylaşımı — Zeynep'in agent sunumu:*

  ![Daily Scrum — Agent sunumu](docs/sprint-1/daily-scrum-agent-sunumu.png)

  *Frontend ilerleme paylaşımı — Serkan'ın UI prototip sunumu:*

  ![Daily Scrum — Frontend sunumu](docs/sprint-1/daily-scrum-frontend-sunumu.png)

- **Ürün Geliştirme Durumu:** Backend ve AI tarafında ilan analizi, aday uygunluk puanlama, kişiselleştirilmiş CV ve önyazı üretimi çalışır durumdadır (`POST /api/analyze`, Gemini client, agent framework, MinIO PDF depolama). Frontend tarafında CareerTrack arayüzünün profil ve ilan ekleme ekranları hazırlanmıştır; Next.js'te temel sayfalar mevcuttur (`login`, `register`, `profile`, `apply`).

  *Profil sayfası — kullanıcı bilgileri, özet ve beceriler:*

  ![Ürün durumu — Profil](docs/sprint-1/urun-durumu-profil.png)

  *İlan ekleme sayfası — şirket, pozisyon ve ilan detayları:*

  ![Ürün durumu — İlan Ekle](docs/sprint-1/urun-durumu-ilan-ekle.png)

- **Sprint Review:** Sprint 1 hedeflerinin tamamı kapanmıştır (**62 / 62 SP, %100**). Çıkan ürün testlerde kritik bir sorun göstermemiştir. 

  **Tamamlananlar:**
  - Monorepo altyapısı: FastAPI + Next.js + Docker Compose (PostgreSQL, Redis, MinIO)
  - Supabase/PostgreSQL şeması: `users`, `job_listings`, `matches`, `documents`
  - JWT authentication, Redis token blacklist, seed verisi (`make seed`)
  - AI agent katmanı: ilan analizi, eşleştirme, CV üretimi (Tectonic PDF), önyazı üretimi
  - `POST /api/analyze`, `PATCH /api/profiles/me`, Gemini client (rate limit, token tracking)
  - CareerTrack frontend: layout, login/register, profil ve ilan ekleme sayfaları; ilan analizi API entegrasyonu

  **Alınan kararlar:**
  - US-004: Standalone compiler kaldırıldı; Tectonic API Docker image içine gömüldü
  - `applications` CRUD yerine agent odaklı veri modeli benimsendi
  - İlan analizi ve üretilen dokümanlar veritabanında kalıcı olarak saklanır; kullanıcı akışı kanonik ilan detay rotasına yönlenir
  - CV/önyazı üretimi backend'de hazır; kullanıcı arayüzüne uçtan uca entegrasyon Sprint 2 kapsamına alındı

- **Sprint Retrospective:** 

  - **İyi giden:** Backend ve agent altyapısı erken tamamlandı.
  - **İyileştirme:** GitHub Projects board'u sprint sonu koxwd durumuyla senkron tutuldu.
  - **İyileştirme:** Kısmi story'lerde eksik AC'ler Sprint 2 borç listesine taşındı (~8 SP).
  - **Sprint 2 planlandı:** Sprint 1 retrospective sonrası Sprint 2 backlog'u revize edildi.

</details>

### Sprint 2

<details id="sprint-2">
<summary><strong>Sprint 2 detayları için tıklayın</strong></summary>

<br>

- **Product Backlog:** Sprint 2 görevleri [GitHub Projects](https://github.com/users/Rum-eysa/projects/6/views/1?groupedBy%5BcolumnId%5D=364119553) üzerinden yönetilmiştir. Sprint 1 borçları (`US-002†`…`US-010†`), çekirdek agent/UI story’leri (`US-013`…`US-035`) ve wishlist/borç kartları (`US-036`…`US-042`) bu sprintte takip edilmiştir.

  ![GitHub Project Board — Sprint 2](docs/sprint-2/github-project-board.png)

- **Sprint Puanlaması:** Sprint 2 planı toplam **~90 story point** (35 user story: borç + çekirdek + US-036…042). Kod denetimi sonucu: **35 story tamamlandı** — kazanılan **~90 / 90 SP (%100)**.


<table width="100%">
<thead>
<tr>
<th width="12%">Story</th>
<th width="40%">Başlık</th>
<th width="8%">SP</th>
<th width="12%">Öncelik</th>
<th width="18%">Durum</th>
<th width="10%">Kazanılan</th>
</tr>
</thead>
<tbody>
<tr>
<td>US-002†</td>
<td>Supabase Borç Kapatma</td>
<td>2</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-006†</td>
<td>Layout Borç Kapatma</td>
<td>2</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-008†</td>
<td>Profil Borç Kapatma</td>
<td>2</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-009†</td>
<td>İlan Girişi Borç Kapatma</td>
<td>1</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>1</td>
</tr>
<tr>
<td>US-010†</td>
<td>Seed Borç Kapatma</td>
<td>1</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>1</td>
</tr>
<tr>
<td>US-013</td>
<td>İş Deneyimi & Proje Şeması</td>
<td>3</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-014</td>
<td>Analysis Agent: Tamamlama</td>
<td>1</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>1</td>
</tr>
<tr>
<td>US-015</td>
<td>CV Generation Agent: API Wiring</td>
<td>2</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-016</td>
<td>Matching Agent: API Wiring</td>
<td>2</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-017</td>
<td>Memory Layer: Context Manager</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-018</td>
<td>Logging + Sentry</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-019</td>
<td>Frontend: İş Deneyimi CRUD</td>
<td>4</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>4</td>
</tr>
<tr>
<td>US-020</td>
<td>Frontend: Proje CRUD</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-021</td>
<td>Matching: Skor Sistemi</td>
<td>3</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-022</td>
<td>Cover Letter Agent: API Wiring</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-023</td>
<td>API: <code>/api/match</code></td>
<td>2</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-024</td>
<td>Score Gauge (ilan detay)</td>
<td>5</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-025</td>
<td>API: generate-cv & cover-letter</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-026</td>
<td>Skill Comparison Table</td>
<td>5</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-027</td>
<td>CV Preview + Download</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-028</td>
<td>Cover Letter View</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-029</td>
<td>Job Form → <code>/api/analyze</code></td>
<td>2</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-030</td>
<td>Orchestrator</td>
<td>5</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-031</td>
<td>API E2E Testler</td>
<td>1</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>1</td>
</tr>
<tr>
<td>US-032</td>
<td>Results API Integration</td>
<td>4</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>4</td>
</tr>
<tr>
<td>US-033</td>
<td>Agent Unit Tests (%80+)</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-034</td>
<td>E2E Integration Tests</td>
<td>5</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-035</td>
<td>Staging Deploy</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-036</td>
<td>Kaydet Butonu UX</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-037</td>
<td>Yeniden Analiz & Eşleştirme</td>
<td>5</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-038</td>
<td>Zengin Seed</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-039</td>
<td><code>/results</code> → <code>/listings/:id</code></td>
<td>3</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-040</td>
<td>Match sahiplik kontrolü</td>
<td>1</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>1</td>
</tr>
<tr>
<td>US-041</td>
<td>Orchestrator sıra/retry uyumu</td>
<td>2</td>
<td>medium</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-042</td>
<td>CV route 422/503 testleri</td>
<td>1</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>1</td>
</tr>
<tr>
<td></td>
<td><strong>Toplam</strong></td>
<td><strong>~90</strong></td>
<td></td>
<td><strong>35 tamamlandı</strong></td>
<td><strong>~90</strong></td>
</tr>
</tbody>
</table>

  **Özet:** Planlanan ~90 SP’nin tamamı kazanıldı (**~90 / 90, %100**). Sprint 1 sonrası öne çıkanlar: tek kanonik ilan detay sayfası, eşleşme/CV/önyazı uçtan uca UI, deneyim-proje CRUD, ContextManager + Orchestrator, yeniden analiz/eşleştirme, zengin seed, staging deploy ve agent test coverage gate.

- **Daily Scrum:** Ekip Slack Huddle üzerinden senkron toplantı yapmıştır.

  *Profil / frontend ilerleme paylaşımı — Serkan’ın ekran paylaşımı:*

  ![Daily Scrum — Profil sunumu](docs/sprint-2/daily-scrum-profil-sunumu.png)

  *Ana sayfada yapılabilecek değişikliklerin konuşulması — Serkan’ın ekran paylaşımı:*

  ![Daily Scrum — Ana sayfa sunumu](docs/sprint-2/daily-scrum-anasayfa-sunumu.png)

- **Ürün Geliştirme Durumu:** CareerTrack artık ilan eklemeden sonuç üretimine kadar tek akışta çalışır. `/apply` → analiz → `/listings/:id` üzerinde skor gauge, beceri karşılaştırması, ilana özel CV (önizle/indir) ve önyazı (üret/kopyala) sunulur; ilan değişince yeniden analiz ve eşleşme güncellenebilir. Profilde iş deneyimi ve proje CRUD, seed ile demo verisi, Railway/Vercel staging hazırdır.

  *Giriş ekranı:*

  ![Ürün durumu — Giriş](docs/sprint-2/urun-durumu-giris.png)

  *Profil — deneyim, eğitim ve projeler:*

  ![Ürün durumu — Profil](docs/sprint-2/urun-durumu-profil.png)

  *Başvurulan ilanlar listesi:*

  ![Ürün durumu — İlanlar](docs/sprint-2/urun-durumu-ilanlar.png)

  *İlan detay — düzenleme, skor özeti ve Yeniden Analiz:*

  ![Ürün durumu — İlan detay](docs/sprint-2/urun-durumu-ilan-detay.png)

  *Uygunluk sonucu — skor gauge ve beceri tablosu:*

  ![Ürün durumu — Uygunluk](docs/sprint-2/urun-durumu-uygunluk.png)

  *İlana özel CV önizleme / indirme:*

  ![Ürün durumu — CV](docs/sprint-2/urun-durumu-cv.png)

  *Önyazı üretimi — kopyala ve sayaç:*

  ![Ürün durumu — Önyazı](docs/sprint-2/urun-durumu-onyazi.png)

- **Sprint Review:** Sprint 2 hedeflerinin tamamı kapanmıştır (**~90 / 90 SP, %100**).

  **Tamamlananlar:**
  - Sprint 1 borçları: layout/sidebar, profil alanları, ilan girişi, seed (matches/documents + zengin profil verisi), Supabase kapsam dokümantasyonu
  - Backend: iş deneyimi/proje şeması + CRUD; ContextManager; Orchestrator (`POST /api/process`); `POST /api/match`, `generate-cv`, `generate-cover-letter`; ilan sahipliği; reanalyze/rematch + `analyzed_at`
  - Frontend: tek sayfa `/listings/:id` (US-039); skor gauge, beceri tablosu, CV önizleme, önyazı view; landing fark vurgusu
  - Kalite: agent unit testleri + CI `%80` gate, E2E entegrasyon testleri, Sentry/observability
  - Deploy: Railway backend + Vercel frontend; [`docs/deploy.md`](docs/deploy.md)

  **Alınan kararlar:**
  - `/results` tamamen kaldırıldı; kanonik rota `/listings/:id`
  - İlan değişince otomatik yeniden skor yok — kullanıcı **Yeniden Analiz Et** / **Eşleşmeyi Güncelle** ile tetikler (US-037)
  - ATS odaklı LaTeX şablon yenileme ve CV’ye sertifika/dil/sosyal alanların tam aktarımı Sprint 3’e alındı (US-043/044)
  - Staging/production URL’leri demo için donduruldu; UAT checklist Sprint 3’te kapanacak

- **Sprint Retrospective:**

  - **İyi giden:** Agent API’ler ile frontend sonuç UI’si aynı sprintte birleşti; board’daki Done kartları ürünle hizalandı.
  - **İyileştirme:** Wishlist maddeleri yeni story (US-036…042) olarak açıldı; 
  - **Sprint 3 planlandı:** ATS CV şablonu, tam profil→CV, UAT ve demo prova.

</details>

### Sprint 3

<details id="sprint-3">
<summary><strong>Sprint 3 detayları için tıklayın</strong></summary>

<br>

- **Product Backlog:** Sprint 3 görevleri [GitHub Projects](https://github.com/users/Rum-eysa/projects/6/views/1?groupedBy%5BcolumnId%5D=364119553) üzerinden yönetilmiştir. Sprint 2’den taşınan CV/deploy kartları (`US-043`…`US-046`), önyazı ve ATS story’leri (`US-049`, `US-054`…`US-061`) ile Sprint 2 borç kapanışı (`US-036†`) bu sprintte takip edilmiştir.

- **Sprint Puanlaması:** Sprint 3 planı toplam **~51 story point** (14 user story: CV pipeline + ATS landing + önyazı/analiz iyileştirmeleri). Kod denetimi sonucu: **14 story tamamlandı** — kazanılan **~51 / 51 SP (%100)**.

<table width="100%">
<thead>
<tr>
<th width="12%">Story</th>
<th width="40%">Başlık</th>
<th width="8%">SP</th>
<th width="12%">Öncelik</th>
<th width="18%">Durum</th>
<th width="10%">Kazanılan</th>
</tr>
</thead>
<tbody>
<tr>
<td>US-036†</td>
<td>Sticky Kaydet (Sprint 2 borç)</td>
<td>1</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>1</td>
</tr>
<tr>
<td>US-043</td>
<td>ATS-Uyumlu LaTeX CV Şablonu</td>
<td>5</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-044</td>
<td>CV Üretiminde Tam Profil Verisi</td>
<td>5</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-045</td>
<td>Landing Page Yenileme</td>
<td>3</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-046</td>
<td>Staging / Production Deploy</td>
<td>5</td>
<td>must-have</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-049</td>
<td>Önyazı: Ekstra Prompt + Motivasyon</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-054</td>
<td>Misafir ATS CV Kontrolü + Landing</td>
<td>5</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-055</td>
<td>Çoklu CV Şablonu, Avatar, Edit Prompt</td>
<td>5</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-056</td>
<td>İlan Bazlı Belge Dili (TR/EN)</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-057</td>
<td>Önyazı Regenerate’de Önceki Metin</td>
<td>2</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>2</td>
</tr>
<tr>
<td>US-058</td>
<td>CV İçerik Alaka Filtresi</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-059</td>
<td>CV İlana Göre Rewrite + 1 Sayfa</td>
<td>5</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>5</td>
</tr>
<tr>
<td>US-060</td>
<td>CV Özeti: Ekstra Prompt</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td>US-061</td>
<td>Analiz: Süre≠Beceri + Kota Hatası</td>
<td>3</td>
<td>high</td>
<td>✅ Tamamlandı</td>
<td>3</td>
</tr>
<tr>
<td></td>
<td><strong>Toplam</strong></td>
<td><strong>~51</strong></td>
<td></td>
<td><strong>14 tamamlandı</strong></td>
<td><strong>~51</strong></td>
</tr>
</tbody>
</table>

  **Özet:** Planlanan ~51 SP’nin tamamı kazanıldı (**~51 / 51, %100**). Sprint 2 sonrası öne çıkanlar: ATS uyumlu çoklu CV şablonları, tam profil → CV, misafir ATS skoru landing’i, ilan bazlı belge dili, CV alaka/rewrite/kısaltma ve önyazı ekstra prompt akışı.

- **Daily Scrum:** Ekip Slack Huddle üzerinden senkron toplantı yapmıştır.

  *Deploy ve PR durumu — Rumeysa’nın GitHub Deployments ekran paylaşımı:*

  ![Daily Scrum — Deployments](docs/sprint-3/daily-scrum-deployments.png)

- **Ürün Geliştirme Durumu:** CareerTrack artık misafir ATS kontrolünden ilana özel CV/önyazı üretimine kadar uçtan uca çalışır. Landing’de kayıt olmadan ATS skoru alınır; `/apply` üzerinde belge dili, önyazı tonu ve CV tercihi seçilir; `/listings/:id` üzerinde uygunluk skoru (zorunlu / tercih / kıdem / anlamsal), yeniden analiz ve ilana özel doküman üretimi sunulur.

  *Landing — ATS CV skoru ve “Neden CareerTrack?”:*

  ![Ürün durumu — Landing ATS](docs/sprint-3/urun-durumu-landing-ats.png)

  *İlan ekleme — şirket/pozisyon, belge dili, önyazı ve CV tercihi:*

  ![Ürün durumu — İlan Ekle](docs/sprint-3/urun-durumu-ilan-ekle.png)

  *İlan detay — düzenleme, Yeniden Analiz Et ve eşleşme skoru:*

  ![Ürün durumu — İlan detay](docs/sprint-3/urun-durumu-ilan-detay.png)

- **Sprint Review:** Sprint 3 hedeflerinin tamamı kapanmıştır (**~51 / 51 SP, %100**).

  **Tamamlananlar:**
  - CV pipeline: ATS LaTeX şablonları; tam profil alanlarının CV’ye aktarımı; Version1–5 şablon seçimi, avatar ve edit prompt
  - Backend / agent: belge dili TR/EN; CV alaka filtresi, ilana göre rewrite + 1 sayfa kısaltma; özet ekstra prompt; analiz süre≠beceri ayrımı ve kota hatası netliği
  - Önyazı: kullanıcı ekstra prompt / motivasyon stratejisi; yeniden üretimde önceki metni kullanma
  - Frontend: misafir ATS landing (skor gauge + Tasarım/Düzen/İçerik); ilan ekleme tercihler UI; sticky kaydet
  - Deploy: Railway staging/production dağıtımlarının sprint boyunca sürdürülmesi

  **Alınan kararlar:**
  - Misafir kullanıcılar kayıt olmadan günlük 1 ATS skoru alabilir
  - CV ve önyazı dili ilan bazında seçilir (`tr` / `en`)
  - Tek şablon yerine ilan bazlı çoklu CV şablon tercihi kullanılır
  - İlan metni değişince skor otomatik güncellenmez; kullanıcı **Yeniden Analiz Et** ile tetikler

- **Sprint Retrospective:**

  - **İyi giden:** CV pipeline ile misafir ATS aynı sprintte ürünleşti; deploy’lar huddle’da görünür takip edildi.
  - **İyileştirme:** Landing ve ilan formu tercihlerinin (dil, ton, şablon) erken hizalanması demo akışını hızlandırdı.

</details>

## Mimari

```
.
├── apps/
│   ├── api/                         # FastAPI Backend Service
│   │   ├── app/
│   │   │   ├── main.py              # Application entry point
│   │   │   ├── config.py            # Configuration management
│   │   │   ├── database.py          # Database connection
│   │   │   ├── models/              # SQLAlchemy ORM (User, JobListing, Match, Document)
│   │   │   ├── routes/              # API endpoints
│   │   │   │   ├── auth.py          # Authentication (/api/auth)
│   │   │   │   ├── users.py         # User management (/api/users)
│   │   │   │   ├── profiles.py      # Profile update (/api/profiles)
│   │   │   │   ├── analysis.py      # İlan analizi (/api/analyze)
│   │   │   │   ├── ats_check.py     # Misafir ATS kontrolü (/api/ats-check)
│   │   │   │   ├── listings.py      # İlan CRUD (/api/listings)
│   │   │   │   ├── match.py         # Eşleştirme (/api/match)
│   │   │   │   ├── cv_generation.py # CV üretimi (/api/generate-cv)
│   │   │   │   ├── cover_letter.py  # Önyazı üretimi (/api/generate-cover-letter)
│   │   │   │   ├── documents.py     # Korumalı CV indirme (/api/documents)
│   │   │   │   ├── orchestrator.py  # Orkestratör (POST /api/process)
│   │   │   │   ├── agents.py        # Agent task API (/api/agents)
│   │   │   │   └── health.py        # Health checks (/health)
│   │   │   ├── services/            # Business logic layer
│   │   │   │   ├── auth.py          # JWT, token blacklist
│   │   │   │   ├── user.py          # User service
│   │   │   │   ├── agent.py         # Agent task orchestration
│   │   │   │   ├── context.py       # ContextManager (profil verisi toplama)
│   │   │   │   ├── gemini_client.py # Google Gemini wrapper
│   │   │   │   ├── storage.py       # MinIO PDF depolama
│   │   │   │   └── listing_fetch.py # URL'den ilan metni çekme
│   │   │   ├── agents/              # AI agent modülleri
│   │   │   │   ├── listing_analysis.py
│   │   │   │   ├── matching.py
│   │   │   │   ├── cv_generation.py
│   │   │   │   ├── cover_letter.py
│   │   │   │   ├── ats_check.py     # Misafir ATS CV skoru
│   │   │   │   ├── orchestrator.py  # Ajanları zincirleyen orkestratör
│   │   │   │   ├── strategy.py      # Düşük-skor / ekstra-prompt stratejisi
│   │   │   │   └── prompt_safety.py # Prompt injection savunması (extra_prompt delimiting)
│   │   │   ├── templates/cv/        # Çoklu LaTeX CV şablonları (Version1–5)
│   │   │   ├── repositories/        # Veritabanı erişim katmanı
│   │   │   └── schemas/             # Pydantic request/response modelleri
│   │   ├── scripts/
│   │   │   └── seed_database.py     # Demo verisi (US-010)
│   │   ├── tests/                   # Test suite
│   │   ├── alembic/                 # Database migrations
│   │   └── Dockerfile
│   │
│   └── web/                         # Next.js Frontend Service
│       ├── app/                     # App Router
│       │   ├── page.tsx             # Landing + misafir ATS
│       │   ├── login/               # Giriş
│       │   ├── register/            # Kayıt
│       │   ├── profile/             # Profil formu
│       │   ├── apply/               # İlan girişi (dil / şablon / ton)
│       │   ├── listings/            # Başvurulan ilanlar listesi
│       │   └── listings/[listingId]/ # Kanonik ilan, skor, CV, önyazı
│       ├── components/              # UI, landing ve listing bileşenleri
│       ├── lib/api/                 # Endpoint bazlı API istemcileri
│       ├── components/providers/    # Auth ve React Query sağlayıcıları
│       └── Dockerfile
│
├── docs/sprint-1/                   # Sprint 1 dokümantasyon görselleri
├── docs/sprint-2/                   # Sprint 2 dokümantasyon görselleri
├── docs/sprint-3/                   # Sprint 3 dokümantasyon görselleri
├── docs/deploy.md                   # Canlı URL'ler + Railway/Vercel deploy
├── CONTRIBUTING.md                  # Katkı rehberi
├── railway.json                     # Railway deploy config (Dockerfile/start/healthcheck)
├── .github/workflows/ci.yml         # CI/CD pipeline
├── docker-compose.yml               # Development (postgres, redis, minio, api, web)
├── docker-compose.prod.yml          # Production environment
├── Makefile                         # Command shortcuts
└── ...
```

### Teknoloji Stack

| Katman | Teknoloji | Amaç |
| --- | --- | --- |
| **Frontend** | Next.js 14, React 18, TypeScript, TailwindCSS, TanStack React Query | Duyarlı arayüz ve sunucu durumu yönetimi |
| **Backend** | FastAPI, SQLAlchemy 2.0, Pydantic V2 | Yüksek performanslı async API |
| **Veritabanı** | PostgreSQL 15 / Supabase | Ana veri depolama |
| **Önbellek** | Redis 7 | Token blacklist ve önbellekleme |
| **Depolama** | MinIO (S3 uyumlu) | CV PDF dosya depolama |
| **AI/ML** | Google Gemini | İlan analizi, eşleştirme, ATS kontrolü, CV ve önyazı üretimi |
| **PDF** | Tectonic (API image içinde) | LaTeX → PDF derleme |
| **Altyapı** | Docker, Docker Compose | Konteyner orkestrasyonu |
| **Test** | Pytest, pytest-asyncio, Coverage | Birim ve entegrasyon testleri |
| **CI/CD** | GitHub Actions | Otomatik test ve build |
| **Kod Kalitesi** | Black, isort, flake8, mypy, pre-commit | Linting ve formatlama |


## Hızlı Başlangıç

### Gereksinimler

- Docker & Docker Compose 20.10+
- Git
- Node.js 18+ (local development için)

### Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/Rum-eysa/YZTA-bootcamp-Team-44
cd YZTA-bootcamp-Team-44

# Environment değişkenlerini yapılandır
cp .env.example .env

# Tüm servisleri başlat
make build && make up

# Veritabanı tablolarını oluştur
make migrate

# (İsteğe bağlı) Demo kullanıcıları yükle
make seed
```

### Demo Hesaplar

`make seed` sonrası aşağıdaki hesaplarla giriş yapılabilir (tümü için şifre: `seedpass123`):

| E-posta | Seviye | Hedef Pozisyon |
| --- | --- | --- |
| `junior.dev@example.com` | junior | Python Backend Developer Intern |
| `mid.dev@example.com` | mid | Java Backend Developer |
| `ai.engineer@example.com` | senior | AI Engineer |
| `fullstack.multi@example.com` | mid | Full Stack Developer |
| `senior.dev@example.com` | senior | Senior Backend Engineer |

Her hesapta iş deneyimi, proje, eğitim ve sertifika kayıtları önceden dolu gelir; diğer seed kullanıcıları için bkz. `apps/api/scripts/seed_database.py`.

### Canlı Ortam

- **Frontend**: https://yzta-bootcamp-team-44.vercel.app
- **Backend API**: https://yzta-bootcamp-team-44-production.up.railway.app/docs
- Kurulum, ortam değişkenleri ve sorun giderme: [`docs/deploy.md`](docs/deploy.md)

## Geliştirme

### Kullanılabilir Komutlar

```bash
# Servisleri başlat
make up

# Logları görüntüle
make logs

# Testleri çalıştır
make test

# Servisleri durdur
make down

# Tüm ortamı temizle
make clean

# Production deployment
make prod-up
```

Daha fazla komut için [Makefile](./Makefile) dosyasını inceleyebilirsiniz.

### Ortam Yapılandırması

Örnek ortam dosyasını kopyalayın:

```bash
cp .env.example .env
```

**Önemli üretim ayarları:**
- `JWT_SECRET`: Güçlü bir gizli anahtar (32+ karakter)
- `SUPABASE_DB_URL` veya `DB_PASSWORD`: Veritabanı bağlantısı
- `GEMINI_API_KEY`: Geçerli bir Google Gemini API anahtarı
- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`: MinIO kimlik bilgileri
- `DEBUG`: `false` olarak ayarlayın
- `ENVIRONMENT`: `production` olarak ayarlayın

## Veritabanı Yönetimi

Veritabanı migration Alembic ile yönetilir:

```bash
# Yeni migration oluştur
docker-compose exec api alembic revision --autogenerate -m "açıklama"

# Migration'ları uygula
docker-compose exec api alembic upgrade head

# Bir migration geri al
docker-compose exec api alembic downgrade -1
```

## Testler

```bash
# Tüm testleri çalıştır
make test

# Coverage raporu oluştur
docker-compose exec api pytest tests/ --cov=app --cov-report=html
```

## Code Quality

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### Manuel Linting

```bash
# Python (apps/api dizininde)
cd apps/api
black app/
isort app/
flake8 app/
mypy app/

# Frontend
cd apps/web
npm run lint
```

## Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## API Endpoint'leri

Tüm API route'ları `/api` prefix'i altında tanımlıdır (health hariç).

### Authentication
- `POST /api/auth/register` - Kullanıcı kaydı
- `POST /api/auth/login` - Kullanıcı girişi (JWT)
- `POST /api/auth/refresh` - Token yenileme
- `POST /api/auth/logout` - Çıkış (Redis token blacklist)

### Users
- `GET /api/users/me` - Mevcut kullanıcı profili
- `PUT /api/users/me` - Kullanıcı profili güncelleme
- `GET /api/users/{user_id}` - Kullanıcı bilgisi

### Profiles
- `PATCH /api/profiles/me` - Profil güncelleme
- `POST /api/profiles/me/avatar` - Avatar yükleme
- `GET /api/profiles/me/avatar/file` - Avatar dosyası
- `DELETE /api/profiles/me/avatar` - Avatar silme
- `GET|POST /api/profiles/me/experiences` · `PATCH|DELETE .../experiences/{id}` - İş deneyimi CRUD
- `GET|POST /api/profiles/me/projects` · `PATCH|DELETE .../projects/{id}` - Proje CRUD
- `GET|POST /api/profiles/me/education` · `PATCH|DELETE .../education/{id}` - Eğitim CRUD
- `GET|POST /api/profiles/me/certificates` · `PATCH|DELETE .../certificates/{id}` - Sertifika CRUD
- `GET|POST /api/profiles/me/exams` · `PATCH|DELETE .../exams/{id}` - Sınav CRUD
- `GET|POST /api/profiles/me/languages` · `PATCH|DELETE .../languages/{id}` - Dil CRUD
- `GET|POST /api/profiles/me/social-links` · `PATCH|DELETE .../social-links/{id}` - Sosyal link CRUD
- `GET|POST /api/profiles/me/references` · `PATCH|DELETE .../references/{id}` - Referans CRUD

### Listings
- `GET /api/listings` - Kullanıcının ilan listesi
- `GET /api/listings/{listing_id}` - İlan detayı (analiz, eşleşme, dokümanlar)
- `PATCH /api/listings/{listing_id}` - İlan güncelleme (şirket, metin, şablon, belge dili vb.)
- `POST /api/listings/{listing_id}/reanalyze` - İlanı yeniden analiz et
- `POST /api/listings/{listing_id}/rematch` - Eşleşmeyi yeniden hesapla

### Analysis
- `POST /api/analyze` - İlan metni veya URL analizi (AI)

### ATS Check
- `POST /api/ats-check` - Misafir PDF CV ATS skoru (auth yok; IP başına günlük 1)

### Matching & Documents
- `POST /api/match` - Profil ↔ ilan eşleştirme skoru (cache'li)
- `POST /api/generate-cover-letter` - Şirkete özel önyazı üretimi (AI; ekstra prompt / regenerate)
- `POST /api/generate-cv` - İlana özel PDF CV üretimi (LaTeX/Tectonic; şablon + belge dili)
- `GET /api/documents/{document_id}/file` - Korumalı CV PDF indirme / önizleme

### Orchestrator
- `POST /api/process` - Analiz → eşleşme → CV → önyazı zincirini çalıştır

### Agents
- `POST /api/agents/tasks` - Agent görevi oluşturma
- `GET /api/agents/tasks/{task_id}` - Görev durumu
- `GET /api/agents/status` - Agent sistemi durumu

### Health
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe

## Agent Sistemi

Platformda beş ana AI modülü çalışır:

- **İlan Analizi** — İş ilanındaki beceri ve deneyim beklentilerini çıkarır
- **Eşleştirme** — Aday profili ile ilan arasında uygunluk puanı hesaplar (zorunlu / tercih / kıdem / anlamsal)
- **CV Üretimi** — İlana özel ATS uyumlu CV oluşturur; alaka filtresi, rewrite, şablon ve dil seçimi destekler
- **Önyazı Üretimi** — Profil ve ilan bilgisine göre önyazı üretir; ekstra prompt ve önceki metinle regenerate
- **ATS Kontrolü** — Misafir CV yüklemelerinde Tasarım / Düzen / İçerik skorunu hesaplar

## Katkıda Bulunma

Katkı sağlamak için repoyu fork’layın (veya clone’layın), `main` üzerinden bir feature branch açın, değişikliği test edip Pull Request gönderin.

```bash
git clone https://github.com/Rum-eysa/YZTA-bootcamp-Team-44
cd YZTA-bootcamp-Team-44
cp .env.example .env
make build && make up && make migrate
```

Commit mesajı, kod stili, test ve PR kontrol listesi için [`CONTRIBUTING.md`](CONTRIBUTING.md) dosyasına bakın. Sorular ve hata bildirimleri için GitHub Issues kullanabilirsiniz.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](./LICENSE) dosyasına bakın.

## Destek

Sorularınız ve desteğiniz için GitHub'da issue açabilirsiniz.

---

<div align="center">

**Built with ❤️ by YZTA Bootcamp Team 44**

[⬆ Başa Dön](#yzta-bootcamp---ai-destekli-staj-başvuru-platformu)

</div>
