import Link from "next/link";

export const metadata = {
  title: "KVKK Aydınlatma Metni | CareerTrack",
  description: "CareerTrack kişisel veri aydınlatma metni; hangi veriler işlendiği, amaç ve saklama açıklaması.",
};

export default function KvkkPage() {
  return (
    <div className="px-margin-mobile md:px-lg py-12 md:py-16">
      <div className="max-w-container-max mx-auto">
        <div className="mb-8">
          <p className="text-label-lg font-semibold text-primary">KVKK Aydınlatma Metni</p>
          <h1 className="mt-4 text-headline-lg text-on-surface font-bold">
            Kişisel Verilerinizin İşlenme Amacı ve Saklama Süresi
          </h1>
        </div>

        <div className="space-y-6 text-body-md text-on-surface-variant">
          <p>
            CareerTrack olarak kişisel verilerinizi aşağıdaki amaçlarla işleriz. Bu sayfa hukuki danışmanlık
            yerine geçmez ve sadece uygulamamızın veri kullanımını kısa ve anlaşılır biçimde açıklar.
          </p>

          <div className="rounded-3xl border border-outline-variant bg-surface-container-lowest p-6">
            <h2 className="text-title-lg font-semibold text-on-surface">İşlenen Veri Kategorileri</h2>
            <ul className="mt-4 space-y-3 list-disc pl-5 text-body-md">
              <li>Hesap bilgileri: e-posta, ad, soyad ve kimlik doğrulama verileri.</li>
              <li>Profil bilgileri: deneyim, eğitim, beceriler, hedef pozisyon, telefon, konum, avatar ve kişisel tercihler.</li>
              <li>İlan metni ve analiz bilgileri: kullanıcı tarafından girilen iş ilanı içeriği, analiz sonuçları ve eşleşme verisi.</li>
              <li>Üretilen belgeler: oluşturulan CV ve ön yazı içerikleri ve onların depolama bağlantıları.</li>
              <li>Kullanım verisi: oturum, erişim ve servis kullanım kayıtları.</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-outline-variant bg-surface-container-lowest p-6">
            <h2 className="text-title-lg font-semibold text-on-surface">Amaç</h2>
            <ul className="mt-4 space-y-3 list-disc pl-5 text-body-md">
              <li>Hizmet sağlamak: hesap yönetimi, profil düzenleme ve iş ilanı analizi.</li>
              <li>Eşleştirme: ilan ve profil uyumluluğunu değerlendirmek ve CV/ön yazı üretimi için gerekli veriyi hazırlamak.</li>
              <li>Kullanıcı deneyimi: profil tercihleri, belge dili ve şablon ayarları gibi kişiselleştirmeleri desteklemek.</li>
              <li>Güvenlik ve destek: platformun düzgün çalışmasını izlemek, sorunları çözmek ve kötüye kullanımı önlemek.</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-outline-variant bg-surface-container-lowest p-6">
            <h2 className="text-title-lg font-semibold text-on-surface">Saklama ve Erişim</h2>
            <p className="text-body-md leading-relaxed">
              Veriler, platformu kullanım süreniz boyunca hizmete erişiminiz için saklanır. Üretilen belgeler ve
              analiz sonuçları, kullanıcı tarafından silinene veya hesabınız kapatılana kadar erişilebilir
              durumda tutulur. Yetkili teknik ekip ve servis altyapısı sadece uygulamanın çalışması ve veri güvenliği
              için bu bilgilere erişir.
            </p>
          </div>

          <div className="rounded-3xl border border-outline-variant bg-surface-container-lowest p-6">
            <p className="text-body-md text-on-surface-variant">
              Bu sayfa, CareerTrack hizmeti kapsamında işlenen kişisel verilerin kısa özetini sağlar. Daha fazla bilgi
              için uygulama içi iletişim kanallarını kullanabilirsiniz.
            </p>
          </div>

          <div className="pt-4 border-t border-outline-variant">
            <Link href="/" className="text-primary font-semibold hover:underline">
              Ana Sayfaya Dön
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
