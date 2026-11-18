"use client";

import React from "react";
import { ArrowRightIcon, CheckCircleIcon, ShieldIcon } from "./icons";
import { Role } from "../lib/types";

interface ProfileCardProps {
  email: string;
  role?: Role;
  onContinue: () => void;
}

export function ProfileCard({ email, role = "ADMIN", onContinue }: ProfileCardProps) {
  const displayName = email.split("@")[0].replace(/[._-]/g, " ");
  const name = displayName.replace(/\b\w/g, (letter) => letter.toUpperCase());

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950 px-4 py-12 text-slate-100">
      <div className="pointer-events-none absolute h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl" />
      <div className="glass-panel relative w-full max-w-md rounded-3xl p-7 text-center shadow-2xl shadow-black/40 sm:p-9">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-400 to-cyan-300 text-2xl font-bold text-slate-950 shadow-lg shadow-indigo-950/50">
          {name.charAt(0)}
        </div>
        <p className="mt-6 text-[10px] font-bold uppercase tracking-[0.25em] text-indigo-300">
          Profile ready &bull; {role}
        </p>
        <h1 className="mt-2 text-2xl font-bold text-white">Welcome, {name}</h1>
        <p className="mt-2 text-sm text-slate-400">{email}</p>
        <div className="mt-7 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4 text-left">
          <div className="flex items-center gap-2 text-sm font-semibold text-emerald-200">
            <CheckCircleIcon className="h-4 w-4" />
            {role === "ADMIN" ? "Administrator workspace access enabled" : `${role} workspace access enabled`}
          </div>
          <p className="mt-2 text-xs leading-5 text-slate-400">
            {role === "ADMIN"
              ? "You have full administrator privileges: content creation, guideline upload, reviews, and team role management."
              : "Your brand guidelines, content, and approvals are ready in one place."}
          </p>
        </div>
        <button
          onClick={onContinue}
          className="mt-7 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-500 px-4 py-3 text-sm font-bold text-white transition hover:bg-indigo-400"
        >
          Open workspace
          <ArrowRightIcon className="h-4 w-4" />
        </button>
        <div className="mt-5 flex items-center justify-center gap-2 text-[11px] text-slate-500">
          <ShieldIcon className="h-3.5 w-3.5" />
          Protected by BrandGuard AI
        </div>
      </div>
    </div>
  );
}
