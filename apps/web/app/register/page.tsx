"use client";

import { AuthPageLayout } from "@/components/auth/AuthPageLayout";
import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { login, register as registerUser, saveTokens } from "@/lib/api/auth";
import { getApiErrorMessage, getApiErrorStatus } from "@/lib/apiErrors";
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
    setFocus,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    let registrationCompleted = false;

    try {
      await registerUser(data);
      registrationCompleted = true;
      const tokens = await login(data.email, data.password);
      saveTokens(tokens);
      await refreshUser();
      router.push("/profile");
    } catch (err: unknown) {
      const status = getApiErrorStatus(err);
      if (!registrationCompleted && (status === 400 || status === 409)) {
        setApiError("Bu e-posta adresiyle daha önce kayıt olunmuş.");
        setFocus("email");
        return;
      }

      setApiError(
        getApiErrorMessage(err, "Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.", {
          serviceUnavailable: "Kayıt servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        })
      );
    }
  };

  return (
    <AuthPageLayout>
      <h1 className="mb-6 text-headline-lg-mobile font-semibold text-on-surface">Kayıt Ol</h1>

      <form
        onSubmit={(event) => {
          setApiError(undefined);
          void handleSubmit(onSubmit)(event);
        }}
        className="space-y-4"
      >
        <FormError message={apiError} />
        <Input
          label="Ad Soyad"
          autoComplete="name"
          error={errors.full_name?.message}
          {...register("full_name")}
        />
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
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <Button type="submit" loading={isSubmitting} className="w-full py-3">
          Kayıt Ol
        </Button>
      </form>

      <p className="mt-5 text-center text-body-sm text-on-surface-variant">
        Zaten hesabınız var mı?{" "}
        <Link href="/login" className="font-semibold text-primary hover:underline">
          Giriş yapın
        </Link>
      </p>
    </AuthPageLayout>
  );
}
