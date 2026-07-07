"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { createCertificate, updateCertificate } from "@/lib/api/certificates";
import type { Certificate, CertificateCreate } from "@/types/certificate";
import { useEffect, useState } from "react";

interface CertificateModalProps {
  open: boolean;
  certificate: Certificate | null;
  onClose: () => void;
  onSaved: () => void;
}

export function CertificateModal({ open, certificate, onClose, onSaved }: CertificateModalProps) {
  const [apiError, setApiError] = useState<string>();
  const [title, setTitle] = useState("");
  const [issuer, setIssuer] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setTitle(certificate?.title || "");
    setIssuer(certificate?.issuer || "");
    setIssueDate(certificate?.issue_date || "");
    setUrl(certificate?.url || "");
    setApiError(undefined);
  }, [open, certificate]);

  const submit = async () => {
    setApiError(undefined);
    setSubmitting(true);
    try {
      const payload: CertificateCreate = {
        title: title.trim(),
        issuer: issuer.trim() || null,
        issue_date: issueDate || null,
        url: url.trim() || null,
      };
      if (certificate) await updateCertificate(certificate.id, payload);
      else await createCertificate(payload);
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
      title={certificate ? "Sertifikayı Düzenle" : "Sertifika Ekle"}
      footer={
        <>
          <Button type="button" variant="outline" onClick={onClose}>
            İptal
          </Button>
          <Button type="button" onClick={submit} loading={submitting} disabled={!title.trim()}>
            Kaydet
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <FormError message={apiError} />
        <Input label="Sertifika Adı" value={title} onChange={(e) => setTitle(e.target.value)} />
        <Input label="Kurum" value={issuer} onChange={(e) => setIssuer(e.target.value)} />
        <Input label="Tarih" type="date" value={issueDate} onChange={(e) => setIssueDate(e.target.value)} />
        <Input
          label="Link"
          placeholder="https://..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
      </div>
    </Modal>
  );
}

