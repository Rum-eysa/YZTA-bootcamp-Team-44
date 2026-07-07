import api from "../api";
import type { EducationCreate, EducationRecord, EducationUpdate } from "@/types/education";

export async function listEducation(): Promise<EducationRecord[]> {
  const { data } = await api.get<EducationRecord[]>("/api/profiles/me/education");
  return data;
}

export async function createEducation(payload: EducationCreate): Promise<EducationRecord> {
  const { data } = await api.post<EducationRecord>("/api/profiles/me/education", payload);
  return data;
}

export async function updateEducation(
  id: string,
  payload: EducationUpdate
): Promise<EducationRecord> {
  const { data } = await api.patch<EducationRecord>(`/api/profiles/me/education/${id}`, payload);
  return data;
}

export async function deleteEducation(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/education/${id}`);
}

