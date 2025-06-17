import React from "react";
import { Lightbulb } from "lucide-react";

interface AIInsightProps {
  reason: string;
}

export function AIInsight({ reason }: AIInsightProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Lightbulb className="w-5 h-5 text-amber-500" />
        <h4 className="text-sm font-semibold text-gray-700">AI Insight</h4>
      </div>
      <p className="text-gray-600 text-sm">{reason}</p>
    </div>
  );
} 