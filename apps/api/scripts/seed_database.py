"""Gerçekçi demo verisiyle veritabanını seed eder.

Çalıştır: python scripts/seed_database.py (apps/api içinden, PYTHONPATH=. ile)
veya: docker compose exec -e PYTHONPATH=/app api python scripts/seed_database.py

Kullanıcılar bilinçli olarak farklı ünvan/tech-stack kombinasyonlarıyla seçildi
(Python Backend, Java Backend, AI Engineer, çoklu-stack Full Stack) ki CV/önyazı
ajanları ve eşleştirme skoru gerçekçi çeşitlilikte test edilebilsin.

CV test senaryoları (çok uzun paragraflar + bol proje/deneyim → 1 sayfa aşımı /
kısaltma / ilana göre filtre+rewrite / max 3 proje ranking):
  - Ayşe Yılmaz: stajyer profili; ~5 deneyim + ~10 proje (web, mobil, veri,
    ML, devops, scrapy…). Backend / Mobile / Frontend / Data Science Intern
    ilanlarıyla eşleştir.
  - Can Öztürk: ~4 deneyim + ~8 proje (C#, Java, Python, mobil, veri, Go…).
    Full Stack (Python/React), .NET Backend, Java Backend ile ranking test et.
  - Mehmet / Zeynep / Elif: orta-üst zenginlikte uzun açıklamalar + ek projeler.

Şifre tüm hesaplar için: seedpass123
"""
import asyncio
import json
from datetime import date

from sqlalchemy import delete

from app.database import AsyncSessionLocal
from app.models import (
    Certificate,
    Document,
    EducationRecord,
    Exam,
    JobListing,
    Language,
    Match,
    Project,
    Reference,
    SocialLink,
    User,
    WorkExperience,
)
from app.services.auth import get_password_hash

