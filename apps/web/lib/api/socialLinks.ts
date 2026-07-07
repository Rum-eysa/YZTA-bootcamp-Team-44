import api from "../api";
import type { SocialLink, SocialLinkCreate, SocialLinkUpdate } from "@/types/socialLink";

export async function listSocialLinks(): Promise<SocialLink[]> {
  const { data } = await api.get<SocialLink[]>("/api/profiles/me/social-links");
  return data;
}

export async function createSocialLink(payload: SocialLinkCreate): Promise<SocialLink> {
  const { data } = await api.post<SocialLink>("/api/profiles/me/social-links", payload);
  return data;
}

export async function updateSocialLink(
  id: string,
  payload: SocialLinkUpdate
): Promise<SocialLink> {
  const { data } = await api.patch<SocialLink>(`/api/profiles/me/social-links/${id}`, payload);
  return data;
}

export async function deleteSocialLink(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/social-links/${id}`);
}

