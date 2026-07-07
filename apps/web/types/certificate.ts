export interface Certificate {
  id: string;
  user_id: string;
  title: string;
  issuer: string | null;
  issue_date: string | null;
  url: string | null;
  created_at: string;
  updated_at: string;
}

export interface CertificateCreate {
  title: string;
  issuer?: string | null;
  issue_date?: string | null;
  url?: string | null;
}

export type CertificateUpdate = Partial<CertificateCreate>;

