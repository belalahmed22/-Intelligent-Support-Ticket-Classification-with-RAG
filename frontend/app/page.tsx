"use client";

import Link from "next/link";
import { ArrowRight, Bot, Cpu, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground selection:bg-primary/20">
      {/* Visual background decorations */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30" />
      <div className="pointer-events-none absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[120px]" />
      <div className="pointer-events-none absolute right-10 bottom-10 w-[400px] h-[400px] bg-indigo-500/5 rounded-full blur-[100px]" />

      <header className="relative mx-auto max-w-7xl px-6 py-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-primary/15 border border-primary/25">
            <Bot className="h-5 w-5 text-primary" />
          </div>
          <span className="font-semibold tracking-tight text-lg">AI Ops Desk</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
              Dashboard
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="sm" className="bg-primary hover:bg-primary/95 text-primary-foreground shadow-lg shadow-primary/20">
              Launch App
            </Button>
          </Link>
        </div>
      </header>

      <section className="relative mx-auto max-w-5xl px-6 pt-20 pb-24 text-center flex flex-col items-center justify-center gap-8 z-10">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-xs text-primary font-medium tracking-wide uppercase"
        >
          <Sparkles className="h-3.5 w-3.5" /> Next-Generation Ticket Routing & Triage
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-5xl font-bold tracking-tight sm:text-7xl max-w-4xl bg-gradient-to-b from-white via-slate-200 to-slate-400 bg-clip-text text-transparent"
        >
          Classify Support Tickets with Hybrid RAG Triage
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="max-w-2xl text-lg text-muted-foreground leading-relaxed"
        >
          An enterprise-grade triage suite combining lexical search (BM25) and semantic vector search (FAISS) with high-confidence fallback classification. Autogenerate responses instantly.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Link href="/dashboard">
            <Button size="lg" className="h-12 px-8 bg-primary hover:bg-primary/95 text-primary-foreground font-semibold shadow-xl shadow-primary/25 transition-all duration-200 hover:scale-[1.02]">
              Open Operations Desk <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </motion.div>

        {/* Highlight Stats Blocks */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl mt-12 text-left"
        >
          <div className="glass-panel p-5 rounded-2xl">
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 w-fit mb-3">
              <ShieldCheck className="h-5 w-5 text-indigo-400" />
            </div>
            <p className="text-2xl font-bold">97.2%</p>
            <p className="text-xs text-muted-foreground mt-1">Classification Accuracy</p>
          </div>

          <div className="glass-panel p-5 rounded-2xl">
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 w-fit mb-3">
              <Zap className="h-5 w-5 text-emerald-400" />
            </div>
            <p className="text-2xl font-bold">&lt; 45ms</p>
            <p className="text-xs text-muted-foreground mt-1">Average Response Latency</p>
          </div>

          <div className="glass-panel p-5 rounded-2xl">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 w-fit mb-3">
              <Cpu className="h-5 w-5 text-amber-400" />
            </div>
            <p className="text-2xl font-bold">FAISS</p>
            <p className="text-xs text-muted-foreground mt-1">High-Speed L2 Indexes</p>
          </div>

          <div className="glass-panel p-5 rounded-2xl">
            <div className="p-2 rounded-lg bg-purple-500/10 border border-purple-500/20 w-fit mb-3">
              <Bot className="h-5 w-5 text-purple-400" />
            </div>
            <p className="text-2xl font-bold">95.0%</p>
            <p className="text-xs text-muted-foreground mt-1">Top-5 Retrieval Hits</p>
          </div>
        </motion.div>
      </section>

      <footer className="absolute bottom-6 left-0 right-0 text-center text-xs text-muted-foreground z-10">
        AI Support Ticket Triage Operations • Enterprise Edition v1.0.0
      </footer>
    </main>
  );
}
