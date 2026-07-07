"use client";

import { Button } from "@/components/ui/Button";
import { FormError } from "@/components/ui/FormError";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { createExam, updateExam } from "@/lib/api/exams";
import type { Exam, ExamCreate } from "@/types/exam";
import { useEffect, useState } from "react";

interface ExamModalProps {
  open: boolean;
  exam: Exam | null;
  onClose: () => void;
  onSaved: () => void;
}

export function ExamModal({ open, exam, onClose, onSaved }: ExamModalProps) {
  const [apiError, setApiError] = useState<string>();
  const [name, setName] = useState("");
  const [score, setScore] = useState("");
  const [examDate, setExamDate] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open) return;
    setName(exam?.name || "");
    setScore(exam?.score || "");
    setExamDate(exam?.exam_date || "");
    setApiError(undefined);
  }, [open, exam]);

  const submit = async () => {
    setApiError(undefined);
    setSubmitting(true);
    try {
      const payload: ExamCreate = {
        name: name.trim(),
        score: score.trim() || null,
        exam_date: examDate || null,
        description: null,
      };
      if (exam) await updateExam(exam.id, payload);
      else await createExam(payload);
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
      title={exam ? "Sınavı Düzenle" : "Sınav Ekle"}
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
        <Input label="Sınav Adı" value={name} onChange={(e) => setName(e.target.value)} />
        <div className="grid grid-cols-2 gap-3">
          <Input label="Skor" value={score} onChange={(e) => setScore(e.target.value)} />
          <Input label="Tarih" type="date" value={examDate} onChange={(e) => setExamDate(e.target.value)} />
        </div>
      </div>
    </Modal>
  );
}

