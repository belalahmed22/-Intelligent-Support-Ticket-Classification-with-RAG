"use client";

import { useEffect, useState } from "react";
import { Cpu } from "lucide-react";

import { getModelInfo } from "@/lib/api";
import type { ModelInfo } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ModelInfoPanel() {
  const [data, setData] = useState<ModelInfo | null>(null);

  useEffect(() => {
    getModelInfo().then(setData).catch(() => setData(null));
  }, []);

  return (
    <Card className="space-y-3">
      <p className="flex items-center gap-2 text-sm font-medium">
        <Cpu className="h-4 w-4" /> Selected Model
      </p>
      {!data ? (
        <Skeleton className="h-12 w-full" />
      ) : (
        <>
          <p className="text-sm">{data.selected_model}</p>
          <p className="line-clamp-1 text-xs text-muted-foreground">{data.model_path}</p>
        </>
      )}
    </Card>
  );
}
