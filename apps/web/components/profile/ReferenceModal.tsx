"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { createReference, updateReference } from "@/lib/api/references";
import { formatTRPhone } from "@/lib/phone";
import type { Reference, ReferenceCreate } from "@/types/reference";
import { useEffect, useState } from "react";

interface ReferenceModalProps {
  open: boolean;
  reference: Reference | null;
  onClose: () => void;
  onSaved: () => void;
}

export function ReferenceModal({ open, reference, onClose, onSaved }: ReferenceModalProps) {
  const [apiError, setApiError] = useState<string>();
  const [name, setName] = useState("");
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [contact, setContact] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setName(reference?.name || "");
    setTitle(reference?.title || "");
    setCompany(reference?.company || "");
    setContact(reference?.contact || "");
    setApiError(undefined);
  }, [open, reference]);

  const submit = async () => {
    setApiError(undefined);
    setSubmitting(true);
    try {
      const payload: ReferenceCreate = {
        name: name.trim(),
        title: title.trim() || null,
        company: company.trim() || null,
        contact: contact.trim() || null,
        notes: null,
      };
      if (reference) await updateReference(reference.id, payload);
      else await createReference(payload);
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
      title={reference ? "Referansı Düzenle" : "Referans Ekle"}
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
        <Input label="İsim" value={name} onChange={(e) => setName(e.target.value)} />
        <div className="grid grid-cols-2 gap-3">
          <Input label="Ünvan" value={title} onChange={(e) => setTitle(e.target.value)} />
          <Input label="Şirket" value={company} onChange={(e) => setCompany(e.target.value)} />
        </div>
        <Input
          label="İletişim (Telefon)"
          placeholder="+90 (555) 123 45 67"
          inputMode="tel"
          value={contact}
          onChange={(e) => setContact(formatTRPhone(e.target.value))}
        />
      </div>
    </Modal>
  );
}

