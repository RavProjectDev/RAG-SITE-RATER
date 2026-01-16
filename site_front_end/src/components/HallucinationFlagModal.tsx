"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Flag } from "lucide-react";
import type { HallucinationFlag } from "@/types/comparison";

interface HallucinationFlagModalProps {
  modelLabel: string;
  currentFlags: HallucinationFlag[];
  onSubmit: (flags: HallucinationFlag[]) => void;
  disabled?: boolean;
}

const FLAG_OPTIONS: { value: HallucinationFlag; label: string }[] = [
  { value: "factually_incorrect", label: "Factually Incorrect" },
  { value: "ignored_instructions", label: "Ignored my instructions" },
  { value: "hallucination", label: "Made up information (Hallucination)" },
];

export function HallucinationFlagModal({
  modelLabel,
  currentFlags,
  onSubmit,
  disabled = false,
}: HallucinationFlagModalProps) {
  const [open, setOpen] = useState(false);
  const [selectedFlags, setSelectedFlags] = useState<HallucinationFlag[]>(currentFlags);

  const handleOpenChange = (newOpen: boolean) => {
    if (newOpen) {
      setSelectedFlags(currentFlags);
    }
    setOpen(newOpen);
  };

  const toggleFlag = (flag: HallucinationFlag) => {
    setSelectedFlags((prev) =>
      prev.includes(flag)
        ? prev.filter((f) => f !== flag)
        : [...prev, flag]
    );
  };

  const handleSubmit = () => {
    onSubmit(selectedFlags);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className={`gap-1 ${currentFlags.length > 0 ? 'text-orange-600 hover:text-orange-700' : ''}`}
          disabled={disabled}
        >
          <Flag className={`h-4 w-4 ${currentFlags.length > 0 ? 'fill-orange-600' : ''}`} />
          <span className="text-xs">
            {currentFlags.length > 0 ? `${currentFlags.length} flag${currentFlags.length > 1 ? 's' : ''}` : 'Flag'}
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Flag Issues - Model {modelLabel}</DialogTitle>
          <DialogDescription>
            Select any issues you notice with this response.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          {FLAG_OPTIONS.map((option) => (
            <div key={option.value} className="flex items-start space-x-3">
              <Checkbox
                id={`${modelLabel}-${option.value}`}
                checked={selectedFlags.includes(option.value)}
                onCheckedChange={() => toggleFlag(option.value)}
              />
              <Label
                htmlFor={`${modelLabel}-${option.value}`}
                className="text-sm font-normal cursor-pointer leading-tight"
              >
                {option.label}
              </Label>
            </div>
          ))}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            Submit Flags
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

