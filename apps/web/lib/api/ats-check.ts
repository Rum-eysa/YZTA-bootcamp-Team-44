import api from "../api";
import type { AtsCheckResponse } from "@/types/atsCheck";

const MAX_BYTES = 5 * 1024 * 1024;

export async function checkAtsCompatibility(file: File): Promise<AtsCheckResponse> {
  if (!file.name.toLowerCase().endsWith(".pdf") && file.type !== "application/pdf") {
    throw new Error("Sadece PDF dosyası yüklenebilir");
  }
  if (file.size > MAX_BYTES) {
    throw new Error("CV en fazla 5MB olabilir");
  }

  const form = new FormData();
  form.append("file", file);

  const { data } = await api.post<AtsCheckResponse>("/api/ats-check", form);
  return data;
}
