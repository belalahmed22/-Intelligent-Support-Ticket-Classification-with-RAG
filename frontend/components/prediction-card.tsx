"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, MessageSquare, Cpu, Copy, Check, Info } from "lucide-react";
import { toast } from "sonner";

import type { PredictionResponse } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

type TabType = "solution" | "reply" | "explain";

export function PredictionCard({ prediction }: { prediction: PredictionResponse }) {
  const [activeTab, setActiveTab] = useState<TabType>("solution");
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(prediction.customer_reply);
      setCopied(true);
      toast.success("Draft reply copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error("Failed to copy text.");
    }
  };

  const getPriorityColor = (prio: string) => {
    switch (prio.toLowerCase()) {
      case "high":
        return "border-red-500/30 bg-red-500/10 text-red-400";
      case "medium":
        return "border-amber-500/30 bg-amber-500/10 text-amber-400";
      default:
        return "border-emerald-500/30 bg-emerald-500/10 text-emerald-400";
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="glass-panel p-6 space-y-6 overflow-hidden">
        
        {/* Triage Summary Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Auto Triage Results</span>
              <span className="h-1.5 w-1.5 rounded-full bg-primary/80" />
            </div>
            <h3 className="text-xl font-bold tracking-tight capitalize">
              {prediction.category.replace("_", " ")}
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={`${getPriorityColor(prediction.priority)} uppercase text-xs font-semibold px-3 py-1`}>
              {prediction.priority} Priority
            </Badge>
          </div>
        </div>

        {/* Confidence Meter */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-muted-foreground font-medium flex items-center gap-1">
              <Info className="h-3.5 w-3.5" /> Classification Confidence
            </span>
            <span className="font-bold text-primary">{(prediction.confidence * 100).toFixed(2)}%</span>
          </div>
          <Progress value={prediction.confidence * 100} className="h-2 bg-white/5" />
        </div>

        {/* Custom Tabs Navigation */}
        <div className="flex border-b border-white/5 p-1 bg-white/5 rounded-lg">
          <button
            onClick={() => setActiveTab("solution")}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-medium rounded-md transition-all ${
              activeTab === "solution" 
                ? "bg-primary text-primary-foreground shadow-sm" 
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            <BookOpen className="h-3.5 w-3.5" /> Resolution Guide
          </button>
          <button
            onClick={() => setActiveTab("reply")}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-medium rounded-md transition-all ${
              activeTab === "reply" 
                ? "bg-primary text-primary-foreground shadow-sm" 
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            <MessageSquare className="h-3.5 w-3.5" /> Draft Reply
          </button>
          <button
            onClick={() => setActiveTab("explain")}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-medium rounded-md transition-all ${
              activeTab === "explain" 
                ? "bg-primary text-primary-foreground shadow-sm" 
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            <Cpu className="h-3.5 w-3.5" /> AI Explainability
          </button>
        </div>

        {/* Tabs Content */}
        <div className="min-h-[160px] pt-1">
          {activeTab === "solution" && (
            <motion.div
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-3"
            >
              <div className="p-4 rounded-lg bg-white/5 border border-white/5">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Agent Action Steps</p>
                <p className="text-sm leading-relaxed text-slate-200">{prediction.agent_solution}</p>
              </div>
            </motion.div>
          )}

          {activeTab === "reply" && (
            <motion.div
              initial={{ opacity: 0, x: 5 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-3"
            >
              <div className="relative p-4 rounded-lg bg-white/5 border border-white/5">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Draft Email Response</p>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1 text-[11px] bg-primary/10 border border-primary/20 hover:bg-primary/20 text-primary px-2.5 py-1 rounded-md transition-all"
                  >
                    {copied ? (
                      <>
                        <Check className="h-3.5 w-3.5" /> Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-3.5 w-3.5" /> Copy
                      </>
                    )}
                  </button>
                </div>
                <p className="text-sm leading-relaxed whitespace-pre-wrap text-slate-200">{prediction.customer_reply}</p>
              </div>
            </motion.div>
          )}

          {activeTab === "explain" && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4 text-xs"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-3.5 rounded-lg bg-white/5 border border-white/5 space-y-1">
                  <p className="text-muted-foreground font-medium">Loaded ML Classifier</p>
                  <p className="font-semibold text-slate-200 truncate">{prediction.model_used}</p>
                </div>
                <div className="p-3.5 rounded-lg bg-white/5 border border-white/5 space-y-1">
                  <p className="text-muted-foreground font-medium">Feature Vectorizer</p>
                  <p className="font-semibold text-slate-200 truncate">{prediction.vectorizer_used}</p>
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-white/5 border border-white/5 space-y-1">
                <p className="text-muted-foreground font-medium">Explainability Log</p>
                <p className="text-[11px] leading-relaxed text-slate-300">
                  {prediction.confidence >= 0.70 
                    ? `Classification was resolved with high confidence (${(prediction.confidence * 100).toFixed(1)}%) by the production-ready classifier model. A direct retrieval template was mapped.`
                    : "Low confidence ticket detected. If Fallback RAG was enabled, the pipeline queries historical BM25 lexical matches and FAISS dense vector spaces to synthesize agent recommendations."}
                </p>
              </div>
            </motion.div>
          )}
        </div>

      </Card>
    </motion.div>
  );
}
