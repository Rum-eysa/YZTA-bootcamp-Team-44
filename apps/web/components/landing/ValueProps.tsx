import Link from "next/link";
import { ClipboardList, GraduationCap, Languages, FileText, ArrowRight } from "lucide-react";

const PROPS = [
  {
    icon: GraduationCap,
    title: "Öğrenciler ve sık başvuran adaylar için",
    description:
      "CareerTrack, staj ve iş ararken sürekli farklı ilanlara başvuran adaylar için tasarlandı. Her başvuru için aynı CV’yi kopyalamak yerine süreci tek yerden yönetirsiniz.",
  },
  {
    icon: FileText,
    title: "İlana özel CV ve önyazı",
    description:
      "İş ilanını ekleyin; AI profilinizle eşleştirerek ATS uyumlu CV ve önyazıyı o pozisyona göre kolayca oluştursun.",
  },
  {
    icon: ClipboardList,
    title: "Başvuruları kolayca takip edin",
    description:
      "Hangi şirkete ne gönderdiğinizi, eşleşme skorlarınızı ve belgelerinizi tek panelden izleyin; hiçbir başvuruyu kaybetmeyin.",
  },
  {
    icon: Languages,
    title: "Türkçe ve İngilizce",
    description:
      "Belgelerinizi ihtiyacınıza göre Türkçe veya İngilizce üretebilirsiniz; çok dilli başvuru süreçlerinde esnek kalın.",
  },
];

export function ValueProps() {
  return (
    <section className="mt-20 md:mt-24">
      <div className="relative mb-12 overflow-hidden rounded-2xl border border-outline-variant bg-surface-container-lowest px-6 py-10 md:px-10 md:py-14 shadow-card">
        <div
          aria-hidden
          className="absolute -right-8 top-1/2 h-56 w-56 -translate-y-1/2 rounded-full bg-primary-container/35 blur-3xl md:h-72 md:w-72"
        />
        <div
          aria-hidden
          className="absolute -right-20 bottom-0 h-40 w-40 rounded-full bg-secondary-container/45 blur-3xl"
        />
        <div className="relative text-center">
          <h2 className="text-headline-lg md:text-[40px] md:leading-[48px] font-bold text-on-surface">
            Neden CareerTrack?
          </h2>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
        {PROPS.map(({ icon: Icon, title, description }, index) => (
          <div
            key={title}
            className="relative overflow-hidden rounded-xl border border-outline-variant bg-surface-container-lowest p-6 shadow-card transition-shadow hover:shadow-card-hover"
          >
            <div
              aria-hidden
              className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-primary-container/20 blur-2xl"
            />
            <div className="relative flex gap-4">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-primary text-on-primary">
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-label-md font-semibold text-on-surface-variant">
                  0{index + 1}
                </p>
                <h3 className="mt-0.5 text-title-md font-semibold text-on-surface">{title}</h3>
                <p className="mt-2 text-body-sm text-on-surface-variant">{description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="relative mt-14 overflow-hidden rounded-2xl border border-outline-variant/30 bg-inverse-surface px-6 py-10 md:px-12 md:py-14 text-inverse-on-surface shadow-card-hover">
        <div
          aria-hidden
          className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_rgba(0,108,73,0.35),_transparent_60%)]"
        />
        <div
          aria-hidden
          className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-primary/30 blur-3xl"
        />
        <div
          aria-hidden
          className="absolute -left-12 bottom-[-20%] h-48 w-48 rounded-full bg-primary-container/20 blur-3xl"
        />
        <div className="relative max-w-2xl">
          <h3 className="text-headline-lg-mobile md:text-[36px] md:leading-[44px] font-bold">
            Hazır mısınız? CareerTrack&rsquo;e katılın
          </h3>
          <p className="mt-3 text-body-sm md:text-body-lg text-inverse-on-surface/75 max-w-lg">
            Profilinizi oluşturun, ilan ekleyin ve her başvuruya özel ATS uyumlu CV ile
            önyazı üretmeye başlayın.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-lg bg-primary-container px-6 py-2.5 font-semibold text-on-primary-container hover:opacity-90 transition-opacity"
            >
              Ücretsiz kayıt ol
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center rounded-lg border border-inverse-on-surface/30 px-6 py-2.5 font-semibold text-inverse-on-surface hover:bg-inverse-on-surface/10 transition-colors"
            >
              Giriş yap
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
