import * as React from "react";

import { cn } from "@/lib/utils";

export function Badge({
  className,
  children
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-border bg-muted/80 px-2 py-1 text-xs font-medium",
        className
      )}
    >
      {children}
    </span>
  );
}
