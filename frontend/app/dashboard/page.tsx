"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BarChart3, Activity, Sparkles, CheckCircle2, RefreshCw, Layers } from "lucide-react";

import { LoginForm } from "@/components/login-form";
import { ChatbotWidget } from "@/components/chatbot-widget";
import { ClassificationForm } from "@/components/classification-form";
import { HealthIndicator } from "@/components/health-indicator";
import { PredictionCard } from "@/components/prediction-card";
import { RecentPredictions } from "@/components/recent-predictions";
import { SidebarNav } from "@/components/sidebar-nav";
import { Card } from "@/components/ui/card";
import type { PredictionResponse } from "@/lib/types";

export default function DashboardPage() {
  const [activeUser, setActiveUser] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [history, setHistory] = useState<PredictionResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Authenticate user session on mount
  useEffect(() => {
    setIsMounted(true);
    const storedUser = localStorage.getItem("ai_ops_active_user");
    if (storedUser) {
      setActiveUser(storedUser);
      loadUserHistory(storedUser);
    }
  }, []);

  const loadUserHistory = (username: string) => {
    const userKey = `ai_ops_history_${username.toLowerCase()}`;
    const storedHistory = localStorage.getItem(userKey);
    if (storedHistory) {
      setHistory(JSON.parse(storedHistory));
    } else {
      setHistory([]);
      localStorage.setItem(userKey, JSON.stringify([]));
    }
  };

  const handleLoginSuccess = (username: string) => {
    localStorage.setItem("ai_ops_active_user", username);
    setActiveUser(username);
    loadUserHistory(username);
  };

  const handleLogout = () => {
    localStorage.removeItem("ai_ops_active_user");
    setActiveUser(null);
    setPrediction(null);
    setHistory([]);
  };

  const handlePrediction = (result: PredictionResponse) => {
    setPrediction(result);

    // Save prediction in user history
    if (activeUser) {
      const userKey = `ai_ops_history_${activeUser.toLowerCase()}`;
      const newHistory = [result, ...history];
      setHistory(newHistory);
      localStorage.setItem(userKey, JSON.stringify(newHistory));
    }
  };

  const handleSelectHistoryItem = (item: PredictionResponse) => {
    setPrediction(item);
  };

  // Prevent SSR flicker
  if (!isMounted) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <RefreshCw className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }

  // Render Login flow if session is empty
  if (!activeUser) {
    return <LoginForm onSuccess={handleLoginSuccess} />;
  }

  // Compute live analytics from user history
  const totalProcessed = history.length;
  const avgConfidence = history.length > 0 
    ? history.reduce((acc, curr) => acc + curr.confidence, 0) / history.length 
    : 0;
  
  const categoryCounts = history.reduce((acc, curr) => {
    acc[curr.category] = (acc[curr.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const priorityCounts = history.reduce((acc, curr) => {
    acc[curr.priority] = (acc[curr.priority] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <main className="min-h-screen bg-background p-4 text-foreground md:p-6 relative selection:bg-primary/20 transition-colors duration-300">
      {/* Visual glowing meshes */}
      <div className="pointer-events-none absolute right-0 top-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] dark:bg-primary/5" />
      <div className="pointer-events-none absolute left-0 bottom-0 w-[450px] h-[450px] bg-indigo-500/5 rounded-full blur-[100px] dark:bg-indigo-500/5" />

      <div className="mx-auto max-w-[1400px] grid gap-6 lg:grid-cols-[280px_1fr]">
        
        {/* Left column - Navigation, status checks */}
        <div className="space-y-6">
          <SidebarNav activeUser={activeUser} onLogout={handleLogout} />
          <HealthIndicator />
        </div>

        {/* Central triage console & live statistics */}
        <div className="space-y-6">
          
          <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">AI Operations Desk</h1>
              <p className="text-sm text-muted-foreground">Welcome back! Manage support classification logs and drafts under your operator account.</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg w-fit">
              <Activity className="h-3.5 w-3.5 text-emerald-500 animate-pulse" /> Session: {activeUser}
            </div>
          </header>

          <div className="grid gap-6 md:grid-cols-3">
            
            {/* Classification playground (2 cols) */}
            <div className="md:col-span-2 space-y-6">
              <Card className="glass-panel p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">Ticket Triage Playground</h2>
                  <span className="text-[10px] bg-primary/10 border border-primary/25 text-primary px-3 py-0.5 rounded-full font-bold">
                    Qwen-2.5-1.5B Active
                  </span>
                </div>
                <ClassificationForm loading={loading} onPrediction={handlePrediction} setLoading={setLoading} />
              </Card>

              <AnimatePresence mode="wait">
                {loading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="glass-panel p-6 space-y-4 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <RefreshCw className="h-4 w-4 animate-spin text-primary" />
                      <p className="text-sm text-muted-foreground">Running Qwen hybrid triage models, analyzing keywords...</p>
                    </div>
                    <div className="h-32 bg-white/5 animate-pulse rounded-lg" />
                  </motion.div>
                )}

                {!loading && prediction && (
                  <PredictionCard prediction={prediction} />
                )}
              </AnimatePresence>
            </div>

            {/* Live operator statistics (1 col) */}
            <div className="space-y-6">
              <Card className="glass-panel p-5 space-y-5 h-full">
                <h2 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-primary" /> Personal Analytics
                </h2>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 border border-white/5 p-3 rounded-lg text-center">
                    <p className="text-2xl font-bold text-primary">{totalProcessed}</p>
                    <p className="text-[10px] text-muted-foreground mt-1">Processed</p>
                  </div>
                  <div className="bg-white/5 border border-white/5 p-3 rounded-lg text-center">
                    <p className="text-2xl font-bold text-emerald-400">
                      {(avgConfidence * 100).toFixed(1)}%
                    </p>
                    <p className="text-[10px] text-muted-foreground mt-1">Avg Confidence</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="text-xs font-medium text-muted-foreground">Category Share</p>
                  <div className="space-y-2">
                    {Object.entries(categoryCounts).length === 0 ? (
                      <p className="text-xs text-muted-foreground italic">No tickets classified yet.</p>
                    ) : (
                      Object.entries(categoryCounts).map(([cat, count]) => {
                        const pct = (count / totalProcessed) * 100;
                        return (
                          <div key={cat} className="space-y-1">
                            <div className="flex justify-between text-xs">
                              <span className="font-medium capitalize">{cat.replace("_", " ")}</span>
                              <span className="text-muted-foreground">{count} ({pct.toFixed(0)}%)</span>
                            </div>
                            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-primary rounded-full transition-all duration-500" 
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>

                <div className="space-y-3 pt-2">
                  <p className="text-xs font-medium text-muted-foreground">Priority Breakdown</p>
                  <div className="flex items-center gap-2">
                    {["high", "medium", "low"].map((prio) => {
                      const count = priorityCounts[prio] || 0;
                      const color = 
                        prio === "high" 
                          ? "bg-red-500/80" 
                          : prio === "medium" 
                          ? "bg-amber-500/80" 
                          : "bg-emerald-500/80";
                      
                      return (
                        <div key={prio} className="flex-1 bg-white/5 border border-white/5 rounded-lg p-2 text-center" title={`${count} tickets`}>
                          <span className={`inline-block w-2.5 h-2.5 rounded-full ${color} mb-1`} />
                          <p className="text-[10px] uppercase font-bold text-muted-foreground">{prio}</p>
                          <p className="text-xs font-semibold mt-0.5">{count}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </Card>
            </div>

          </div>

          {/* History log (bottom) */}
          <RecentPredictions items={history} onSelectItem={handleSelectHistoryItem} />
          
        </div>
      </div>

      {/* Floating Qwen support chatbot in the bottom right */}
      <ChatbotWidget />
    </main>
  );
}
