import Link from "next/link";
import { AppHeader } from "@/components/layout/AppHeader";
import { AuthAwareLink } from "@/components/common/AuthAwareLink";

export default function Home() {
  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />

      <main className="max-w-container-max mx-auto px-margin-mobile md:px-lg py-16">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-headline-lg md:text-[48px] md:leading-[56px] font-bold text-on-surface">
            Yapay Zeka Destekli Kariyer Platformu
          </h1>
          <p className="mt-4 text-body-lg text-on-surface-variant">
            CareerTrack ile profilinizi oluşturun, iş ilanlarını analiz edin ve başvurularınızı
            profesyonelce yönetin.
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
