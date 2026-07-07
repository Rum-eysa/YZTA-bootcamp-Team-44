"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { createSocialLink, updateSocialLink } from "@/lib/api/socialLinks";
import type { SocialLink, SocialLinkCreate } from "@/types/socialLink";
import { useEffect, useState } from "react";

interface SocialLinkModalProps {
  open: boolean;
  socialLink: SocialLink | null;
  onClose: () => void;
  onSaved: () => void;
}

export function SocialLinkModal({ open, socialLink, onClose, onSaved }: SocialLinkModalProps) {
  const [apiError, setApiError] = useState<string>();
  const [platform, setPlatform] = useState("");
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setPlatform(socialLink?.platform || "");
    setUrl(socialLink?.url || "");
    setApiError(undefined);
  }, [open, socialLink]);

  const submit = async () => {
    setApiError(undefined);
    setSubmitting(true);
    try {
      const payload: SocialLinkCreate = { platform: platform.trim(), url: url.trim() };
      if (socialLink) await updateSocialLink(socialLink.id, payload);
      else await createSocialLink(payload);
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
      title={socialLink ? "Sosyal Bağlantıyı Düzenle" : "Sosyal Bağlantı Ekle"}
      footer={
        <>
          <Button type="button" variant="outline" onClick={onClose}>
            İptal
          </Button>
          <Button
            type="button"
            onClick={submit}
            loading={submitting}
            disabled={!platform.trim() || !url.trim()}
          >
            Kaydet
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <FormError message={apiError} />
        <Input
          label="Platform"
          placeholder="LinkedIn / GitHub"
          value={platform}
          onChange={(e) => setPlatform(e.target.value)}
        />
        <Input label="URL" placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
      </div>
    </Modal>
  );
}

