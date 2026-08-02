import Link from "next/link";

export function AppFooter() {
  return (
    <footer className="bg-surface-container-lowest border-t border-outline-variant py-6 px-margin-mobile md:px-lg">
      <div className="max-w-container-max mx-auto flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="text-center md:text-left">
          <p className="text-body-sm text-on-surface-variant">
            CareerTrack — Kişisel verileriniz yalnızca hizmetin sağlanması ve size doğru deneyim sunulması için işlenir.
          </p>
        </div>
        <div className="flex flex-col items-center gap-2 md:flex-row md:items-center md:gap-4">
          <Link
            href="/kvkk"
            className="text-body-sm text-primary font-semibold hover:underline"
          >
            KVKK Aydınlatma Metni
          </Link>
          <Link
            href="/"
            className="text-body-sm text-on-surface-variant hover:text-primary transition-colors"
          >
            Ana Sayfa
          </Link>
        </div>
      </div>
    </footer>
  );
}
