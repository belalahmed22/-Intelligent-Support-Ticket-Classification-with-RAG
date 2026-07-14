"use client";

import Link from "next/link";
import { Bot, LayoutDashboard, LogOut, ShieldCheck, Home } from "lucide-react";

import { Card } from "@/components/ui/card";
import { ThemeToggle } from "@/components/theme-toggle";

export function SidebarNav({
  activeUser,
  onLogout
}: {
  activeUser?: string | null;
  onLogout?: () => void;
}) {
  const getInitials = (name: string) => {
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <Card className="glass-panel p-5 space-y-6 h-fit border-white/10">
      
      {/* Brand Header */}
      <div className="flex items-center justify-between border-b border-white/5 pb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10 border border-primary/20">
            <Bot className="h-4.5 w-4.5 text-primary" />
          </div>
          <p className="font-bold tracking-tight text-sm text-foreground">AI Ops Desk</p>
        </div>
        <ThemeToggle />
      </div>

      {/* Navigation Links */}
      <div className="space-y-1.5">
        <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-3 mb-1">
          Menu
        </p>
        <Link 
          className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all" 
          href="/"
        >
          <Home className="h-4 w-4" /> Landing
        </Link>
        <Link 
          className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-xs font-medium text-primary bg-primary/10 border border-primary/10 transition-all" 
          href="/dashboard"
        >
          <LayoutDashboard className="h-4 w-4" /> Dashboard
        </Link>
      </div>

      {/* User Profile & Logout section */}
      {activeUser && (
        <div className="space-y-3 pt-4 border-t border-white/5">
          <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider px-3">
            Operator Session
          </p>
          <div className="flex items-center gap-3 p-2 bg-white/5 rounded-xl border border-white/5">
            <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center text-primary-foreground text-xs font-bold shadow-md shadow-primary/10">
              {getInitials(activeUser)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-foreground truncate capitalize">{activeUser}</p>
              <p className="text-[9px] text-muted-foreground flex items-center gap-0.5 mt-0.5">
                <ShieldCheck className="h-3 w-3 text-primary" /> Agent Operator
              </p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-semibold text-red-400 bg-red-500/5 hover:bg-red-500/10 border border-red-500/10 transition-all mt-1"
          >
            <LogOut className="h-3.5 w-3.5" /> Log Out
          </button>
        </div>
      )}
      
    </Card>
  );
}
