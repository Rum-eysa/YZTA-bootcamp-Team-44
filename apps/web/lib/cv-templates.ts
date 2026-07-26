export const CV_TEMPLATE_IDS = [
  "Version1",
  "Version2",
  "Version3",
  "Version4",
  "Version5",
] as const;

export type CvTemplateId = (typeof CV_TEMPLATE_IDS)[number];

export const DEFAULT_CV_TEMPLATE: CvTemplateId = "Version1";

export interface CvTemplateOption {
  id: CvTemplateId;
  label: string;
  src: string;
}

export const CV_TEMPLATES: CvTemplateOption[] = CV_TEMPLATE_IDS.map((id, index) => ({
  id,
  label: `Versiyon ${index + 1}`,
  src: `/cv-templates/${id}.png`,
}));

export function getCvTemplate(id: string): CvTemplateOption {
  return CV_TEMPLATES.find((t) => t.id === id) ?? CV_TEMPLATES[0];
}

export function normalizeCvTemplateId(id: string | null | undefined): CvTemplateId {
  if (!id) return DEFAULT_CV_TEMPLATE;
  const trimmed = id.trim();
  if ((CV_TEMPLATE_IDS as readonly string[]).includes(trimmed)) {
    return trimmed as CvTemplateId;
  }
  // Eski id'ler (6 şablon dönemi + sayısal)
  const legacy: Record<string, CvTemplateId> = {
    "1": "Version1",
    "2": "Version2",
    "3": "Version3",
    "4": "Version4",
    "5": "Version5",
    "6": "Version5",
    Version6: "Version5",
  };
  return legacy[trimmed] ?? DEFAULT_CV_TEMPLATE;
}
