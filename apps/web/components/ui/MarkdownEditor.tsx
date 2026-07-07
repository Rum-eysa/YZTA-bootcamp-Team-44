"use client";

import { cn } from "@/lib/utils";
import MDEditor from "@uiw/react-md-editor";

interface MarkdownEditorProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  placeholder?: string;
}

export function MarkdownEditor({
  label,
  value,
  onChange,
  error,
  placeholder,
}: MarkdownEditorProps) {
  return (
    <div className="space-y-1" data-color-mode="light">
      {label && (
        <label className="block text-label-md text-on-surface-variant">{label}</label>
      )}
      <div
        className={cn(
          "rounded-lg border border-outline-variant overflow-hidden bg-white",
          error && "border-error"
        )}
      >
        <MDEditor
          value={value}
          onChange={(v) => onChange(v ?? "")}
          textareaProps={{ placeholder }}
          height={200}
          preview="edit"
        />
      </div>
      {error && <p className="text-body-sm text-error">{error}</p>}
    </div>
  );
}

