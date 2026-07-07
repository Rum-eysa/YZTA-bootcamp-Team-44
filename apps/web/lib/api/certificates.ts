import api from "../api";
import type { Certificate, CertificateCreate, CertificateUpdate } from "@/types/certificate";

export async function listCertificates(): Promise<Certificate[]> {
  const { data } = await api.get<Certificate[]>("/api/profiles/me/certificates");
  return data;
}

export async function createCertificate(payload: CertificateCreate): Promise<Certificate> {
  const { data } = await api.post<Certificate>("/api/profiles/me/certificates", payload);
  return data;
}

export async function updateCertificate(id: string, payload: CertificateUpdate): Promise<Certificate> {
  const { data } = await api.patch<Certificate>(`/api/profiles/me/certificates/${id}`, payload);
  return data;
}

export async function deleteCertificate(id: string): Promise<void> {
  await api.delete(`/api/profiles/me/certificates/${id}`);
}

