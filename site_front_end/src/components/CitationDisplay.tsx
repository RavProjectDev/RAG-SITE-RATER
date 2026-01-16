"use client";

import { useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import type { Citation } from "@/types/comparison";

interface CitationDisplayProps {
  citation: Citation;
}

export function CitationDisplay({ citation }: CitationDisplayProps) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button 
          className="inline-flex items-center justify-center text-xs font-medium transition-colors hover:bg-blue-100 dark:hover:bg-blue-900 rounded px-1 mx-0.5 cursor-pointer bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400"
        >
          [{citation.number}]
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-4 max-h-[80vh] overflow-y-auto" align="start">
        <div className="space-y-3">
          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400">
            Source {citation.number}
          </div>
          <div className="text-sm text-gray-700 dark:text-gray-300 p-3 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 whitespace-pre-wrap break-words">
            {citation.text}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 italic break-words">
            {citation.source}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

