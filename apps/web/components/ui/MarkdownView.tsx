"use client";

import { cn } from "@/lib/utils";
import MDEditor from "@uiw/react-md-editor";

interface MarkdownViewProps {
  source: string;
  className?: string;
}

export function MarkdownView({ source, className }: MarkdownViewProps) {
  return (
    <div data-color-mode="light" className={cn("markdown-view", className)}>
      <MDEditor.Markdown source={source} />
    </div>
  );
}
