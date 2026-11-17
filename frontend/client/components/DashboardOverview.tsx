"use client";

import React from "react";
import { DashboardMetrics, Role } from "../lib/types";
import { ScoreRing } from "./ScoreRing";
import {
  FileTextIcon,
  LayersIcon,
  UserCheckIcon,
  SparklesIcon,
  ArrowRightIcon,
  ClockIcon,
  UploadCloudIcon,
} from "./icons";

interface DashboardOverviewProps {
  metrics: DashboardMetrics;
  userRole: Role;
  onNavigate: (tab: string) => void;
}

export function DashboardOverview({
  metrics,
  userRole,
  onNavigate,
}: DashboardOverviewProps) {
  const avgScore = metrics.average_score ?? 0;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Welcome & Quick Stats Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-indigo-950/40 p-6 sm:p-8 backdrop-blur-xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <SparklesIcon className="w-3.5 h-3.5" />
              <span>AI-Powered Brand Governance</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Enterprise Brand Consistency & Compliance
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              BrandGuard AI automatically evaluates marketing copy against your official brand guidelines, 
              flags terminology and tone inconsistencies with citations, and keeps final approvals in human hands.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigate("studio")}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-xs text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
            >
              <SparklesIcon className="w-4 h-4" />
              <span>Open Content Studio</span>
            </button>
            <button
              onClick={() => onNavigate("guidelines")}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-xs text-slate-200 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition-all cursor-pointer"
            >
              <UploadCloudIcon className="w-4 h-4" />
              <span>Upload Guidelines</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Average Compliance Score Card */}
        <div className="glass-panel p-5 rounded-2xl flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Avg Compliance Score
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-white">{avgScore}</span>
              <span className="text-xs font-medium text-emerald-400">/ 100</span>
            </div>
            <p className="text-[11px] text-slate-400">Across evaluated marketing copy</p>
          </div>
          <div className="scale-75 origin-right">
            <ScoreRing score={avgScore} size={84} strokeWidth={8} showStatus={false} />
          </div>
        </div>

        {/* Pending Approvals Card */}
        <div
          onClick={() => onNavigate("approvals")}
          className="glass-card-interactive p-5 rounded-2xl cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Pending Approvals
            </p>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 border border-amber-500/20">
              <ClockIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{metrics.pending_approvals}</span>
            <span className="text-xs text-amber-400 font-medium">Awaiting review</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400 flex items-center gap-1 text-indigo-400">
            <span>Review now</span>
            <ArrowRightIcon className="w-3 h-3" />
          </p>
        </div>

        {/* Brand Guidelines Ingested Card */}
        <div
          onClick={() => onNavigate("guidelines")}
          className="glass-card-interactive p-5 rounded-2xl cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Brand Guidelines
            </p>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
              <LayersIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{metrics.documents}</span>
            <span className="text-xs text-indigo-400 font-medium">Uploaded documents</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">Indexed in vector knowledge</p>
        </div>

        {/* Content Submissions */}
        <div
          onClick={() => onNavigate("studio")}
          className="glass-card-interactive p-5 rounded-2xl cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Total Submissions
            </p>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 border border-purple-500/20">
              <FileTextIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-black text-white">{metrics.content}</span>
            <span className="text-xs text-slate-400 font-medium">
              {metrics.reports} reports generated
            </span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">From all content creators</p>
        </div>
      </div>

      {/* Main Insights Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Health Breakdown */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white">Brand Rule Evaluation Engine</h2>
              <p className="text-xs text-slate-400">
                Core check categories evaluated by Google Gemini & LangChain RAG
              </p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Qdrant Vector Indexed
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                <h4 className="text-xs font-bold text-slate-200">Brand Voice & Tone</h4>
              </div>
              <p className="text-xs text-slate-400">
                Checks tone against premium, elevated, and inclusive voice standards.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-indigo-400" />
                <h4 className="text-xs font-bold text-slate-200">Approved Terminology</h4>
              </div>
              <p className="text-xs text-slate-400">
                Enforces canonical naming conventions and flag deprecated words.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-amber-400" />
                <h4 className="text-xs font-bold text-slate-200">Claims & Superlatives</h4>
              </div>
              <p className="text-xs text-slate-400">
                Catches unverified claims (&apos;undisputed&apos;, &apos;fastest&apos;, &apos;100% guarantee&apos;).
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-rose-400" />
                <h4 className="text-xs font-bold text-slate-200">Mandatory Disclaimers</h4>
              </div>
              <p className="text-xs text-slate-400">
                Ensures regulatory, health, and financial caveats are never omitted.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-800/40 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <UserCheckIcon className="w-5 h-5 text-indigo-400" />
              <div>
                <p className="text-xs font-bold text-white">Human Approval Authority</p>
                <p className="text-[11px] text-slate-300">
                  AI generates evidence & suggestions; final approval decisions are reserved strictly for human reviewers.
                </p>
              </div>
            </div>
            <button
              onClick={() => onNavigate("approvals")}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold text-indigo-300 bg-indigo-500/10 border border-indigo-500/30 hover:bg-indigo-500/20 cursor-pointer whitespace-nowrap"
            >
              View Approvals
            </button>
          </div>
        </div>

        {/* Quick Guide Card */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <div>
            <h2 className="text-base font-bold text-white pb-3 border-b border-slate-800">
              Workflow Status
            </h2>
            <div className="mt-4 space-y-3 text-xs text-slate-300">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <p className="font-semibold text-white">1. Guidelines</p>
                <p className="text-[11px] text-slate-400">
                  {metrics.documents > 0
                    ? `${metrics.documents} brand guidelines uploaded and ready.`
                    : "No guidelines uploaded. Upload a PDF guideline to begin."}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <p className="font-semibold text-white">2. Content & Analysis</p>
                <p className="text-[11px] text-slate-400">
                  {metrics.content > 0
                    ? `${metrics.content} content draft(s) with ${metrics.reports} reports generated.`
                    : "Create campaign copy in Content Studio to evaluate compliance."}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <p className="font-semibold text-white">3. Review & Approval</p>
                <p className="text-[11px] text-slate-400">
                  {metrics.pending_approvals > 0
                    ? `${metrics.pending_approvals} submission(s) awaiting reviewer clearance.`
                    : "No pending approval requests."}
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80">
            <p className="text-[11px] text-slate-400 text-center">
              Active Role: <span className="text-indigo-300 font-semibold">{userRole}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
