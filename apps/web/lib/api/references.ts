import api from "../api";
import type { Reference, ReferenceCreate, ReferenceUpdate } from "@/types/reference";

export async function listReferences(): Promise<Reference[]> {
  const { data } = await api.get<Reference[]>("/api/profiles/me/references");
  return data;
}

export async function createReference(payload: ReferenceCreate): Promise<Reference> {
  const { data } = await api.post<Reference>("/api/profiles/me/references", payload);
  return data;
}

export async function updateReference(id: string, payload: ReferenceUpdate): Promise<Reference> {
  const { data } = await api.patch<Reference>(`/api/profiles/me/references/${id}`, payload);
  return data;
}

export async function deleteReference(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/references/${id}`);
}

