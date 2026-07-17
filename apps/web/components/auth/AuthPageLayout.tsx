import { AppHeader } from "@/components/layout/AppHeader";
import { CheckCircle2, FileText, Sparkles, Target } from "lucide-react";
import type { ReactNode } from "react";

interface AuthPageLayoutProps {
  children: ReactNode;
}

function AuthPromo() {
  return (
    <section className="relative overflow-hidden bg-inverse-surface p-8 text-inverse-on-surface md:p-10">
      <div
        aria-hidden="true"
        className="absolute -right-20 -top-20 h-56 w-56 rounded-full bg-primary/40 blur-3xl"
      />
      <div className="relative">
        <span className="inline-flex items-center gap-2 rounded-full border border-inverse-on-surface/20 bg-inverse-on-surface/10 px-3 py-1 text-label-md">
          <Sparkles className="h-4 w-4 text-inverse-primary" />
          AI destekli kariyer asistanı
        </span>
        <h1 className="mt-6 text-headline-lg font-semibold">
          Başvurunuzu tek bir akışta güçlendirin
        </h1>
        <p className="mt-3 max-w-md text-body-lg text-inverse-on-surface/75">
          Profilinizi kullanarak ilanı analiz edin, eşleşme skorunuzu görün ve ilana özel
          belgelerinizi oluşturun.
        </p>

        <div className="mt-8 grid gap-3">
          <div className="flex items-center gap-3 rounded-xl bg-inverse-on-surface/10 p-3">
            <Target className="h-5 w-5 shrink-0 text-inverse-primary" />
            <span className="text-body-sm">Profil ve ilan arasında gerçek eşleşme analizi</span>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-inverse-on-surface/10 p-3">
            <FileText className="h-5 w-5 shrink-0 text-inverse-primary" />
            <span className="text-body-sm">İlana özel CV ve önyazı oluşturma</span>
          </div>
          <div className="flex items-center gap-3 rounded-xl bg-inverse-on-surface/10 p-3">
            <CheckCircle2 className="h-5 w-5 shrink-0 text-inverse-primary" />
            <span className="text-body-sm">Başvuruları tek panelden takip etme</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export function AuthPageLayout({ children }: AuthPageLayoutProps) {
  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />
      <main className="relative overflow-hidden px-margin-mobile py-xl md:py-2xl">
        <div
          aria-hidden="true"
          className="absolute -left-24 top-8 h-64 w-64 rounded-full bg-primary-fixed/30 blur-3xl"
        />
        <div
          aria-hidden="true"
          className="absolute -right-24 bottom-0 h-72 w-72 rounded-full bg-secondary-container/50 blur-3xl"
        />

        <div className="relative mx-auto grid max-w-[960px] overflow-hidden rounded-2xl border border-outline-variant bg-surface-container-lowest shadow-card-hover lg:grid-cols-[1.05fr_0.95fr]">
          <AuthPromo />
          <section className="p-6 md:p-10">{children}</section>
        </div>
      </main>
    </div>
  );
}
