"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { login, saveTokens } from "@/lib/api/auth";
import { useAuth } from "@/hooks/useAuth";
import { zodResolver } from "@hookform/resolvers/zod";
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
      <main className="max-w-md mx-auto px-margin-mobile py-xl">
        <div className="card">
          <h1 className="text-headline-lg-mobile font-semibold text-on-surface mb-2">Giriş Yap</h1>
          <p className="text-body-sm text-on-surface-variant mb-6">
            Profilinizi düzenlemek için giriş yapın.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <FormError message={apiError} />
            <Input
              label="E-posta"
              type="email"
              error={errors.email?.message}
              {...register("email")}
            />
            <Input
              label="Şifre"
              type="password"
              error={errors.password?.message}
              {...register("password")}
            />
            <Button type="submit" loading={isSubmitting} className="w-full">
              Giriş Yap
            </Button>
          </form>

          <p className="mt-4 text-body-sm text-on-surface-variant text-center">
            Hesabınız yok mu?{" "}
            <Link href="/register" className="text-primary hover:underline">
              Kayıt olun
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
