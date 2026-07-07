export function formatTRPhone(value: string): string {
  const digits = value.replace(/\D/g, "");
  const local = digits.startsWith("90") ? digits.slice(2) : digits;
  const ten = local.startsWith("0") ? local.slice(1) : local;
  const sliced = ten.slice(0, 10);
  const area = sliced.slice(0, 3);
  const part1 = sliced.slice(3, 6);
  const part2 = sliced.slice(6, 8);
  const part3 = sliced.slice(8, 10);
  if (!sliced) return "";
  if (sliced.length <= 3) return `+90 (${area}`;
  if (sliced.length <= 6) return `+90 (${area}) ${part1}`;
  if (sliced.length <= 8) return `+90 (${area}) ${part1} ${part2}`;
  return `+90 (${area}) ${part1} ${part2} ${part3}`.trim();
}
