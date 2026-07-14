import * as React from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-xl border border-white/15 bg-white/5 p-5 shadow-xl backdrop-blur-xl dark:bg-black/20",
        className
      )}
      {...props}
    />
  );
}
