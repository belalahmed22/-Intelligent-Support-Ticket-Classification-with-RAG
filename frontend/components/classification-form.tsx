"use client";

import { FormEvent, useState } from "react";
import { toast } from "sonner";
import { Sparkles, FileText, CheckCircle2 } from "lucide-react";

import { classifyTicket } from "@/lib/api";
import type { PredictionResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Customer support ticket templates for instant testing
const ticketTemplates = [
  {
    name: "Billing - Double Charge",
    title: "Double charge on my credit card",
    description: "I noticed that my bank account was charged twice for the same transaction on July 12th. The order reference is #881203. Please look into this duplicate transaction and initiate a refund for the second charge."
  },
  {
    name: "Account - Locked Out",
    title: "Cannot access my admin account",
    description: "My login attempts failed several times and now the system says my account is locked for security reasons. I urgently need access to complete the client reports today. Can you please trigger an account unlock?"
  },
  {
    name: "Technical - App Crash",
    title: "Application crashes on dashboard load",
    description: "Immediately after logging in and loading the analytics dashboard, the entire application crashes and redirects to an error screen showing 'Runtime Error: Failed to fetch chart assets'. This is happening on Safari v18."
  },
  {
    name: "General - Address Update",
    title: "Change shipping address for order #4492",
    description: "I placed an order ten minutes ago but realized I typed my old shipping address. Can you please update the zip code and street address to 120 Green Lane, Boston, MA 02115 before it enters the shipping queue?"
  }
];

export function ClassificationForm({
  onPrediction,
  loading,
  setLoading
}: {
  onPrediction: (value: PredictionResponse) => void;
  loading: boolean;
  setLoading: (value: boolean) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const handleSelectTemplate = (tpl: typeof ticketTemplates[0]) => {
    setTitle(tpl.title);
    setDescription(tpl.description);
    toast.info(`Loaded template: ${tpl.name}`);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (title.trim().length < 3 || description.trim().length < 5) {
      toast.error("Please provide a meaningful title and description.");
      return;
    }
    setLoading(true);
    try {
      const prediction = await classifyTicket({ title, description });
      onPrediction(prediction);
      toast.success("Ticket classified successfully.");
    } catch (error) {
      toast.error("Prediction failed. Please ensure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Template Quick Selection */}
      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
          <FileText className="h-3.5 w-3.5 text-primary" /> Quick Templates
        </label>
        <div className="grid grid-cols-2 gap-2">
          {ticketTemplates.map((tpl) => (
            <button
              key={tpl.name}
              type="button"
              onClick={() => handleSelectTemplate(tpl)}
              className="text-left text-xs bg-white/5 border border-white/5 hover:border-primary/30 hover:bg-white/10 p-2.5 rounded-lg transition-all duration-200 truncate"
            >
              {tpl.name}
            </button>
          ))}
        </div>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        {/* Title Input */}
        <div className="space-y-1">
          <div className="flex justify-between items-center">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Ticket Title</label>
            <span className="text-[10px] text-muted-foreground">{title.length} / 100</span>
          </div>
          <Input 
            onChange={(e) => setTitle(e.target.value.slice(0, 100))} 
            placeholder="Brief title summarizing the customer issue..." 
            value={title}
            className="bg-white/5 border-white/10 focus:border-primary focus:ring-1 focus:ring-primary h-10"
          />
        </div>

        {/* Description Input */}
        <div className="space-y-1">
          <div className="flex justify-between items-center">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Detailed Description</label>
            <span className="text-[10px] text-muted-foreground">{description.length} / 1000</span>
          </div>
          <Textarea
            onChange={(e) => setDescription(e.target.value.slice(0, 1000))}
            placeholder="Paste raw support ticket or describe the issue in detail here..."
            value={description}
            rows={5}
            className="bg-white/5 border-white/10 focus:border-primary focus:ring-1 focus:ring-primary resize-none leading-relaxed"
          />
        </div>

        <Button className="w-full h-11 bg-primary hover:bg-primary/95 text-primary-foreground font-semibold shadow-lg shadow-primary/10 transition-all hover:scale-[1.01]" disabled={loading} type="submit">
          {loading ? (
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 animate-pulse" /> Triaging Ticket...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" /> Classify Ticket
            </span>
          )}
        </Button>
      </form>
    </div>
  );
}
