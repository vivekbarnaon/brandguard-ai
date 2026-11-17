"use client";

import React, { useState } from "react";
import { ShieldIcon } from "./icons";
import { apiClient } from "../lib/api";

interface AuthModalProps {
  onClose: () => void;
  onAuthenticated: (email: string) => void;
}

export function AuthModal({ onClose, onAuthenticated }: AuthModalProps) {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!email.trim() || !password) {
      setErrorMessage("Enter your email and password.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      if (mode === "signin") {
        await apiClient.signIn(email.trim(), password);
        onAuthenticated(email.trim());
      } else {
        const signedIn = await apiClient.signUp(email.trim(), password);
        if (signedIn) {
          onAuthenticated(email.trim());
        } else {
          setMode("signin");
          setSuccessMessage(
            "Account created. Check your email to confirm your account, then sign in."
          );
        }
      }
    } catch (error: unknown) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-md">
      <div className="glass-panel w-full max-w-md rounded-3xl p-6 shadow-2xl shadow-black/50 sm:p-8">
        <div className="flex items-start justify-between">
          <div>
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-indigo-500/15 text-indigo-300 ring-1 ring-indigo-400/30">
              <ShieldIcon className="h-5 w-5" />
            </div>
            <h2 className="text-xl font-bold text-white">
              {mode === "signin" ? "Welcome back" : "Create your account"}
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              {mode === "signin"
                ? "Sign in to enter your brand workspace."
                : "Create an account to start protecting your brand."}
            </p>
          </div>
          <button onClick={onClose} className="rounded-lg px-2 py-1 text-slate-400 hover:bg-white/10 hover:text-white">
            <span className="sr-only">Close</span>
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-7 space-y-4">
          <label className="block text-xs font-semibold text-slate-300">
            Work email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950/60 px-3.5 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-indigo-400"
            />
          </label>
          <label className="block text-xs font-semibold text-slate-300">
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Your password"
              autoComplete="current-password"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950/60 px-3.5 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-indigo-400"
            />
          </label>
          {errorMessage && (
            <p className="rounded-xl border border-rose-800/60 bg-rose-950/40 p-3 text-xs text-rose-300">
              {errorMessage}
            </p>
          )}
          {successMessage && (
            <p className="rounded-xl border border-emerald-800/60 bg-emerald-950/40 p-3 text-xs text-emerald-300">
              {successMessage}
            </p>
          )}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-indigo-500 px-4 py-3 text-sm font-bold text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting
              ? mode === "signin"
                ? "Signing in..."
                : "Creating account..."
              : mode === "signin"
                ? "Sign in to BrandGuard"
                : "Create account"}
          </button>
        </form>
        <p className="mt-5 text-center text-xs text-slate-500">
          {mode === "signin" ? "New to BrandGuard?" : "Already have an account?"}{" "}
          <button
            type="button"
            onClick={() => {
              setMode(mode === "signin" ? "signup" : "signin");
              setErrorMessage(null);
              setSuccessMessage(null);
            }}
            className="font-semibold text-indigo-300 hover:text-indigo-200"
          >
            {mode === "signin" ? "Create an account" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}
