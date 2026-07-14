"use client";

import { useState } from "react";
import { Search, History, ArrowUpRight } from "lucide-react";
import type { PredictionResponse } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function RecentPredictions({
  items,
  onSelectItem
}: {
  items: PredictionResponse[];
  onSelectItem?: (item: PredictionResponse) => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredItems = items.filter((item) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      item.category.toLowerCase().includes(searchLower) ||
      item.priority.toLowerCase().includes(searchLower) ||
      item.customer_reply.toLowerCase().includes(searchLower)
    );
  });

  const getPriorityColor = (prio: string) => {
    switch (prio.toLowerCase()) {
      case "high":
        return "border-red-500/25 bg-red-500/10 text-red-400";
      case "medium":
        return "border-amber-500/25 bg-amber-500/10 text-amber-400";
      default:
        return "border-emerald-500/25 bg-emerald-500/10 text-emerald-400";
    }
  };

  return (
    <Card className="glass-panel p-5 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h3 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground flex items-center gap-2">
          <History className="h-4 w-4 text-primary" /> Triage History Log
        </h3>
        
        {/* Search input */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Filter by category or content..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-slate-200"
          />
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <p className="text-xs text-muted-foreground italic text-center py-4">No historical records match your search filter.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-white/5">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-white/5 border-b border-white/5 text-muted-foreground font-semibold">
                <th className="p-3">Category</th>
                <th className="p-3">Priority</th>
                <th className="p-3">Confidence</th>
                <th className="p-3">Response Preview</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredItems.map((item, idx) => (
                <tr
                  key={`${item.category}-${idx}`}
                  className="hover:bg-white/5 transition-colors cursor-pointer group"
                  onClick={() => onSelectItem?.(item)}
                >
                  <td className="p-3 font-semibold capitalize text-slate-200">
                    {item.category.replace("_", " ")}
                  </td>
                  <td className="p-3">
                    <Badge className={`${getPriorityColor(item.priority)} font-bold text-[10px] px-2 py-0.5 uppercase`}>
                      {item.priority}
                    </Badge>
                  </td>
                  <td className="p-3 font-medium text-primary">
                    {(item.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="p-3 text-muted-foreground max-w-xs truncate">
                    {item.customer_reply}
                  </td>
                  <td className="p-3 text-right">
                    <button className="inline-flex items-center gap-1 text-[10px] text-primary bg-primary/5 hover:bg-primary/10 border border-primary/10 px-2 py-1 rounded transition-all group-hover:scale-105">
                      Load Details <ArrowUpRight className="h-3 w-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
