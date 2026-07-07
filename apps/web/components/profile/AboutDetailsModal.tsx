"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { patchProfile } from "@/lib/api/profiles";
import type { UserResponse, UserUpdate } from "@/types/user";
import { useEffect, useState } from "react";

interface AboutDetailsModalProps {
  open: boolean;
  profile: UserResponse;
  onClose: () => void;
  onSaved: (user: UserResponse) => void;
}

const GENDER_OPTIONS = [
  { value: "", label: "Seçiniz" },
  { value: "Kadın", label: "Kadın" },
  { value: "Erkek", label: "Erkek" },
  { value: "Belirtmek istemiyorum", label: "Belirtmek istemiyorum" },
];

const DRIVER_LICENSE_OPTIONS = [
  { value: "", label: "Seçiniz" },
  { value: "Yok", label: "Yok" },
  { value: "B", label: "B Sınıfı" },
  { value: "A", label: "A Sınıfı" },
];

const MILITARY_OPTIONS = [
  { value: "", label: "Seçiniz" },
  { value: "Yapıldı", label: "Yapıldı" },
  { value: "Muaf", label: "Muaf" },
  { value: "Tecilli", label: "Tecilli" },
];

export function AboutDetailsModal({ open, profile, onClose, onSaved }: AboutDetailsModalProps) {
  const [apiError, setApiError] = useState<string>();
  const [gender, setGender] = useState("");
  const [nationality, setNationality] = useState("");
  const [driverLicense, setDriverLicense] = useState("");
  const [militaryStatus, setMilitaryStatus] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setGender(profile.gender || "");
    setNationality(profile.nationality || "");
    setDriverLicense(profile.driver_license || "");
    setMilitaryStatus(profile.military_status || "");
    setApiError(undefined);
  }, [open, profile]);

  const onSubmit = async () => {
    setApiError(undefined);
    setSubmitting(true);
    try {
      const payload: UserUpdate = {
        gender: gender || undefined,
        nationality: nationality.trim() || undefined,
        driver_license: driverLicense || undefined,
        military_status: gender === "Kadın" ? undefined : militaryStatus || undefined,
      };
      const updated = await patchProfile(payload);
      onSaved(updated);
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
      title="Hakkımda Detayları"
      footer={
        <>
          <Button type="button" variant="outline" onClick={onClose}>
            İptal
          </Button>
          <Button type="button" onClick={onSubmit} loading={submitting}>
            Kaydet
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <FormError message={apiError} />
        <Select label="Cinsiyet" options={GENDER_OPTIONS} value={gender} onChange={(e) => setGender(e.target.value)} />
        <Input label="Uyruk" placeholder="T.C." value={nationality} onChange={(e) => setNationality(e.target.value)} />
        <Select
          label="Sürücü Belgesi"
          options={DRIVER_LICENSE_OPTIONS}
          value={driverLicense}
          onChange={(e) => setDriverLicense(e.target.value)}
        />
        {gender !== "Kadın" && (
          <Select
            label="Askerlik Durumu"
            options={MILITARY_OPTIONS}
            value={militaryStatus}
            onChange={(e) => setMilitaryStatus(e.target.value)}
          />
        )}
      </div>
    </Modal>
  );
}

