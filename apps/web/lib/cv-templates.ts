export const CV_TEMPLATE_IDS = ["1", "2", "3", "4", "5", "6"] as const;

export type CvTemplateId = (typeof CV_TEMPLATE_IDS)[number];

export const DEFAULT_CV_TEMPLATE: CvTemplateId = "1";

export interface CvTemplateOption {
  id: CvTemplateId;
  label: string;
  src: string;
}

/** Sıra: eski 1.1 → 2.1 → 1.2 → 2.2 → 1.3 → 3 */
export const CV_TEMPLATES: CvTemplateOption[] = CV_TEMPLATE_IDS.map((id) => ({
  id,
  label: `Versiyon ${id}`,
  src: `/cv-templates/${id}.png`,
}));

export function getCvTemplate(id: string): CvTemplateOption {
  return CV_TEMPLATES.find((t) => t.id === id) ?? CV_TEMPLATES[0];
}
