"use client";

import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { KeyboardEvent, useState } from "react";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  label?: string;
  error?: string;
  placeholder?: string;
}

export function TagInput({
  value,
  onChange,
  label,
  error,
  placeholder = "Beceri ekleyip Enter'a basın",
}: TagInputProps) {
  const [input, setInput] = useState("");

  const addTag = (tag: string) => {
    const trimmed = tag.trim();
    if (!trimmed || value.includes(trimmed)) return;
    onChange([...value, trimmed]);
    setInput("");
  };

  const removeTag = (tag: string) => {
    onChange(value.filter((t) => t !== tag));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(input);
    } else if (e.key === "Backspace" && !input && value.length > 0) {
      onChange(value.slice(0, -1));
    }
  };

  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-label-md text-on-surface-variant">{label}</label>
      )}
      <div
        className={cn(
          "input-field flex flex-wrap gap-2 items-center min-h-[42px]",
          error && "border-error focus-within:border-error focus-within:ring-error/20"
        )}
      >
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 bg-primary-fixed/20 text-primary px-2 py-1 rounded-full text-label-md max-w-full"
          >
            <span className="break-all min-w-0">{tag}</span>
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="hover:text-error transition-colors shrink-0"
              aria-label={`${tag} kaldır`}
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => input && addTag(input)}
          placeholder={value.length === 0 ? placeholder : ""}
          className="flex-1 min-w-[120px] outline-none bg-transparent text-body-sm"
        />
      </div>
      {error && <p className="text-body-sm text-error">{error}</p>}
    </div>
  );
}
