"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, User, Lock, ArrowRight, UserPlus, KeyRound } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export function LoginForm({ onSuccess }: { onSuccess: (username: string) => void }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const name = username.trim().toLowerCase();
    const pass = password.trim();

    if (name.length < 3 || pass.length < 4) {
      toast.error("Username must be at least 3 chars, password at least 4 chars.");
      return;
    }

    // Retrieve local user database
    const rawUsers = localStorage.getItem("ai_ops_users");
    const users = rawUsers ? JSON.parse(rawUsers) : { admin: "admin123" }; // default user

    if (isRegister) {
      // Register Mode
      if (users[name]) {
        toast.error("Account already exists. Please choose a different username.");
        return;
      }
      users[name] = pass;
      localStorage.setItem("ai_ops_users", JSON.stringify(users));
      toast.success(`Account registered successfully! You can now log in.`);
      setIsRegister(false);
      setPassword("");
    } else {
      // Login Mode
      if (users[name] && users[name] === pass) {
        toast.success(`Welcome back, ${username}!`);
        onSuccess(username);
      } else {
        toast.error("Invalid username or password. Try 'admin' and 'admin123'.");
      }
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background px-4 py-8 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(147,51,234,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(147,51,234,0.02)_1px,transparent_1px)] bg-[size:3rem_3rem]" />
      <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[100px]" />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-[420px] z-10"
      >
        <Card className="glass-panel p-6 sm:p-8 space-y-6">
          {/* Brand Header */}
          <div className="text-center space-y-2">
            <div className="mx-auto p-3 rounded-2xl bg-primary/10 border border-primary/20 w-fit mb-2">
              <ShieldCheck className="h-6 w-6 text-primary" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">AI Operations Desk</h1>
            <p className="text-xs text-muted-foreground">Sign in to classify tickets and manage response workflows.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                <User className="h-3.5 w-3.5" /> Username
              </label>
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Enter username..."
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="bg-background/50 border-input pl-3 pr-3 py-2 text-sm focus:border-primary focus:ring-primary w-full"
                  required
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                <Lock className="h-3.5 w-3.5" /> Password
              </label>
              <div className="relative">
                <Input
                  type="password"
                  placeholder="Enter password..."
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-background/50 border-input pl-3 pr-3 py-2 text-sm focus:border-primary focus:ring-primary w-full"
                  required
                />
              </div>
            </div>

            {/* Action buttons */}
            <Button
              type="submit"
              className="w-full h-11 bg-primary hover:bg-primary/95 text-primary-foreground font-semibold shadow-lg shadow-primary/10 transition-all flex items-center justify-center gap-2 mt-2"
            >
              {isRegister ? (
                <>
                  <UserPlus className="h-4 w-4" /> Create Account <ArrowRight className="h-4 w-4" />
                </>
              ) : (
                <>
                  <KeyRound className="h-4 w-4" /> Log In <ArrowRight className="h-4 w-4" />
                </>
              )}
            </Button>
          </form>

          {/* Toggle Tab link */}
          <div className="text-center pt-2 border-t border-border/50">
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setPassword("");
              }}
              className="text-xs text-primary hover:underline font-medium"
            >
              {isRegister 
                ? "Already have an account? Sign In" 
                : "Need an account? Sign Up/Register"}
            </button>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
