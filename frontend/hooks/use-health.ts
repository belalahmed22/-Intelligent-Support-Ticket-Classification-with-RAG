"use client";

import { useEffect, useState } from "react";

import { getHealth } from "@/lib/api";
import type { HealthStatus } from "@/lib/types";

export function useHealth(intervalMs = 10000) {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      try {
        const next = await getHealth();
        if (!cancelled) {
          setHealth(next);
        }
      } catch {
        if (!cancelled) {
          setHealth({ status: "down", model_loaded: false, model_name: null });
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    poll();
    const timer = setInterval(poll, intervalMs);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [intervalMs]);

  return { health, loading };
}
