"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { login, register as registerUser, saveTokens } from "@/lib/api/auth";
import { useAuth } from "@/hooks/useAuth";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const registerSchema = z.object({
  full_name: z.string().min(1, "Ad zorunludur"),
  email: z.string().email("Geçerli bir e-posta adresi giriniz"),
  password: z.string().min(8, "Şifre en az 8 karakter olmalıdır"),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [apiError, setApiError] = useState<string>();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setApiError(undefined);
    try {
      await registerUser(data);
      const tokens = await login(data.email, data.password);
      saveTokens(tokens);
      await refreshUser();
      router.push("/profile");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.";
      setApiError(typeof message === "string" ? message : "Kayıt başarısız.");
    }
  };

  return (
    <div className="min-h-screen bg-surface-bright">
      <AppHeader />
      <main className="max-w-md mx-auto px-margin-mobile py-xl">
        <div className="card">
          <h1 className="text-headline-lg-mobile font-semibold text-on-surface mb-2">Kayıt Ol</h1>
          <p className="text-body-sm text-on-surface-variant mb-6">
            CareerTrack hesabı oluşturun ve profilinizi tamamlayın.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <FormError message={apiError} />
            <Input
              label="Ad Soyad"
              error={errors.full_name?.message}
              {...register("full_name")}
            />
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
              Kayıt Ol
            </Button>
          </form>

          <p className="mt-4 text-body-sm text-on-surface-variant text-center">
            Zaten hesabınız var mı?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Giriş yapın
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
