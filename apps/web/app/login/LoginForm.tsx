"use client";

import { AuthPageLayout } from "@/components/auth/AuthPageLayout";
import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { login, saveTokens } from "@/lib/api/auth";
import { getApiErrorMessage, getApiErrorStatus } from "@/lib/apiErrors";
import { useAuth } from "@/hooks/useAuth";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
  const [apiError, setApiError] = useState<string>();

  const {
    register,
    handleSubmit,
    setFocus,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      const tokens = await login(data.email, data.password);
      saveTokens(tokens);
      await refreshUser();
      router.push("/profile");
    } catch (err: unknown) {
      const status = getApiErrorStatus(err);
      if (status && [400, 401, 402, 404].includes(status)) {
        setApiError("E-posta veya şifre hatalı.");
        setFocus("password");
        return;
      }

      setApiError(
        getApiErrorMessage(err, "Giriş başarısız. Lütfen tekrar deneyin.", {
          serviceUnavailable: "Giriş servisi şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        })
      );
    }
  };

  return (
    <AuthPageLayout>
      <h2 className="mb-6 text-headline-lg-mobile font-semibold text-on-surface">Giriş Yap</h2>

      <form
        onSubmit={(event) => {
          setApiError(undefined);
          void handleSubmit(onSubmit)(event);
        }}
        className="space-y-4"
      >
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

      <p className="mt-5 text-center text-body-sm text-on-surface-variant">
        Hesabınız yok mu?{" "}
        <Link href="/register" className="font-semibold text-primary hover:underline">
          Kayıt olun
        </Link>
      </p>
    </AuthPageLayout>
  );
}