USERS = [
    dict(
        email="junior.dev@example.com",
        full_name="Ayşe Yılmaz",
        target_position="Python Backend Developer Intern",
        seniority="junior",
        experience_years=1.0,
        skills=[
            "Python",
            "SQL",
            "Git",
            "REST API",
            "Flask",
            "FastAPI",
            "React",
            "React Native",
            "Flutter",
            "pandas",
            "scikit-learn",
            "Docker",
            "PostgreSQL",
            "TypeScript",
            "Node.js",
        ],
        experience_summary=(
            "Bilgisayar mühendisliği 4. sınıf öğrencisi; son iki yılda staj, "
            "öğrenci topluluğu, freelance ve açık kaynak katkılarıyla web API, "
            "mobil uygulama, veri analizi ve küçük ML prototipleri geliştirdi. "
            "Sürekli yeni teknolojiler deneyerek Flask, FastAPI, React, React "
            "Native, Flutter, pandas ve Docker arasında geçiş yapıyor. "
            "Öğrendiklerini GitHub'da dokümante edilmiş küçük ürünlere "
            "dönüştürmeyi ve staj başvurusunda ilana göre en alakalı "
            "deneyimleri öne çıkarmayı hedefliyor."
        ),
        tone_preference="professional",
        gender="Kadın",
        nationality="TC",
        driver_license="B",
        military_status=None,
        birth_year=2003,
        phone="+90 532 111 22 33",
        location="Erzincan / İstanbul",
        education=[
            dict(
                school="Erzincan Binali Yıldırım Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2021, 9, 1),
                end_date=None,
                description=(
                    "4. sınıf, mezuniyet 2026 Haziran. Veri yapıları, veritabanı "
                    "sistemleri, yazılım mühendisliği ve yapay zeka derslerinde "
                    "proje ağırlıklı çalıştı. Bitirme projesinde REST API + "
                    "basit öneri sistemi üzerine odaklanıyor. GPA 3.4/4.0; "
                    "bölüm içi algoritma yarışmalarında düzenli katılımcı."
                ),
            ),
        ],
        experiences=[
            dict(
                company="SoftBridge Teknoloji",
                title="Yazılım Stajyeri",
                start_date=date(2025, 6, 1),
                end_date=date(2025, 9, 1),
                description=(
                    "Yaz stajında Flask tabanlı dahili bir REST API'nin endpoint "
                    "tasarımına, doğrulama katmanına ve SQLite'dan PostgreSQL'e "
                    "geçişine katkı verdi. Postman koleksiyonları ve örnek "
                    "payload'lar hazırladı; basit JWT auth middleware'ini "
                    "mevcut servise entegre etti. Takımın GitHub PR sürecine "
                    "dahil olup lint ve birim test kurallarını öğrendi. Staj "
                    "sonunda küçük bir raporlama endpoint'ini tek başına "
                    "teslim etti; code review geri bildirimleriyle edge-case "
                    "testlerini ve hata mesajlarını iyileştirdi. Docker "
                    "Compose ile yerel geliştirme ortamını ayağa kaldırmayı "
                    "deneyimledi ve haftalık demo'larda ilerlemeyi sundu."
                ),
            ),
            dict(
                company="EBYÜ Yazılım ve Yapay Zeka Topluluğu",
                title="Proje Ekibi Üyesi / Workshop Asistanı",
                start_date=date(2023, 10, 1),
                end_date=date(2025, 5, 1),
                description=(
                    "Öğrenci topluluğunda haftalık hackathon, workshop ve "
                    "kodlama kulübü etkinliklerinin organizasyonuna katıldı. "
                    "Yeni üyelere Git, Python, temel web ve SQL kavramlarını "
                    "anlattı; canlı kodlama oturumlarında asistanlık yaptı. "
                    "Topluluk içi etkinlik kayıt sisteminin backend tarafında "
                    "çalıştı; kayıt, yoklama ve geri bildirim anketlerinin "
                    "verisini temizleyip pandas ile basit görselleştirmeler "
                    "üretti. Etkinlik sonrası retrospektif notlarını tutarak "
                    "bir sonraki dönem için iyileştirme önerileri hazırladı. "
                    "İletişim ve ekip çalışması becerilerini güçlendirdi."
                ),
            ),
            dict(
                company="Freelance / Yerel İşletmeler",
                title="Junior Geliştirici",
                start_date=date(2024, 1, 1),
                end_date=date(2025, 5, 1),
                description=(
                    "Yerel bir kafe ve küçük bir kırtasiye için menü, stok ve "
                    "sipariş takip ihtiyacını karşılayan web panelleri "
                    "geliştirdi. Müşteri gereksinimlerini yüz yüze toplayıp "
                    "basit bir ürün backlog'u ve wireframe çıkardı; React "
                    "arayüz ile Flask API'yi entegre etti. Teslim sonrası hata "
                    "düzeltmeleri, küçük özellik eklemeleri ve kullanıcı "
                    "eğitimi ile bakım desteği verdi. Ödeme alma veya karmaşık "
                    "muhasebe kapsam dışı bırakılarak bilinçli bir MVP "
                    "kapsamı tanımlandı. Bu süreçte kapsam yönetimi ve "
                    "müşteri iletişimi konusunda pratik kazandı."
                ),
            ),
            dict(
                company="Kodluyoruz / Açık Kaynak Katkıları",
                title="Gönüllü Katkımcı",
                start_date=date(2024, 3, 1),
                end_date=date(2024, 12, 1),
                description=(
                    "Öğrenci odaklı açık kaynak ve bootcamp projelerinde "
                    "dokümantasyon, bug fix ve küçük feature PR'ları açtı. "
                    "Issue triage sürecini izleyerek yeniden üretilebilir "
                    "hata raporları yazmayı öğrendi. CI'da kırılan testleri "
                    "inceleyip basit düzeltmeler önerdi. İngilizce README ve "
                    "contribution guide metinlerine katkı vererek teknik "
                    "yazım pratiği yaptı. Bu deneyim, profesyonel kod "
                    "tabanlarında işbirliği alışkanlığı kazandırdı."
                ),
            ),
            dict(
                company="Üniversite Bitirme Projesi (devam)",
                title="Backend Geliştirici (Öğrenci)",
                start_date=date(2025, 9, 1),
                end_date=None,
                description=(
                    "Bitirme projesinde kampüs içi kayıp-eşya ve eşleştirme "
                    "akışını destekleyen FastAPI tabanlı bir backend tasarlıyor. "
                    "PostgreSQL şeması, basit öneri skoru ve admin paneli "
                    "için API sözleşmesi üzerinde çalışıyor. Takım arkadaşlarıyla "
                    "haftalık sprint planlaması yapıyor; OpenAPI şeması ve "
                    "örnek isteklerle frontend entegrasyonunu kolaylaştırıyor. "
                    "Hedef, staj döneminde öğrendiği test ve Docker "
                    "pratiklerini akademik projeye taşımak."
                ),
            ),
        ],
        projects=[
            dict(
                title="Kütüphane Ödünç Takip API'si",
                description=(
                    "Flask + SQLite/PostgreSQL ile kitap ödünç/iade süreçlerini "
                    "yöneten REST API. JWT benzeri basit token auth, sayfalama, "
                    "rol bazlı erişim (öğrenci/kütüphaneci) ve gecikme cezası "
                    "hesabı ekledi. OpenAPI şeması, örnek istekler ve Postman "
                    "koleksiyonu ile dokümante etti; kritik akışlar için birim "
                    "ve entegrasyon testleri yazdı. Seed script ile örnek "
                    "veri yükleme sağladı. Proje, staj başvurusunda backend "
                    "deneyimini göstermek için GitHub'da yayınlandı ve README'de "
                    "kurulum adımları Türkçe/İngilizce anlatıldı."
                ),
                tech_stack=["Python", "Flask", "PostgreSQL", "SQL", "Git", "REST API"],
                url="https://github.com/example/library-api",
            ),
            dict(
                title="Kampüs Etkinlik Panosu",
                description=(
                    "React + TypeScript ile öğrencilerin kulüp etkinliklerini "
                    "filtreleyip favorileyebildiği bir frontend panosu. Tarih "
                    "aralığı, kategori ve arama barı; favoriler localStorage'da "
                    "saklanır. Backend olarak önce JSON-server, sonra Flask "
                    "proxy kullandı. Responsive düzeni mobil tarayıcılarda "
                    "test etti; erişilebilirlik için temel aria etiketleri "
                    "ekledi. Takım arkadaşlarıyla Figma üzerinden UI taslağı "
                    "üzerinde anlaştı ve component library benzeri küçük bir "
                    "buton/kart seti oluşturdu."
                ),
                tech_stack=["React", "TypeScript", "CSS", "Flask", "Figma"],
                url="https://github.com/example/campus-events",
            ),
            dict(
                title="Yemek Tarifi Mobil Uygulaması",
                description=(
                    "React Native (Expo) ile tarif listeleme, favorileme, "
                    "alışveriş listesi ve basit arama özellikli mobil uygulama "
                    "prototipi. AsyncStorage ile offline favoriler; REST "
                    "API'den tarif verisi çekimi. Pull-to-refresh, skeleton "
                    "loading ve hata ekranları eklendi. Android emülatörü ve "
                    "fiziksel cihazda test edildi. Amaç mobil geliştirme, "
                    "navigasyon ve state yönetimini pratik etmekti; backend "
                    "staj ilanlarında düşük öncelikli kalabilecek bir yan "
                    "projedir ancak Mobile Intern ilanında öne çıkması beklenir."
                ),
                tech_stack=["React Native", "Expo", "JavaScript", "AsyncStorage"],
                url="https://github.com/example/recipe-mobile",
            ),
            dict(
                title="Alışkanlık Takip Flutter Uygulaması",
                description=(
                    "Flutter ile günlük alışkanlık işaretleme, streak sayacı "
                    "ve basit istatistik ekranı içeren cross-platform mobil "
                    "uygulama. SharedPreferences ile yerel saklama; Provider "
                    "ile state yönetimi denendi. Material Design bileşenleri "
                    "ve koyu tema desteği eklendi. React Native deneyimini "
                    "Flutter ile karşılaştırmak için bilinçli olarak ikinci "
                    "bir mobil stack denemesi yapıldı. UI animasyonları ve "
                    "widget testleri kısmen tamamlandı."
                ),
                tech_stack=["Flutter", "Dart", "Provider"],
                url="https://github.com/example/habit-flutter",
            ),
            dict(
                title="Öğrenci Not Analiz Paneli",
                description=(
                    "pandas ve matplotlib ile anonimleştirilmiş ders notlarını "
                    "temizleyip dağılım, başarı oranı ve korelasyon grafikleri "
                    "üreten analiz scripti. Jupyter notebook'ta EDA yaptıktan "
                    "sonra sonuçları Streamlit benzeri basit bir HTML/Streamlit "
                    "rapora aktardı. Eksik veri doldurma, aykırı değer ayıklama "
                    "ve SQL ile ham veri çekme adımlarını dokümante etti. "
                    "Data Science / Data Engineer staj ilanlarında güçlü "
                    "eşleşen bir proje olarak tasarlandı."
                ),
                tech_stack=["Python", "pandas", "SQL", "matplotlib", "Streamlit"],
                url="https://github.com/example/grade-analytics",
            ),
            dict(
                title="Haber Başlığı Sınıflandırıcı",
                description=(
                    "scikit-learn ile Türkçe haber başlıklarını kategoriye "
                    "ayıran ML prototipi. TF-IDF vektörleştirme, Naive Bayes "
                    "ve lojistik regresyon modellerini karşılaştırdı; "
                    "doğruluk, F1 ve confusion matrix raporladı. Veri "
                    "artırma ve stop-word temizliği denendi. Üretim seviyesinde "
                    "olmayan, öğrenme odaklı bir projedir; ancak Data Science "
                    "ilanlarında NLP ilgisi göstermek için faydalıdır. "
                    "Sonuçlar notebook ve kısa sunum slaytıyla paylaşıldı."
                ),
                tech_stack=["Python", "scikit-learn", "pandas", "NLP"],
                url="https://github.com/example/news-classifier",
            ),
            dict(
                title="Fiyat Takip Scraperi",
                description=(
                    "Belirli e-ticaret sayfalarından ürün fiyatını periyodik "
                    "çeken BeautifulSoup + requests scripti. Sonuçları CSV/SQLite'a "
                    "yazıp fiyat düşüşünde konsol veya e-posta uyarısı verdi. "
                    "Rate limiting, User-Agent rotasyonu ve robots.txt kontrolü "
                    "ile kibarca tarama yapmayı öğrendi; yasal/etik sınırları "
                    "README'de not düştü. Backend staj ilanlarıyla doğrudan "
                    "ilgili olmayan keşif projesi; filtre/ranking'in düşük "
                    "alakalı projeyi elemesini test etmek için kasıtlı eklendi."
                ),
                tech_stack=["Python", "BeautifulSoup", "requests", "SQLite"],
                url="https://github.com/example/price-scraper",
            ),
            dict(
                title="Kişisel Blog + Markdown CMS",
                description=(
                    "Next.js benzeri basit bir yapı yerine Flask + Markdown "
                    "dosyalarıyla çalışan kişisel blog. Syntax highlighting, "
                    "etiket filtreleme ve RSS feed içerir. Statik dosya "
                    "servisi ve basit admin formu ile yeni yazı ekleme "
                    "denendi. Frontend Intern ve içerik odaklı roller için "
                    "yan portföy parçası; asıl odak yazı düzeni ve CSS "
                    "tipografisiydi. Deploy için Railway/Render denemeleri "
                    "yapıldı."
                ),
                tech_stack=["Python", "Flask", "Markdown", "CSS", "HTML"],
                url="https://github.com/example/markdown-blog",
            ),
            dict(
                title="Dockerize Todo API + CI",
                description=(
                    "FastAPI ile Todo CRUD API'sini Docker ve docker-compose "
                    "ile paketledi; GitHub Actions üzerinde lint + pytest "
                    "çalıştıran basit CI kurdu. Healthcheck, multi-stage "
                    "build ve .env örneği ekledi. Amaç DevOps temellerini "
                    "öğrenmek ve stajda gördüğü Compose kullanımını kendi "
                    "projesine taşımaktı. Backend Intern ilanlarında Docker "
                    "nice-to-have ile örtüşür."
                ),
                tech_stack=["Python", "FastAPI", "Docker", "GitHub Actions", "pytest"],
                url="https://github.com/example/todo-api-ci",
            ),
            dict(
                title="Node.js Chat Socket Prototipi",
                description=(
                    "Node.js + Socket.io ile oda bazlı basit gerçek zamanlı "
                    "sohbet prototipi. Express ile statik arayüz servis edildi; "
                    "bağlantı, odaya katılma ve mesaj yayınlama akışları "
                    "test edildi. Amaç JavaScript ekosisteminde backend "
                    "denemekti; üretim auth/güvenlik kapsam dışı. Python "
                    "odaklı ilanlarda düşük alakalı kalması beklenen, "
                    "çok alanlı öğrenci profilini yansıtan bir deneydir."
                ),
                tech_stack=["Node.js", "Socket.io", "Express", "JavaScript"],
                url="https://github.com/example/socket-chat",
            ),
        ],
        certificates=[
            dict(
                title="Python for Everybody Specialization",
                issuer="Coursera / University of Michigan",
                issue_date=date(2024, 3, 15),
                url="https://coursera.org/verify/example-py4e",
            ),
            dict(
                title="Google Data Analytics Professional Certificate",
                issuer="Coursera / Google",
                issue_date=date(2024, 11, 20),
                url="https://coursera.org/verify/example-gda",
            ),
            dict(
                title="Meta React Native Specialization (Courses 1-3)",
                issuer="Coursera / Meta",
                issue_date=date(2025, 2, 10),
                url="https://coursera.org/verify/example-rn",
            ),
            dict(
                title="Docker Essentials",
                issuer="IBM / Coursera",
                issue_date=date(2025, 4, 2),
                url="https://coursera.org/verify/example-docker",
            ),
        ],
        exams=[
            dict(
                name="YDS",
                score="78.75",
                exam_date=date(2024, 9, 8),
                description=(
                    "İngilizce; akademik okuma ve kelime bilgisinde yeterli seviye. "
                    "Teknik dokümantasyon okuma için kullanılıyor."
                ),
            ),
            dict(
                name="TOEFL iBT (Practice)",
                score="92",
                exam_date=date(2025, 1, 15),
                description=(
                    "Deneme sınavı; speaking ve writing bölümlerinde gelişim "
                    "hedefleniyor. Resmi sınav planlanıyor."
                ),
            ),
            dict(
                name="ALES",
                score="82.4",
                exam_date=date(2025, 4, 20),
                description="Sayısal ağırlıklı; lisansüstü başvuru için alındı.",
            ),
        ],
        languages=[
            dict(name="Türkçe", level="Ana dil"),
            dict(name="İngilizce", level="B2"),
            dict(name="Almanca", level="A2"),
        ],
        social_links=[
            dict(platform="LinkedIn", url="https://linkedin.com/in/ayse-yilmaz-example"),
            dict(platform="GitHub", url="https://github.com/ayseyilmaz-example"),
            dict(platform="Portfolio", url="https://ayseyilmaz.dev.example"),
            dict(platform="Medium", url="https://medium.com/@ayseyilmaz-example"),
        ],
        references=[
            dict(
                name="Doç. Dr. Selim Arslan",
                title="Öğretim Üyesi",
                company="EBYÜ Bilgisayar Mühendisliği",
                contact="selim.arslan@example.edu.tr",
                notes=(
                    "Bitirme projesi danışmanı; yazılım ve veri derslerinde "
                    "birlikte çalıştı. Akademik referans."
                ),
            ),
            dict(
                name="Melis Kara",
                title="Yazılım Takım Lideri",
                company="SoftBridge Teknoloji",
                contact="melis.kara@softbridge.example",
                notes="Yaz stajı boyunca doğrudan mentorluk yaptı.",
            ),
        ],
    ),
    dict(
        email="mid.dev@example.com",
        full_name="Mehmet Kaya",
        target_position="Java Backend Developer",
        seniority="mid",
        experience_years=2.5,
        skills=[
            "Java",
            "Spring Boot",
            "PostgreSQL",
            "Docker",
            "Kafka",
            "Redis",
            "Kubernetes",
            "Groovy",
            "Micrometer",
        ],
        experience_summary=(
            "2.5 yıldır fintech ortamında Java/Spring Boot mikroservisleri "
            "geliştiriyor. Ödeme, bildirim ve mutabakat akışlarında Kafka ile "
            "event-driven mimariye geçişte aktif rol aldı. Üretim ortamında "
            "gözlemlenebilirlik, idempotency ve güvenilirlik konularına "
            "odaklanıyor; junior ekip arkadaşlarına code review mentörlüğü "
            "yapıyor."
        ),
        tone_preference="confident",
        gender="Erkek",
        nationality="TC",
        driver_license="B",
        military_status="Yapıldı",
        birth_year=1997,
        phone="+90 533 444 55 66",
        location="İstanbul",
        education=[
            dict(
                school="Orta Doğu Teknik Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2015, 9, 1),
                end_date=date(2019, 6, 1),
                description=(
                    "Dağıtık sistemler ve veritabanı derslerinde yüksek performans "
                    "gösterdi. Bitirme projesinde mesaj kuyruklu bir sipariş "
                    "sistemi tasarladı; jüri değerlendirmesinde başarı belgesi aldı."
                ),
            ),
        ],
        experiences=[
            dict(
                company="FinTechCo",
                title="Java Backend Developer",
                start_date=date(2023, 3, 1),
                end_date=None,
                description=(
                    "Spring Boot mikroservislerinde ödeme mutabakatı, webhook "
                    "işleme ve merchant onboarding servislerini geliştirdi. "
                    "Kafka topic tasarımı, consumer idempotency, retry ve "
                    "dead-letter kuyrukları üzerinde çalıştı. PostgreSQL şema "
                    "migrasyonlarını Flyway ile yönetti; Docker üzerinde yerel "
                    "geliştirme ortamını standartlaştırdı. Micrometer + Grafana "
                    "ile latency ve hata oranı panoları kurdu. On-call "
                    "rotasyonunda üretim olaylarına müdahale etti; postmortem "
                    "notları yazdı. Sprint planlamasında story'leri parçalayıp "
                    "tahminlemeye katkı verdi."
                ),
            ),
            dict(
                company="PayLite",
                title="Junior Backend Developer",
                start_date=date(2021, 7, 1),
                end_date=date(2023, 2, 1),
                description=(
                    "REST API'ler üzerinden hesap, işlem sorgulama ve limit "
                    "yönetimi endpoint'leri yazdı. Redis ile sık kullanılan "
                    "sorguları önbelleğe aldı; cache invalidation stratejilerini "
                    "belirledi. Entegrasyon testlerini Testcontainers ile "
                    "genişletti. Kod review kültürüne uyum sağlayarak ekip "
                    "standartlarına ve checkstyle kurallarına katkı verdi. "
                    "Partner banka entegrasyonlarında sandbox ortamında "
                    "uçtan uca senaryolar koşturdu."
                ),
            ),
            dict(
                company="OMÜ / Staj (Bitirme öncesi)",
                title="Yazılım Stajyeri",
                start_date=date(2018, 6, 1),
                end_date=date(2018, 9, 1),
                description=(
                    "Kurumsal bir yazılım firmasında Java SE ve temel Spring "
                    "MVC ile dahili raporlama ekranlarına destek verdi. SQL "
                    "sorgularını optimize etti; JUnit ile ilk birim testlerini "
                    "yazdı. Profesyonel iş ortamı, ticket sistemi ve günlük "
                    "stand-up disiplinini ilk kez deneyimledi."
                ),
            ),
        ],
        projects=[
            dict(
                title="Ödeme Mikroservisi",
                description=(
                    "Spring Boot + Kafka ile asenkron ödeme işleme servisi. "
                    "Outbox pattern ile tutarlı event yayını; retry, circuit "
                    "breaker ve DLQ politikaları. PostgreSQL üzerinde işlem "
                    "durumu takibi ve audit log. Staging ortamında yük testi "
                    "senaryoları koşturarak p95 gecikme metriklerini raporladı. "
                    "OpenAPI dokümantasyonu ve contract testleri eklendi. "
                    "FinTechCo Java Backend ilanıyla yüksek örtüşme için "
                    "tasarlanmış referans projedir."
                ),
                tech_stack=["Java", "Spring Boot", "Kafka", "PostgreSQL", "Docker"],
                url="https://github.com/example/payment-service",
            ),
            dict(
                title="Bildirim Servisi",
                description=(
                    "Kullanıcı bildirimlerini e-posta, SMS ve push kanallarına "
                    "dağıtan Spring Boot servisi. Redis kuyruk ile yoğun "
                    "saatlerde throttle; şablon motoru ile kişiselleştirilmiş "
                    "içerik. Delivery status callback'lerini işleyerek "
                    "başarısız gönderimleri yeniden denedi. Multi-tenant "
                    "yapılandırma ve feature flag ile kademeli rollout destekledi."
                ),
                tech_stack=["Java", "Spring Boot", "Redis", "PostgreSQL"],
                url="https://github.com/example/notification-service",
            ),
            dict(
                title="Fraud Rule Engine (PoC)",
                description=(
                    "Basit kural motoru ile şüpheli işlemleri işaretleyen PoC. "
                    "Kurallar YAML'dan yüklenir; eşleşen işlemler audit "
                    "kuyruğuna yazılır. Groovy ile dinamik kural denemeleri "
                    "yapıldı. Amaç domain karmaşıklığını Java ekosisteminde "
                    "modellemekti; üretim ML modeli içermez. Review sürecinde "
                    "güvenlik ekibiyle tehdit modeli tartışıldı."
                ),
                tech_stack=["Java", "Spring Boot", "YAML", "PostgreSQL"],
                url="https://github.com/example/fraud-rules-poc",
            ),
            dict(
                title="Merchant Onboarding Portal API",
                description=(
                    "Merchant başvuru, doküman yükleme ve onay durumlarını "
                    "yöneten API. State machine ile başvuru yaşam döngüsü; "
                    "S3 uyumlu object storage entegrasyonu mock'landı. "
                    "Admin tarafı için arama/filtreleme ve export endpoint'leri "
                    "eklendi. Rol bazlı erişim ve audit trail zorunlu tutuldu."
                ),
                tech_stack=["Java", "Spring Boot", "PostgreSQL", "Redis"],
                url="https://github.com/example/merchant-onboarding",
            ),
            dict(
                title="Local Dev Stack (Compose)",
                description=(
                    "Ekip için Kafka, PostgreSQL, Redis ve birkaç Spring "
                    "servisini tek komutla ayağa kaldıran docker-compose "
                    "şablonu. Init script'leri, örnek .env ve troubleshooting "
                    "README içerir. Yeni katılan geliştiricilerin kurulum "
                    "süresini saatlerden dakikalara indirmeyi hedefledi."
                ),
                tech_stack=["Docker", "Kafka", "PostgreSQL", "Redis"],
                url="https://github.com/example/fintech-dev-stack",
            ),
        ],
        certificates=[
            dict(
                title="Spring Professional Certification",
                issuer="VMware",
                issue_date=date(2023, 9, 10),
                url="https://vmware.com/certify/example-spring",
            ),
            dict(
                title="Confluent Certified Developer for Apache Kafka",
                issuer="Confluent",
                issue_date=date(2024, 4, 18),
                url="https://confluent.io/certification/example-ccda",
            ),
            dict(
                title="Oracle Certified Professional: Java SE Developer",
                issuer="Oracle",
                issue_date=date(2022, 6, 1),
                url="https://education.oracle.com/example-java-se-mk",
            ),
        ],
        exams=[
            dict(
                name="YDS",
                score="85",
                exam_date=date(2022, 4, 3),
                description="İngilizce; teknik dokümantasyon ve toplantı dili seviyesi.",
            ),
            dict(
                name="TOEIC",
                score="870",
                exam_date=date(2023, 1, 10),
                description="İş İngilizcesi odaklı skor.",
            ),
        ],
        languages=[
            dict(name="Türkçe", level="Ana dil"),
            dict(name="İngilizce", level="C1"),
        ],
        social_links=[
            dict(platform="LinkedIn", url="https://linkedin.com/in/mehmet-kaya-example"),
            dict(platform="GitHub", url="https://github.com/mehmetkaya-example"),
            dict(platform="Stack Overflow", url="https://stackoverflow.com/users/example/mehmet"),
        ],
        references=[
            dict(
                name="Ayhan Demirtaş",
                title="Engineering Manager",
                company="FinTechCo",
                contact="ayhan.demirtas@fintechco.example",
                notes="Doğrudan yöneticisi; mikroservis ve Kafka projelerinde birlikte çalıştı.",
            ),
            dict(
                name="Gizem Aksoy",
                title="Staff Engineer",
                company="PayLite",
                contact="gizem.aksoy@paylite.example",
                notes="İlk backend rolünde teknik mentor.",
            ),
        ],
    ),
    dict(
        email="ai.engineer@example.com",
        full_name="Zeynep Demir",
        target_position="AI Engineer",
        seniority="senior",
        experience_years=4.0,
        skills=[
            "Python",
            "LLM",
            "Gemini API",
            "OpenAI API",
            "FastAPI",
            "Prompt Engineering",
            "LangChain",
            "RAG",
            "PyTorch",
            "Docker",
            "PostgreSQL",
            "Vector DB",
        ],
        experience_summary=(
            "4 yıl backend deneyiminin son 1.5 yılında LLM tabanlı agent "
            "sistemleri geliştirmeye odaklandı. Gemini/OpenAI function calling, "
            "prompt değerlendirme, RAG ve FastAPI ile üretim seviyesinde AI "
            "ürünleri çıkardı. Değerlendirme metrikleri, maliyet kontrolü ve "
            "güvenlik (prompt injection, PII) katmanlarına önem veriyor."
        ),
        tone_preference="professional",
        gender="Kadın",
        nationality="TC",
        driver_license="B",
        military_status=None,
        birth_year=1996,
        phone="+90 534 777 88 99",
        location="İstanbul",
        education=[
            dict(
                school="Boğaziçi Üniversitesi",
                degree="Yüksek Lisans",
                field_of_study="Yapay Zeka",
                start_date=date(2019, 9, 1),
                end_date=date(2021, 6, 1),
                description=(
                    "Doğal dil işleme ve pekiştirmeli öğrenme odaklı tez çalışması. "
                    "LLM fine-tuning ve evaluation konularında seminerler verdi. "
                    "Tezinde retrieval-augmented generation öncesi klasik IR "
                    "yöntemlerini karşılaştırdı."
                ),
            ),
            dict(
                school="Boğaziçi Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2015, 9, 1),
                end_date=date(2019, 6, 1),
                description=(
                    "Algoritma ve makine öğrenmesi derslerinde güçlü performans. "
                    "Öğrenci asistanlığı yaptı; lab oturumlarında Python ve "
                    "NumPy temelleri anlattı."
                ),
            ),
        ],
        experiences=[
            dict(
                company="NeuralWorks",
                title="AI Engineer",
                start_date=date(2024, 6, 1),
                end_date=None,
                description=(
                    "Gemini function calling ile multi-agent bir başvuru platformu "
                    "geliştirdi. İlan analizi, eşleştirme skoru, CV ve önyazı "
                    "üreten ajanları orkestre etti; tool calling hatalarında "
                    "retry ve fallback stratejileri tasarladı. Prompt sürümleme "
                    "ve regresyon testleriyle çıktı kalitesini ölçülebilir hale "
                    "getirdi. Token bütçesi, cache ve rate limit ile maliyet "
                    "kontrolü kurdu. FastAPI üzerinden üretim API'sini yayınladı; "
                    "güvenlik ekibiyle PII redaksiyonunu tartıştı."
                ),
            ),
            dict(
                company="ScaleUp Tech",
                title="Backend Developer → AI Platform",
                start_date=date(2021, 9, 1),
                end_date=date(2024, 5, 1),
                description=(
                    "FastAPI tabanlı müşteri servislerinde çalıştı; ardından AI "
                    "ürün ekibine geçiş yaptı. Embedding tabanlı arama ve basit "
                    "RAG prototiplerinde yer aldı. Observability için structured "
                    "logging ve latency dashboard'ları kurdu. Junior "
                    "geliştiricilere code review mentörlüğü yaptı. Model "
                    "çıktılarını A/B test etmek için feature flag altyapısına "
                    "entegrasyon sağladı."
                ),
            ),
            dict(
                company="Araştırma Laboratuvarı (Boğaziçi)",
                title="Araştırma Asistanı (yarı zamanlı)",
                start_date=date(2020, 2, 1),
                end_date=date(2021, 5, 1),
                description=(
                    "Yüksek lisans döneminde NLP laboratuvarında veri seti "
                    "hazırlama, baseline model eğitimi ve makale reproduksiyon "
                    "deneyleri yürüttü. GPU kuyruk yönetimi ve deney loglama "
                    "(Weights & Biases benzeri) süreçlerine katkı verdi. "
                    "Haftalık reading group sunumları yaptı."
                ),
            ),
        ],
        projects=[
            dict(
                title="Çok Ajanlı Başvuru Asistanı",
                description=(
                    "Gemini function calling ile ilan analizi, eşleştirme, CV ve "
                    "önyazı üreten agent sistemi. Her ajanın sorumluluğu net "
                    "ayrıldı; ortak context katmanı ile profil ve ilan verisi "
                    "paylaşıldı. Maliyet kontrolü için token bütçesi ve cache "
                    "katmanı eklendi. Demo ortamında uçtan uca başvuru akışını "
                    "çalıştıracak şekilde paketlendi. Eval seti ile ajan "
                    "çıktılarının tutarlılığı ölçülüyor."
                ),
                tech_stack=["Python", "Gemini API", "FastAPI", "LangChain"],
                url="https://github.com/example/multi-agent-assistant",
            ),
            dict(
                title="Prompt Değerlendirme Aracı",
                description=(
                    "Farklı prompt varyantlarının çıktı kalitesini otomatik "
                    "skorlayan araç. Rubrik tabanlı LLM-as-judge ve insan "
                    "etiketleriyle karşılaştırma yaptı. Sonuçları CSV ve "
                    "dashboard'a aktararak regresyonları erken yakalamayı "
                    "hedefledi. Ekip içi prompt review sürecine entegre edildi; "
                    "sürümler git'te tutuluyor."
                ),
                tech_stack=["Python", "LLM", "Prompt Engineering"],
                url="https://github.com/example/prompt-eval",
            ),
            dict(
                title="Şirket İçi RAG Doküman Asistanı",
                description=(
                    "İç wiki ve PDF'lerden chunk + embedding + retrieval yapan "
                    "RAG prototipi. Kaynak gösterimi (citation) ve yanıt "
                    "reddetme (insufficient context) politikaları eklendi. "
                    "Vector DB olarak pgvector denendi. Hassas dokümanlar için "
                    "erişim kontrolü mock'landı. Üretim öncesi güvenlik "
                    "incelemesinden geçirildi."
                ),
                tech_stack=["Python", "RAG", "PostgreSQL", "FastAPI", "OpenAI API"],
                url="https://github.com/example/internal-rag",
            ),
            dict(
                title="Fine-tune Classification Notebook",
                description=(
                    "Küçük bir metin sınıflandırma görevinde LoRA/PEFT benzeri "
                    "hafif fine-tune denemeleri. Veri temizleme, train/val split, "
                    "metrik takibi ve hata analizi notebook'ta belgelendi. "
                    "Amaç API tabanlı LLM'ler yerine özelleştirme seçeneklerini "
                    "keşfetmekti; GPU maliyeti nedeniyle küçük model kullanıldı."
                ),
                tech_stack=["Python", "PyTorch", "NLP", "pandas"],
                url="https://github.com/example/lora-classify",
            ),
            dict(
                title="LLM Cost Dashboard",
                description=(
                    "Provider bazlı token kullanımı, maliyet ve p95 latency "
                    "metriklerini toplayan iç araç. FastAPI + basit React "
                    "panosu; günlük bütçe aşımında alert. AI/ML Engineer "
                    "ilanlarında operasyonel olgunluk göstergesi olarak "
                    "kullanılabilir."
                ),
                tech_stack=["Python", "FastAPI", "React", "PostgreSQL"],
                url="https://github.com/example/llm-cost-dash",
            ),
        ],
        certificates=[
            dict(
                title="DeepLearning.AI Generative AI with LLMs",
                issuer="Coursera / DeepLearning.AI",
                issue_date=date(2024, 2, 28),
                url="https://coursera.org/verify/example-genai",
            ),
            dict(
                title="LangChain for LLM Application Development",
                issuer="DeepLearning.AI",
                issue_date=date(2024, 6, 12),
                url="https://learn.deeplearning.ai/example-langchain",
            ),
        ],
        exams=[
            dict(
                name="IELTS Academic",
                score="7.5",
                exam_date=date(2023, 11, 12),
                description="Overall band 7.5; akademik yazma ve dinleme güçlü.",
            ),
        ],
        languages=[
            dict(name="Türkçe", level="Ana dil"),
            dict(name="İngilizce", level="C1"),
            dict(name="Fransızca", level="B1"),
        ],
        social_links=[
            dict(platform="LinkedIn", url="https://linkedin.com/in/zeynep-demir-example"),
            dict(platform="GitHub", url="https://github.com/zeynepdemir-example"),
            dict(platform="Hugging Face", url="https://huggingface.co/zeynepdemir-example"),
            dict(platform="Twitter", url="https://x.com/zeynepdemir_ai_example"),
        ],
        references=[],
    ),
    dict(
        email="fullstack.multi@example.com",
        full_name="Can Öztürk",
        target_position="Full Stack Developer",
        seniority="mid",
        experience_years=3.5,
        skills=[
            "C#",
            "Java",
            "Python",
            "React",
            "SQL Server",
            "PostgreSQL",
            "Flutter",
            "pandas",
            "Docker",
            "Go",
            "TypeScript",
            "AWS",
        ],
        experience_summary=(
            "3.5 yıl boyunca farklı şirketlerde C#, Java, Python ve kısmen Go "
            "yığınlarıyla full stack projeler geliştirdi. React frontend, "
            "kurumsal .NET, Spring servisleri, FastAPI dashboard'ları ve "
            "mobil yan projeler arasında geçiş yaparak ilan gereksinimlerine "
            "göre en alakalı deneyimini öne çıkarabilecek geniş bir portföy "
            "oluşturdu. CV ajanının proje seçimi ve metin rewrite "
            "davranışlarını test etmek için kasıtlı olarak çok dilli / çok "
            "alanlı bir profil tutuldu."
        ),
        tone_preference="confident",
        gender="Erkek",
        nationality="TC",
        driver_license="B",
        military_status="Muaf",
        birth_year=1998,
        phone="+90 535 222 33 44",
        location="Ankara",
        education=[
            dict(
                school="Yıldız Teknik Üniversitesi",
                degree="Lisans",
                field_of_study="Yazılım Mühendisliği",
                start_date=date(2016, 9, 1),
                end_date=date(2021, 6, 1),
                description=(
                    "Yazılım mimarisi, mobil uygulama ve veritabanı derslerinde "
                    "proje üretti. Mezuniyet projesi çok katmanlı bir stok "
                    "yönetim sistemiydi; jüri tarafından öne çıkarıldı."
                ),
            ),
        ],
        experiences=[
            dict(
                company="Kodçu Yazılım",
                title="Full Stack Developer",
                start_date=date(2022, 1, 1),
                end_date=None,
                description=(
                    "React frontend ile C#, Java ve Python backend'lerinin "
                    "birlikte yaşadığı müşteri projelerinde çalıştı. Ortak "
                    "auth ve API gateway katmanlarını iyileştirdi; CI/CD "
                    "pipeline'larına unit test ve lint adımları ekledi. "
                    "Müşteri demo'larında gereksinimleri toplayıp sprint "
                    "planlamasına katkı verdi. Kod kalitesi için review "
                    "checklist'leri oluşturdu. Performans sorunlarında "
                    "SQL plan analizi ve N+1 sorgularını giderdi. Junior "
                    "geliştiricilere pair programming yaptı."
                ),
            ),
            dict(
                company="NovaSoft",
                title="Junior Full Stack Developer",
                start_date=date(2021, 6, 1),
                end_date=date(2021, 12, 31),
                description=(
                    "ASP.NET Core ile dahili CRM modüllerine CRUD ekranları "
                    "ekledi. SQL Server sorgularını optimize etti; React "
                    "formlarında validasyon ve hata gösterimini iyileştirdi. "
                    "İlk yılında Agile süreçlere uyum sağlayarak story "
                    "tahminleme toplantılarına katıldı. Azure DevOps "
                    "board'larında iş takibi yaptı; release notları yazdı."
                ),
            ),
            dict(
                company="StartupHub (sözleşmeli)",
                title="Full Stack Danışman (yarı zamanlı)",
                start_date=date(2023, 3, 1),
                end_date=date(2023, 9, 1),
                description=(
                    "Erken aşama bir startup'a MVP için FastAPI + React "
                    "iskeleti kurdu. Auth, temel CRUD ve admin paneli "
                    "teslim etti; deploy için Docker ve basit CI ekledi. "
                    "Kurucu ekibe teknik borç ve sonraki sprint önerileri "
                    "bıraktı. Kısa süreli ama yoğun bir ürün odaklı "
                    "deneyimdi."
                ),
            ),
            dict(
                company="YTÜ Teknoloji Transfer (öğrenci projesi dönemi)",
                title="Öğrenci Geliştirici",
                start_date=date(2020, 2, 1),
                end_date=date(2021, 5, 1),
                description=(
                    "Üniversite-sanayi işbirliği kapsamında küçük bir "
                    "endüstriyel IoT dashboard prototipine katkı verdi. "
                    "Veri toplama API'si ve React grafik ekranları yazdı. "
                    "Donanım ekibiyle seri protokol mock'ları üzerinde "
                    "anlaştı. Mezuniyet sonrası referans olarak kullanıldı."
                ),
            ),
        ],
        projects=[
            dict(
                title="Stok Yönetim Sistemi",
                description=(
                    "ASP.NET Core + SQL Server ile kurumsal stok yönetim "
                    "uygulaması. Depo giriş/çıkış, barkod okuma entegrasyonu "
                    "ve rol bazlı yetkilendirme içerir. Entity Framework ile "
                    "migrasyonlar yönetildi; ayrı React SPA kullanıldı. "
                    "Raporlama ekranlarında günlük hareket özetleri sunuldu; "
                    "müşteri UAT sürecinde kritik hatalar kapatıldı. .NET "
                    "Backend ilanlarında birincil eşleşen proje olarak "
                    "tasarlandı. Audit log ve soft-delete politikaları eklendi."
                ),
                tech_stack=["C#", "ASP.NET Core", "SQL Server", "React", "Entity Framework"],
                url="https://github.com/example/inventory-dotnet",
            ),
            dict(
                title="Sipariş Takip Servisi",
                description=(
                    "Spring Boot ile mikroservis mimarili sipariş takip API'si. "
                    "Sipariş durumu makinesi, PostgreSQL persistence ve "
                    "OpenAPI dokümantasyonu içerir. Docker Compose ile yerel "
                    "ortam ayağa kaldırıldı; entegrasyon testleri ile mutlu "
                    "yol ve hata senaryoları doğrulandı. Java Backend "
                    "ilanlarında öne çıkması beklenen referans projedir. "
                    "Outbox ile event yayını PoC seviyesinde denendi."
                ),
                tech_stack=["Java", "Spring Boot", "PostgreSQL", "Docker"],
                url="https://github.com/example/order-tracking-java",
            ),
            dict(
                title="Veri Analiz Panosu",
                description=(
                    "FastAPI + React ile satış verilerini görselleştiren "
                    "dashboard. CSV yükleme, filtreleme ve grafik bileşenleri "
                    "sunar; backend'de pandas ile aggregasyon yapılır. "
                    "PostgreSQL'e yazılan özet tabloları ile tekrarlı "
                    "sorgular hızlandırıldı. Python/React Full Stack "
                    "ilanlarında birincil eşleşen proje olarak tasarlandı. "
                    "Auth ve rol bazlı rapor erişimi eklendi."
                ),
                tech_stack=["Python", "FastAPI", "React", "PostgreSQL", "pandas"],
                url="https://github.com/example/sales-dashboard-python",
            ),
            dict(
                title="Saha Servis Mobil Uygulaması",
                description=(
                    "Flutter ile saha ekiplerinin iş emri alıp fotoğraf "
                    "yükleyebildiği mobil uygulama. Offline-first taslak "
                    "akışları ve basit senkronizasyon kuyruğu içerir. REST "
                    "API'ye bağlanır; harita üzerinde yakındaki işleri "
                    "gösterir. Full stack web ilanlarında düşük öncelikli "
                    "kalması beklenen mobil yan projedir; ranking/filtre "
                    "testi için kasıtlı çeşitlilik sağlar."
                ),
                tech_stack=["Flutter", "Dart", "REST API"],
                url="https://github.com/example/field-service-flutter",
            ),
            dict(
                title="Müşteri Churn Tahmin Notebook'u",
                description=(
                    "pandas ve scikit-learn ile abonelik churn tahmini yapan "
                    "keşifsel veri bilimi çalışması. Feature engineering, "
                    "train/test split ve ROC-AUC karşılaştırması içerir. "
                    "Sonuçlar iş birimine kısa bir sunumla aktarıldı; "
                    "üretim pipeline'ına taşınmadı. Çok alanlı portföyü "
                    "göstermek ve Data odaklı ilanlarda yan sinyal vermek "
                    "için eklendi."
                ),
                tech_stack=["Python", "pandas", "scikit-learn"],
                url="https://github.com/example/churn-notebook",
            ),
            dict(
                title="Gateway Rate Limiter (Go)",
                description=(
                    "Go ile yazılmış basit API gateway rate limiter PoC. "
                    "Token bucket algoritması, Redis backend ve Prometheus "
                    "metrikleri. Amaç Go'yu öğrenmek ve yüksek trafikli "
                    "kenar servislerini denemekti. Python/C#/Java odaklı "
                    "ilanlarda düşük alakalı kalması beklenir; max-3 proje "
                    "elemesi için iyi bir adaydır."
                ),
                tech_stack=["Go", "Redis", "Prometheus"],
                url="https://github.com/example/go-rate-limiter",
            ),
            dict(
                title="E-Ticaret Admin Paneli",
                description=(
                    "TypeScript + React ile ürün, sipariş ve kupon yönetimi "
                    "yapan admin paneli. Tablo sanallaştırma, gelişmiş filtre "
                    "ve CSV export içerir. Backend olarak mock ve ardından "
                    "FastAPI bağlandı. UI/UX tutarlılığı için ortak form "
                    "bileşenleri çıkarıldı. Full Stack ilanlarında frontend "
                    "gücünü destekler."
                ),
                tech_stack=["TypeScript", "React", "FastAPI", "CSS"],
                url="https://github.com/example/ecommerce-admin",
            ),
            dict(
                title="AWS Serverless Image Resizer",
                description=(
                    "S3 upload tetiklemeli Lambda ile görsel yeniden "
                    "boyutlandırma PoC. CloudWatch logları ve basit IAM "
                    "politikası dokümante edildi. Bulut deneyimini göstermek "
                    "için eklendi; ana stack değil. Maliyet kontrolü için "
                    "concurrency limit denendi."
                ),
                tech_stack=["AWS", "Lambda", "S3", "Python"],
                url="https://github.com/example/s3-image-resizer",
            ),
        ],
        certificates=[
            dict(
                title="Microsoft Certified: Azure Developer Associate",
                issuer="Microsoft",
                issue_date=date(2023, 6, 5),
                url="https://learn.microsoft.com/credentials/example-az204",
            ),
            dict(
                title="Oracle Certified Professional: Java SE Developer",
                issuer="Oracle",
                issue_date=date(2022, 10, 14),
                url="https://education.oracle.com/example-java-se",
            ),
            dict(
                title="AWS Certified Cloud Practitioner",
                issuer="Amazon Web Services",
                issue_date=date(2024, 1, 22),
                url="https://aws.amazon.com/verification/example-clf",
            ),
        ],
        exams=[
            dict(
                name="YDS",
                score="82.5",
                exam_date=date(2021, 9, 5),
                description="İngilizce; teknik iletişim için yeterli seviye.",
            ),
            dict(
                name="TOEFL iBT",
                score="98",
                exam_date=date(2022, 5, 14),
                description="Uluslararası müşteri toplantıları için alındı.",
            ),
        ],
        languages=[
            dict(name="Türkçe", level="Ana dil"),
            dict(name="İngilizce", level="B2"),
            dict(name="İspanyolca", level="A1"),
        ],
        social_links=[
            dict(platform="LinkedIn", url="https://linkedin.com/in/can-ozturk-example"),
            dict(platform="GitHub", url="https://github.com/canozturk-example"),
            dict(platform="Portfolio", url="https://canozturk.dev.example"),
            dict(platform="Dev.to", url="https://dev.to/canozturk-example"),
        ],
        references=[
            dict(
                name="Burak Yılmaz",
                title="Tech Lead",
                company="Kodçu Yazılım",
                contact="burak.yilmaz@kodcu.example",
                notes="Full stack ekip lideri; React ve çoklu backend projelerinde mentor.",
            ),
            dict(
                name="Prof. Dr. Nilgün Kara",
                title="Öğretim Üyesi",
                company="YTÜ Yazılım Mühendisliği",
                contact="nilgun.kara@example.edu.tr",
                notes="Mezuniyet projesi danışmanı.",
            ),
        ],
    ),
    dict(
        email="senior.dev@example.com",
        full_name="Elif Aydın",
        target_position="Senior Backend Engineer",
        seniority="senior",
        experience_years=5.0,
        skills=[
            "Python",
            "FastAPI",
            "Kubernetes",
            "AWS",
            "System Design",
            "PostgreSQL",
            "Terraform",
            "gRPC",
            "Redis",
            "Kafka",
        ],
        experience_summary=(
            "5 yıl kıdemli backend mühendisi olarak mikroservis mimarileri "
            "kurdu ve ölçeklendirdi. AWS üzerinde Kubernetes ile çalışan "
            "platformlarda güvenilirlik, maliyet ve geliştirici deneyimini "
            "dengelemeye odaklanıyor. Teknik liderlik, mentörlük ve "
            "incident response süreçlerinde deneyimli."
        ),
        tone_preference="professional",
        gender="Kadın",
        nationality="TC",
        driver_license=None,
        military_status=None,
        birth_year=1994,
        phone="+90 536 999 00 11",
        location="İstanbul",
        education=[
            dict(
                school="İstanbul Teknik Üniversitesi",
                degree="Lisans",
                field_of_study="Bilgisayar Mühendisliği",
                start_date=date(2012, 9, 1),
                end_date=date(2016, 6, 1),
                description=(
                    "Dağıtık sistemler ve işletim sistemleri derslerinde güçlü "
                    "temel. Mezuniyet sonrası hemen endüstriye geçti; sonraki "
                    "yıllarda platform mühendisliğine yöneldi."
                ),
            ),
        ],
        experiences=[
            dict(
                company="ScaleUp Tech",
                title="Senior Backend Engineer",
                start_date=date(2020, 4, 1),
                end_date=None,
                description=(
                    "AWS üzerinde Kubernetes ile ölçeklenen mikroservis "
                    "mimarisini tasarladı ve ekibe mentörlük yaptı. Service "
                    "mesh, HPA ve canary deploy stratejilerini hayata "
                    "geçirdi. Incident response runbook'ları yazdı; SLO "
                    "tanımları ve error budget süreçlerini kurdu. FastAPI "
                    "servislerinin performansını profiling ile iyileştirdi. "
                    "Hiring sürecinde teknik mülakatlar yaptı; onboarding "
                    "dokümanlarını yeniledi."
                ),
            ),
            dict(
                company="CloudBase",
                title="Backend Engineer",
                start_date=date(2017, 8, 1),
                end_date=date(2020, 3, 1),
                description=(
                    "Python tabanlı API'lerde yüksek trafikli okuma "
                    "yollarını optimize etti. PostgreSQL indeksleme ve "
                    "read-replica stratejileri uyguladı. CI pipeline'larına "
                    "güvenlik tarama adımları ekledi; on-call sürecine "
                    "katılarak üretim stabilitesine katkı verdi. Redis "
                    "cache katmanı ve rate limiting ile abuse'u azalttı."
                ),
            ),
            dict(
                company="StartupForge",
                title="Software Engineer",
                start_date=date(2016, 7, 1),
                end_date=date(2017, 7, 1),
                description=(
                    "Erken aşama üründe monolit Python API ve temel admin "
                    "panel geliştirdi. Müşteri geri bildirimlerine göre hızlı "
                    "iterasyon yaptı; teknik borcu yönetmek için refactor "
                    "haftaları önerdi. İlk üretim deploy ve monitoring "
                    "deneyimini burada kazandı."
                ),
            ),
        ],
        projects=[
            dict(
                title="Mikroservis Altyapı Geçişi",
                description=(
                    "Monolitik sistemi Kubernetes tabanlı mikroservislere "
                    "taşıyan dönüşüm projesi. Domain sınırlarını belirleyip "
                    "aşamalı cutover planı çıkardı; blue/green deploy ile "
                    "riski azalttı. Observability için Prometheus/Grafana "
                    "dashboard'ları ve merkezi log toplama kurdu. Geçiş "
                    "sonrası p95 latency ve hata oranlarında ölçülebilir "
                    "iyileşme sağlandı. Senior Backend ilanlarıyla yüksek "
                    "örtüşme için ana referans projedir."
                ),
                tech_stack=["Python", "Kubernetes", "AWS", "FastAPI", "PostgreSQL"],
                url="https://github.com/example/microservices-migration",
            ),
            dict(
                title="Platform Developer Portal",
                description=(
                    "İç geliştiricilerin servis şablonu, secret ve ortam "
                    "yönetimini self-service yapabildiği portal. Terraform "
                    "modülleri ve Helm chart'ları ile standart iskelet üretir. "
                    "Onboarding süresini haftalardan günlere indirmeyi "
                    "hedefledi. RBAC ve audit log zorunlu tutuldu."
                ),
                tech_stack=["Python", "Kubernetes", "AWS", "Terraform"],
                url="https://github.com/example/dev-portal",
            ),
            dict(
                title="Event Backbone (Kafka)",
                description=(
                    "Şirket içi domain event'lerini standardize eden Kafka "
                    "altyapısı. Schema registry, consumer lag alert'leri ve "
                    "replay prosedürleri tanımlandı. Servis ekiplerine "
                    "örnek producer/consumer kütüphanesi sağlandı. "
                    "Güvenilir asenkron iletişim için kritik platform "
                    "parçası haline geldi."
                ),
                tech_stack=["Kafka", "Python", "Kubernetes", "AWS"],
                url="https://github.com/example/event-backbone",
            ),
            dict(
                title="gRPC Internal API Kit",
                description=(
                    "Servisler arası gRPC sözleşmeleri, codegen ve "
                    "interceptor (auth, tracing) kit'i. Proto breaking "
                    "change kontrolü CI'ya eklendi. REST'ten gRPC'ye "
                    "kademeli geçişte ekiplere rehberlik etti. Latency "
                    "hassas iç çağrılarda p99 iyileşmesi ölçüldü."
                ),
                tech_stack=["gRPC", "Python", "Protobuf", "Kubernetes"],
                url="https://github.com/example/grpc-api-kit",
            ),
            dict(
                title="Cost Guard Rails",
                description=(
                    "AWS maliyet anomalilerini tespit eden ve bütçe aşımında "
                    "ticket açan otomasyon. Tag politikaları ve idle resource "
                    "raporları içerir. FinOps ekibiyle ortak tanımlandı; "
                    "aylık tasarruf raporları üretildi."
                ),
                tech_stack=["AWS", "Python", "Terraform"],
                url="https://github.com/example/cost-guard",
            ),
        ],
        certificates=[
            dict(
                title="AWS Certified Solutions Architect - Professional",
                issuer="Amazon Web Services",
                issue_date=date(2022, 11, 1),
                url="https://aws.amazon.com/verification/example-saa-p",
            ),
            dict(
                title="Certified Kubernetes Administrator (CKA)",
                issuer="The Linux Foundation",
                issue_date=date(2021, 5, 20),
                url="https://training.linuxfoundation.org/certification/verify/example-cka",
            ),
            dict(
                title="HashiCorp Certified: Terraform Associate",
                issuer="HashiCorp",
                issue_date=date(2023, 3, 8),
                url="https://hashicorp.com/certification/example-terraform",
            ),
        ],
        exams=[
            dict(
                name="TOEFL iBT",
                score="105",
                exam_date=date(2020, 3, 20),
                description="Uluslararası ekip iletişimi için yeterli İngilizce seviyesi.",
            ),
            dict(
                name="YDS",
                score="90",
                exam_date=date(2019, 9, 8),
                description="Akademik / teknik İngilizce.",
            ),
        ],
        languages=[
            dict(name="Türkçe", level="Ana dil"),
            dict(name="İngilizce", level="C1"),
        ],
        social_links=[
            dict(platform="LinkedIn", url="https://linkedin.com/in/elif-aydin-example"),
            dict(platform="GitHub", url="https://github.com/elifaydin-example"),
            dict(platform="Speaker Deck", url="https://speakerdeck.com/elifaydin-example"),
        ],
        references=[
            dict(
                name="Cem Özkan",
                title="VP of Engineering",
                company="ScaleUp Tech",
                contact="cem.ozkan@scaleup.example",
                notes="Platform dönüşümü ve Kubernetes geçişinde birlikte çalıştı.",
            ),
            dict(
                name="Deniz Uçar",
                title="Principal Engineer",
                company="CloudBase",
                contact="deniz.ucar@cloudbase.example",
                notes="Backend Engineer döneminde teknik mentor ve referans.",
            ),
        ],
    ),
]

