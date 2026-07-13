"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { login, saveTokens } from "@/lib/api/auth";
import { useAuth } from "@/hooks/useAuth";
import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, FileText, Sparkles, Target } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email("Geçerli bir e-posta adresi giriniz"),
  password: z.string().min(1, "Şifre zorunludur"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginForm() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/profile";
  const [apiError, setApiError] = useState<string>();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setApiError(undefined);
    try {
      const tokens = await login(data.email, data.password);
      saveTokens(tokens);
      await refreshUser();
      router.push(redirect);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.";
      setApiError(typeof message === "string" ? message : "Giriş başarısız.");
    }
  };

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

          <section className="p-6 md:p-10">
            <h2 className="text-headline-lg-mobile font-semibold text-on-surface mb-2">
              Giriş Yap
            </h2>
            <p className="text-body-sm text-on-surface-variant mb-6">
              CareerTrack hesabınızla devam edin.
            </p>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <FormError message={apiError} />
              <Input
                label="E-posta"
                type="email"
                autoComplete="email"
                error={errors.email?.message}
                {...register("email")}
              />
              <Input
                label="Şifre"
                type="password"
                autoComplete="current-password"
                error={errors.password?.message}
                {...register("password")}
              />
              <Button type="submit" loading={isSubmitting} className="w-full py-3">
                Giriş Yap
              </Button>
            </form>

            <p className="mt-5 text-body-sm text-on-surface-variant text-center">
              Hesabınız yok mu?{" "}
              <Link href="/register" className="font-semibold text-primary hover:underline">
                Kayıt olun
              </Link>
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
