import api from "../api";
import type { Language, LanguageCreate, LanguageUpdate } from "@/types/language";

export async function listLanguages(): Promise<Language[]> {
  const { data } = await api.get<Language[]>("/api/profiles/me/languages");
  return data;
}

export async function createLanguage(payload: LanguageCreate): Promise<Language> {
  const { data } = await api.post<Language>("/api/profiles/me/languages", payload);
  return data;
}

export async function updateLanguage(id: string, payload: LanguageUpdate): Promise<Language> {
  const { data } = await api.patch<Language>(`/api/profiles/me/languages/${id}`, payload);
  return data;
}

export async function deleteLanguage(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/languages/${id}`);
}

