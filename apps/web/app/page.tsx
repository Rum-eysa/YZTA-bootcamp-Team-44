import Link from "next/link";
import { FileCheck2, ListChecks, Sparkles, Target } from "lucide-react";
import { AppHeader } from "@/components/layout/AppHeader";
import { AuthAwareLink } from "@/components/common/AuthAwareLink";

const DIFFERENTIATORS = [
  {
    icon: Target,
    title: "AI Eşleşme Skoru",
    description:
      "Profilinizi her ilana karşı otomatik puanlar: zorunlu beceriler, nice-to-have'ler ve seviye uyumu tek bir skorda birleşir, eksik becerileriniz somut olarak gösterilir.",
  },
  {
    icon: FileCheck2,
    title: "İlana Özel ATS CV & Önyazı",
    description:
      "Genel şablon değil — her başvuru için o ilana özel, ATS uyumlu LaTeX CV ve şirkete/pozisyona referans veren önyazı AI tarafından saniyeler içinde üretilir.",
  },
  {
    icon: ListChecks,
    title: "Başvuru Takibi",
    description:
      "Tüm başvurularınızı, eşleşme skorlarını ve oluşturulan belgeleri tek panelden izleyin; hangi ilana ne gönderdiğinizi asla kaybetmeyin.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />

      <main className="max-w-container-max mx-auto px-margin-mobile md:px-lg py-16">
        <div className="text-center max-w-3xl mx-auto">
          <span className="inline-flex items-center gap-1.5 text-body-sm font-semibold text-primary bg-primary-container/40 px-3 py-1 rounded-full">
            <Sparkles className="w-4 h-4" />
            AI Agent Pipeline
          </span>
          <h1 className="mt-4 text-headline-lg md:text-[48px] md:leading-[56px] font-bold text-on-surface">
            Her başvuruya özel CV ve önyazıyı AI sizin için hazırlasın
          </h1>
          <p className="mt-4 text-body-lg text-on-surface-variant">
            CareerTrack, klasik &ldquo;tek CV&rsquo;yi her yere gönder&rdquo; yaklaşımı yerine her
            iş ilanını AI ajanlarıyla analiz eder. Profilinizle ilan arasındaki uyumu skorlar,
            eksiklerinizi gösterir ve o ilana özel ATS uyumlu CV ile önyazıyı otomatik üretir. Siz
            sadece başvurunuzu takip edin — geri kalanını AI pipeline&rsquo;ımız yönetsin.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <AuthAwareLink href="/apply" className="btn-primary px-8 py-3 text-lg">
              İlan Ekle
            </AuthAwareLink>
            <AuthAwareLink href="/profile" className="btn-outline px-8 py-3 text-lg">
              Profilimi Düzenle
            </AuthAwareLink>
          </div>
        </div>

        <div className="mt-16">
          <h2 className="text-center text-title-lg font-bold text-on-surface">
            Neden CareerTrack?
          </h2>
          <p className="mt-2 text-center text-body-sm text-on-surface-variant max-w-2xl mx-auto">
            Başvuru sürecinizin her adımını tek bir AI destekli akışta birleştiriyoruz.
          </p>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-8">
            {DIFFERENTIATORS.map(({ icon: Icon, title, description }) => (
              <div key={title} className="card">
                <div className="w-10 h-10 rounded-lg bg-primary-container/40 flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="text-title-md font-semibold mb-2 text-primary">{title}</h3>
                <p className="text-body-sm text-on-surface-variant">{description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="card">
            <h3 className="text-title-md font-semibold mb-2 text-primary">Profil Yönetimi</h3>
            <p className="text-body-sm text-on-surface-variant">
              Ad, e-posta, bio, beceriler ve ton tercihinizi kaydedin. AI ajanları profilinizi
              hafızada tutar.
            </p>
            <AuthAwareLink
              href="/profile"
              className="inline-block mt-4 text-primary text-body-sm font-semibold hover:underline"
            >
              Profile git →
            </AuthAwareLink>
          </div>

          <div className="card">
            <h3 className="text-title-md font-semibold mb-2 text-primary">İlan Ekleme</h3>
            <p className="text-body-sm text-on-surface-variant">
              Şirket ve pozisyon bilgilerini girin, ilan metnini ekleyin ve AI analizini başlatın.
            </p>
            <AuthAwareLink
              href="/apply"
              className="inline-block mt-4 text-primary text-body-sm font-semibold hover:underline"
            >
              İlan ekle →
            </AuthAwareLink>
          </div>

          <div className="card">
            <h3 className="text-title-md font-semibold mb-2 text-primary">Güvenli Sistem</h3>
            <p className="text-body-sm text-on-surface-variant">
              JWT tabanlı kimlik doğrulama ve modern güvenlik önlemleri ile verileriniz güvende.
            </p>
            <Link
              href="/register"
              className="inline-block mt-4 text-primary text-body-sm font-semibold hover:underline"
            >
              Kayıt ol →
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
