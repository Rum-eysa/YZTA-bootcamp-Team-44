export interface SocialLink {
  id: string;
  user_id: string;
  platform: string;
  url: string;
  created_at: string;
  updated_at: string;
}

export interface SocialLinkCreate {
  platform: string;
  url: string;
}

export type SocialLinkUpdate = Partial<SocialLinkCreate>;

