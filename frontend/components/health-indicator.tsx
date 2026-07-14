"use client";

import { Activity } from "lucide-react";

import { useHealth } from "@/hooks/use-health";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function HealthIndicator() {
  const { health, loading } = useHealth();

  return (
    <Card className="space-y-3">
      <p className="flex items-center gap-2 text-sm font-medium">
        <Activity className="h-4 w-4" /> API Status
      </p>
      {loading ? (
        <Skeleton className="h-6 w-28" />
      ) : (
        <Badge className={health?.status === "ok" ? "border-emerald-500/40 text-emerald-500" : "text-red-500"}>
          {health?.status === "ok" ? "Online" : "Offline"}
        </Badge>
      )}
    </Card>
  );
}
