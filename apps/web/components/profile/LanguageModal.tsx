"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { createLanguage, updateLanguage } from "@/lib/api/languages";
import type { Language, LanguageCreate } from "@/types/language";
import { useEffect, useState } from "react";

interface LanguageModalProps {
  open: boolean;
  language: Language | null;
  onClose: () => void;
  onSaved: () => void;
}

export function LanguageModal({ open, language, onClose, onSaved }: LanguageModalProps) {
  const [apiError, setApiError] = useState<string>();
  const [name, setName] = useState("");
  const [level, setLevel] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setName(language?.name || "");
    setLevel(language?.level || "");
    setApiError(undefined);
  }, [open, language]);

  const submit = async () => {
    setApiError(undefined);
    setSubmitting(true);
    try {
      const payload: LanguageCreate = { name: name.trim(), level: level.trim() || null };
      if (language) await updateLanguage(language.id, payload);
      else await createLanguage(payload);
      onSaved();
      onClose();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setApiError(typeof detail === "string" ? detail : "Kayıt başarısız. Lütfen tekrar deneyin.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={language ? "Dil Bilgisini Düzenle" : "Dil Ekle"}
      footer={
        <>
          <Button type="button" variant="outline" onClick={onClose}>
            İptal
          </Button>
          <Button type="button" onClick={submit} loading={submitting} disabled={!name.trim()}>
            Kaydet
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <FormError message={apiError} />
        <Input label="Dil" placeholder="İngilizce" value={name} onChange={(e) => setName(e.target.value)} />
        <Input label="Seviye" placeholder="B2" value={level} onChange={(e) => setLevel(e.target.value)} />
      </div>
    </Modal>
  );
}

