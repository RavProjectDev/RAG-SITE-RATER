"use client";

import { useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle } from "lucide-react";
import type { Citation, CitationRating } from "@/types/comparison";

interface CitationPopoverProps {
  citation: Citation;
  onRate: (citationId: string, rating: CitationRating) => void;
  currentRating?: CitationRating;
}

export function CitationPopover({ 
  citation, 
  onRate, 
  currentRating 
}: CitationPopoverProps) {
  const [open, setOpen] = useState(false);

  const handleRate = (rating: CitationRating) => {
    onRate(citation.id, rating);
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button 
          className={`inline-flex items-center justify-center text-xs font-medium transition-colors hover:bg-blue-100 dark:hover:bg-blue-900 rounded px-1 mx-0.5 cursor-pointer ${
            currentRating === "supported" 
              ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" 
              : currentRating === "not_supported"
              ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
              : "bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400"
          }`}
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
          <div className="flex gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <Button
              size="sm"
              variant={currentRating === "supported" ? "default" : "outline"}
              className="flex-1 gap-1"
              onClick={() => handleRate("supported")}
            >
              <CheckCircle2 className="h-4 w-4" />
              Supported
            </Button>
            <Button
              size="sm"
              variant={currentRating === "not_supported" ? "destructive" : "outline"}
              className="flex-1 gap-1"
              onClick={() => handleRate("not_supported")}
            >
              <XCircle className="h-4 w-4" />
              Not Supported
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