LISTINGS = [
    dict(
        title="Backend Developer Intern",
        company="TechNova",
        owner_email="junior.dev@example.com",
        raw_text=(
            "TechNova olarak yaz dönemi Backend Developer stajyeri arıyoruz. "
            "Takımımız Python ile küçük ve orta ölçekli REST API'ler geliştiriyor; "
            "ürünümüz eğitim kurumlarına yönelik dahili araçlar sunuyor.\n\n"
            "Stajyerden temel SQL bilgisi, Git kullanımı, temiz kod alışkanlığı "
            "ve öğrenmeye açıklık bekliyoruz. Staj süresince mevcut Flask/FastAPI "
            "servislerine endpoint ekleyecek, birim test yazacak, Postman "
            "koleksiyonlarını güncelleyecek ve code review sürecine "
            "katılacaksınız. Docker Compose ile yerel ortamı ayağa kaldırmayı "
            "öğreneceksiniz.\n\n"
            "Tercihen REST API tasarımı, FastAPI/Flask veya PostgreSQL deneyimi "
            "olan; üniversite 3. veya 4. sınıf öğrencilerini değerlendiriyoruz. "
            "Mobil veya veri bilimi yan projeleri artı olabilir ancak bu rolde "
            "öncelik backend API geliştirmedir. Hibrit / ofis içi seçenekleri "
            "mevcuttur; mentor eşliğinde 10-12 haftalık program."
        ),
        required_skills=["Python", "SQL", "Git"],
        nice_to_have_skills=["REST API", "FastAPI", "Flask", "Docker", "PostgreSQL"],
        seniority="junior",
    ),
    dict(
        title="Java Backend Developer",
        company="FinTechCo",
        owner_email="mid.dev@example.com",
        raw_text=(
            "FinTechCo bünyesinde Java Backend Developer pozisyonu için "
            "deneyimli geliştirici arıyoruz. Ödeme, mutabakat ve bildirim "
            "gibi kritik akışlarda çalışacak ekibe katılacaksınız.\n\n"
            "Zorunlu nitelikler: Java, Spring Boot ve PostgreSQL. Kafka ve "
            "Docker deneyimi güçlü artıdır. 2-4 yıl backend deneyimi "
            "bekleniyor. Mikroservis mimarisi, event-driven tasarım, "
            "idempotency ve üretim ortamı gözlemlenebilirliği konularında "
            "rahat olan adayları önceliklendiriyoruz.\n\n"
            "Sorumluluklar arasında yeni servis geliştirme, mevcut "
            "servislerin performans iyileştirmesi, on-call rotasyonu ve "
            "junior mentörlüğü yer alır. Hibrit çalışma modeli sunuyoruz; "
            "finansal regülasyonlara uygun güvenlik bilinci aranır."
        ),
        required_skills=["Java", "Spring Boot", "PostgreSQL"],
        nice_to_have_skills=["Kafka", "Docker", "Redis", "Kubernetes"],
        seniority="mid",
    ),
    dict(
        title="Full Stack Developer",
        company="Kodçu Yazılım",
        owner_email="fullstack.multi@example.com",
        raw_text=(
            "Kodçu Yazılım olarak Full Stack Developer arıyoruz. Zorunlu "
            "yığın: Python (tercihen FastAPI), React ve PostgreSQL. Müşteri "
            "dashboard'ları, veri görselleştirme ekranları ve admin "
            "panelleri geliştireceksiniz.\n\n"
            "Docker ve CI/CD deneyimi tercih sebebidir. 1-3 yıl deneyim "
            "bekleniyor. Hem API tasarımı hem de modern React bileşen "
            "yapısında rahat olan, iletişim becerisi yüksek adaylar "
            "aranmaktadır.\n\n"
            "C# veya Java geçmişi artı olabilir ancak bu rolde Python/React "
            "önceliklidir. Müşteri demolarına katılım ve gereksinim "
            "netleştirme sürecinde aktif rol beklenir. Uzaktan ağırlıklı "
            "hibrit model."
        ),
        required_skills=["Python", "React", "PostgreSQL"],
        nice_to_have_skills=["Docker", "CI/CD", "FastAPI", "TypeScript"],
        seniority="mid",
    ),
    dict(
        title="Senior Backend Engineer",
        company="ScaleUp Tech",
        owner_email="senior.dev@example.com",
        raw_text=(
            "ScaleUp Tech, kıdemli backend mühendisi arıyor. Zorunlu: Python, "
            "Kubernetes, sistem tasarımı deneyimi ve AWS. Mikroservis "
            "mimarisinde ölçeklenebilir servisler tasarlayıp ekibe liderlik "
            "edecek profil bekliyoruz.\n\n"
            "5+ yıl deneyim, SLO odaklı çalışma, mentörlük ve incident "
            "response deneyimi önemlidir. Canary deploy, observability, "
            "maliyet optimizasyonu ve platform developer experience "
            "konularında pratik tecrübe aranır.\n\n"
            "Teknik mülakatlara katılım, RFC yazımı ve cross-team "
            "koordinasyon sorumlulukları arasındadır. Uzaktan / hibrit "
            "seçenekleri mevcuttur."
        ),
        required_skills=["Python", "Kubernetes", "sistem tasarımı", "AWS"],
        nice_to_have_skills=["mikroservis mimarisi", "FastAPI", "Terraform", "Kafka"],
        seniority="senior",
    ),
    dict(
        title="Data Engineer Intern",
        company="DataFlow",
        owner_email="junior.dev@example.com",
        raw_text=(
            "DataFlow olarak Veri Mühendisliği stajyeri arıyoruz. Zorunlu: "
            "Python ve SQL. Ham veriyi temizleyip pipeline'lara taşıma, "
            "basit ETL scriptleri yazma ve veri kalitesi kontrolleri "
            "yapma konularında destek bekliyoruz.\n\n"
            "Airflow veya Spark bilgisi tercih sebebidir. pandas ile EDA "
            "yapabilen, veri sözlüğü ve dokümantasyona önem veren "
            "öğrencileri değerlendiriyoruz.\n\n"
            "Staj boyunca anonimleştirilmiş gerçek veri setleriyle "
            "çalışacak, haftalık demo'larda bulgularınızı sunacaksınız. "
            "Yaz dönemi tam zamanlı staj; mentor eşliğinde 8-10 hafta."
        ),
        required_skills=["Python", "SQL"],
        nice_to_have_skills=["Airflow", "Spark", "pandas", "Docker"],
        seniority="junior",
    ),
    dict(
        title="AI/ML Engineer",
        company="NeuralWorks",
        owner_email="ai.engineer@example.com",
        raw_text=(
            "NeuralWorks, yapay zeka mühendisi arıyor. Zorunlu: Python, LLM "
            "API deneyimi (Gemini veya OpenAI) ve FastAPI. Agent "
            "orkestrasyonu, prompt engineering ve RAG konularında pratik "
            "tecrübe tercih sebebidir.\n\n"
            "2+ yıl deneyim bekleniyor. Üretim ortamında LLM çağrılarını "
            "maliyet, gecikme ve güvenlik açısından yönetebilen; "
            "değerlendirme (eval) süreçleri kurabilen adaylar öncelikli.\n\n"
            "Araştırma geçmişi, PyTorch deneyimi ve vector DB bilgisi "
            "artıdır. Ürün ekibiyle yakın çalışarak özellikleri hızlı "
            "deneyimlemeyi seviyoruz."
        ),
        required_skills=["Python", "LLM API", "FastAPI"],
        nice_to_have_skills=["agent orkestrasyonu", "prompt engineering", "RAG", "LangChain"],
        seniority="mid",
    ),
    dict(
        title="Mobile App Intern",
        company="AppForge",
        owner_email="junior.dev@example.com",
        raw_text=(
            "AppForge olarak Mobile App stajyeri arıyoruz. Zorunlu: React "
            "Native veya Flutter ile temel mobil uygulama deneyimi, "
            "JavaScript veya Dart bilgisi ve Git kullanımı.\n\n"
            "Stajyer, mevcut bir tarif/alışveriş listesi tarzı uygulamaya "
            "ekran ekleyecek, API entegrasyonu yapacak ve Expo veya "
            "emülatör üzerinde test edecek. Offline storage (AsyncStorage "
            "vb.), navigasyon ve basit state yönetimi bilen adaylar "
            "tercih edilir.\n\n"
            "UI tutarlılığı, hata durumları ve performans (liste "
            "sanallaştırma) konularında öğrenmeye açık üniversite "
            "öğrencilerine açığız. Portföyde en az bir yayınlanabilir "
            "mobil proje görmek istiyoruz."
        ),
        required_skills=["React Native", "JavaScript", "Git"],
        nice_to_have_skills=["Flutter", "Expo", "AsyncStorage", "TypeScript"],
        seniority="junior",
    ),
    dict(
        title="Frontend Intern",
        company="PixelLab",
        owner_email="junior.dev@example.com",
        raw_text=(
            "PixelLab, Frontend stajyeri arıyor. Zorunlu: React, JavaScript "
            "ve temel CSS/HTML. Bileşen tabanlı arayüz geliştirme, "
            "responsive tasarım ve API'den veri çekme konularında pratik "
            "yapmanızı bekliyoruz.\n\n"
            "TypeScript, erişilebilirlik ve Figma'dan UI aktarımı tercih "
            "sebebidir. Portföyünde en az bir React projesi olan, "
            "öğrenmeye açık 3-4. sınıf öğrencilerini değerlendiriyoruz.\n\n"
            "Staj süresince tasarım sistemi bileşenlerine katkı, storybook "
            "benzeri dokümantasyon ve code review alışkanlığı "
            "kazandırılacaktır. Backend bilgisi artıdır ancak zorunlu değildir."
        ),
        required_skills=["React", "JavaScript", "CSS"],
        nice_to_have_skills=["TypeScript", "Figma", "REST API", "HTML"],
        seniority="junior",
    ),
    dict(
        title="Data Science Intern",
        company="InsightLabs",
        owner_email="junior.dev@example.com",
        raw_text=(
            "InsightLabs olarak Data Science stajyeri arıyoruz. Zorunlu: "
            "Python, pandas ve SQL. Keşifsel veri analizi, basit "
            "sınıflandırma modelleri ve sonuçların görselleştirilmesi "
            "üzerinde çalışacaksınız.\n\n"
            "scikit-learn, matplotlib veya Jupyter deneyimi artıdır. "
            "İstatistik temeli olan, notebook'larını temiz ve tekrar "
            "çalıştırılabilir tutan öğrenciler tercih edilir.\n\n"
            "Staj boyunca gerçek (anonimleştirilmiş) veri setleriyle "
            "pratik yapılacak; bulgularınızı iş birimine sunmanız "
            "beklenir. NLP veya scrapy yan projeleri ilgi çekicidir ancak "
            "temel odak EDA ve klasik ML'dir."
        ),
        required_skills=["Python", "pandas", "SQL"],
        nice_to_have_skills=["scikit-learn", "matplotlib", "NLP", "Jupyter"],
        seniority="junior",
    ),
    dict(
        title=".NET Backend Developer",
        company="NovaSoft",
        owner_email="fullstack.multi@example.com",
        raw_text=(
            "NovaSoft, .NET Backend Developer arıyor. Zorunlu: C#, ASP.NET "
            "Core ve SQL Server. Kurumsal stok, CRM ve raporlama "
            "modüllerinde yeni özellik geliştirecek, Entity Framework "
            "ile veri erişim katmanını sürdüreceksiniz.\n\n"
            "React ile frontend entegrasyonu bilmek artıdır. 2+ yıl "
            "deneyim bekleniyor. Clean architecture, unit test ve Azure "
            "temelleri tercih sebebidir.\n\n"
            "Java veya Python geçmişi olan ancak .NET'e geçiş yapmak "
            "isteyen adaylar da değerlendirilebilir; bu rolde C#/.NET "
            "önceliklidir. Kod review, teknik dokümantasyon ve müşteri "
            "UAT desteği sorumluluklar arasındadır."
        ),
        required_skills=["C#", "ASP.NET Core", "SQL Server"],
        nice_to_have_skills=["React", "Entity Framework", "Azure", "Docker"],
        seniority="mid",
    ),
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Eski veriyi temizle (bağımlılık sırasına göre)
        await session.execute(delete(Document))
        await session.execute(delete(Match))
        await session.execute(delete(Project))
        await session.execute(delete(WorkExperience))
        await session.execute(delete(EducationRecord))
        await session.execute(delete(Certificate))
        await session.execute(delete(Exam))
        await session.execute(delete(Language))
        await session.execute(delete(SocialLink))
        await session.execute(delete(Reference))
        await session.execute(delete(JobListing))
        await session.execute(delete(User))
        await session.commit()

        users = []
        for u in USERS:
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=get_password_hash("seedpass123"),
                target_position=u["target_position"],
                seniority=u["seniority"],
                experience_years=u["experience_years"],
                skills=json.dumps(u["skills"], ensure_ascii=False),
                experience_summary=u["experience_summary"],
                tone_preference=u["tone_preference"],
                gender=u.get("gender"),
                nationality=u.get("nationality"),
                driver_license=u.get("driver_license"),
                military_status=u.get("military_status"),
                birth_year=u.get("birth_year"),
                phone=u.get("phone"),
                location=u.get("location"),
            )
            session.add(user)
            users.append(user)
        await session.commit()

        for u, user in zip(USERS, users):
            for edu in u.get("education") or []:
                session.add(
                    EducationRecord(
                        user_id=user.id,
                        school=edu["school"],
                        degree=edu.get("degree"),
                        field_of_study=edu.get("field_of_study"),
                        start_date=edu.get("start_date"),
                        end_date=edu.get("end_date"),
                        description=edu.get("description"),
                    )
                )
            for exp in u.get("experiences") or []:
                session.add(
                    WorkExperience(
                        user_id=user.id,
                        company=exp["company"],
                        title=exp["title"],
                        start_date=exp.get("start_date"),
                        end_date=exp.get("end_date"),
                        description=exp.get("description"),
                    )
                )
            for proj in u.get("projects") or []:
                session.add(
                    Project(
                        user_id=user.id,
                        title=proj["title"],
                        description=proj.get("description"),
                        tech_stack=json.dumps(
                            proj.get("tech_stack") or [], ensure_ascii=False
                        ),
                        url=proj.get("url"),
                    )
                )
            for cert in u.get("certificates") or []:
                session.add(
                    Certificate(
                        user_id=user.id,
                        title=cert["title"],
                        issuer=cert.get("issuer"),
                        issue_date=cert.get("issue_date"),
                        url=cert.get("url"),
                    )
                )
            for exam in u.get("exams") or []:
                session.add(
                    Exam(
                        user_id=user.id,
                        name=exam["name"],
                        score=exam.get("score"),
                        exam_date=exam.get("exam_date"),
                        description=exam.get("description"),
                    )
                )
            for lang in u.get("languages") or []:
                session.add(
                    Language(
                        user_id=user.id,
                        name=lang["name"],
                        level=lang.get("level"),
                    )
                )
            for link in u.get("social_links") or []:
                session.add(
                    SocialLink(
                        user_id=user.id,
                        platform=link["platform"],
                        url=link["url"],
                    )
                )
            for ref in u.get("references") or []:
                session.add(
                    Reference(
                        user_id=user.id,
                        name=ref["name"],
                        title=ref.get("title"),
                        company=ref.get("company"),
                        contact=ref.get("contact"),
                        notes=ref.get("notes"),
                    )
                )
        await session.commit()

        # US-040 sonrası sahipsiz ilan hiçbir akışta kullanılamıyor - her seed
        # ilanı, profili o ilana en uygun seed kullanıcısına atanır ki demo
        # kullanıcıları giriş yapınca "İlanlarım"da hazır ilan bulup match/CV/
        # önyazı akışını deneyebilsin. required_skills/nice_to_have_skills önceden
        # dolduruluyor ve analysis_status="completed" veriliyor - "pending" bir
        # ilanda calculate_exact_score boş required_skills'i "kriter yok, tam
        # puan" sayıp yanıltıcı yüksek skor üretiyordu (ör. eşleşen/eksik beceri
        # listeleri boşken %90 uygunluk); /api/match artık analiz tamamlanmamış
        # ilanlarda 422 döndürüyor, bu yüzden seed ilanları gerçekten analiz
        # edilmiş gibi gelmeli.
        users_by_email = {u.email: u for u in users}
        listings = []
        for listing_data in LISTINGS:
            owner = users_by_email[listing_data["owner_email"]]
            listing = JobListing(
                created_by=owner.id,
                title=listing_data["title"],
                company=listing_data["company"],
                raw_text=listing_data["raw_text"],
                required_skills=json.dumps(
                    listing_data["required_skills"], ensure_ascii=False
                ),
                nice_to_have_skills=json.dumps(
                    listing_data["nice_to_have_skills"], ensure_ascii=False
                ),
                seniority=listing_data["seniority"],
                analysis_status="completed",
                cv_template=listing_data.get("cv_template", "Version1"),
            )
            session.add(listing)
            listings.append(listing)

        await session.commit()

        # Demo eşleştirme + doküman kayıtları (US-010 borcu: matches/documents seed)
        demo_match = Match(
            user_id=users[0].id,
            listing_id=listings[0].id,
            score=72.5,
            matched_skills=json.dumps(["python", "sql", "git"], ensure_ascii=False),
            missing_skills=json.dumps(["docker"], ensure_ascii=False),
        )
        demo_doc = Document(
            user_id=users[0].id,
            listing_id=listings[0].id,
            doc_type="cover_letter",
            cover_letter_text=(
                "Sayın Yetkili, ilanınızda aradığınız Python ve SQL becerilerine "
                "üniversite projelerimde ve SoftBridge stajımda edindiğim deneyimle "
                "sahibim. Flask ile REST API geliştirdim, Git ve code review "
                "süreçlerine alışkınım... (demo verisi)"
            ),
        )
        session.add_all([demo_match, demo_doc])
        await session.commit()

        total_experiences = sum(len(u.get("experiences") or []) for u in USERS)
        total_projects = sum(len(u.get("projects") or []) for u in USERS)
        total_education = sum(len(u.get("education") or []) for u in USERS)
        total_certificates = sum(len(u.get("certificates") or []) for u in USERS)
        total_exams = sum(len(u.get("exams") or []) for u in USERS)
        total_languages = sum(len(u.get("languages") or []) for u in USERS)
        total_social = sum(len(u.get("social_links") or []) for u in USERS)
        total_refs = sum(len(u.get("references") or []) for u in USERS)
        print(
            f"Seeded {len(users)} users, {len(listings)} listings, 1 matches, "
            f"1 documents, {total_experiences} experiences, {total_projects} projects, "
            f"{total_education} education, {total_certificates} certificates, "
            f"{total_exams} exams, {total_languages} languages, "
            f"{total_social} social_links, {total_refs} references"
        )
        for u in users:
            print(f"  - {u.email} ({u.seniority}, {u.target_position})")


if __name__ == "__main__":
    asyncio.run(seed())
