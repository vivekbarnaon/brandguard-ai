"use client";

import React from "react";
import { ArrowRightIcon, CheckCircleIcon, ShieldIcon, SparklesIcon } from "./icons";

interface LandingPageProps {
  onGetStarted: () => void;
}

export function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="hero-glow pointer-events-none absolute -left-32 top-[-10rem] h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl" />
      <div className="hero-glow pointer-events-none absolute right-[-8rem] top-32 h-[28rem] w-[28rem] rounded-full bg-cyan-500/10 blur-3xl" />

      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500/15 text-indigo-300 ring-1 ring-indigo-400/30">
            <ShieldIcon className="h-5 w-5" />
          </div>
          <span className="text-sm font-bold tracking-wide text-white">BrandGuard AI</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500 sm:inline">
            Team Radhe Radhe
          </span>
          <button
            onClick={onGetStarted}
            className="rounded-xl border border-slate-700/80 bg-slate-900/50 px-4 py-2 text-xs font-semibold text-slate-200 transition hover:border-indigo-400/50 hover:bg-slate-800"
          >
            Sign in
          </button>
        </div>
      </header>

      <main className="relative z-10 mx-auto grid max-w-7xl items-center gap-16 px-6 pb-20 pt-12 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:pb-28 lg:pt-20">
        <section className="hero-fade-up">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-400/20 bg-indigo-500/10 px-3 py-1.5 text-[11px] font-semibold text-indigo-200">
            <SparklesIcon className="h-3.5 w-3.5" />
            AI-powered brand governance
          </div>
          <h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight text-white sm:text-6xl">
            Create with confidence.
            <span className="hero-gradient block bg-gradient-to-r from-indigo-300 via-cyan-200 to-white bg-clip-text text-transparent">
              Stay unmistakably on brand.
            </span>
          </h1>
          <p className="mt-6 max-w-xl text-base leading-7 text-slate-400 sm:text-lg">
            BrandGuard AI helps teams turn brand guidelines into everyday
            decisions, so every message is clear, consistent, and ready for
            approval.
          </p>
          <button
            onClick={onGetStarted}
            className="mt-8 inline-flex items-center gap-2 rounded-2xl bg-indigo-500 px-5 py-3.5 text-sm font-bold text-white shadow-xl shadow-indigo-950/50 transition hover:-translate-y-0.5 hover:bg-indigo-400"
          >
            Get started
            <ArrowRightIcon className="h-4 w-4" />
          </button>
          <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-xs text-slate-400">
            {["Guideline-aware AI", "Human approvals", "Evidence-backed decisions"].map(
              (item) => (
                <span key={item} className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-emerald-400" />
                  {item}
                </span>
              ),
            )}
          </div>
        </section>

        <section className="hero-float relative mx-auto w-full max-w-lg">
          <div className="absolute -inset-4 rounded-[2rem] bg-gradient-to-br from-indigo-500/20 to-cyan-400/10 blur-2xl" />
          <div className="hero-orbit pointer-events-none absolute -right-3 top-12 h-3 w-3 rounded-full bg-cyan-300 shadow-lg shadow-cyan-300/70" />
          <div className="hero-orbit pointer-events-none absolute -left-2 bottom-24 h-2 w-2 rounded-full bg-indigo-300 shadow-lg shadow-indigo-300/70" />
          <div className="glass-panel relative overflow-hidden rounded-[2rem] p-5 shadow-2xl shadow-black/30">
            <div className="hero-scan-line pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/80 to-transparent shadow-lg shadow-cyan-300/70" />
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-indigo-300">
                  Brand workspace
                </p>
                <h2 className="mt-1 text-lg font-bold text-white">Clarity at every step</h2>
              </div>
              <span className="rounded-full bg-emerald-400/10 px-2.5 py-1 text-[10px] font-semibold text-emerald-300">
                Protected
              </span>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {[
                ["01", "Upload guidelines", "Make your standards searchable."],
                ["02", "Create content", "Draft with your brand in mind."],
                ["03", "Review insights", "See evidence behind every flag."],
                ["04", "Approve confidently", "Keep people in the loop."],
              ].map(([number, title, description]) => (
                <div key={number} className="glass-card rounded-2xl p-4">
                  <span className="text-xs font-bold text-indigo-300">{number}</span>
                  <h3 className="mt-3 text-sm font-semibold text-white">{title}</h3>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{description}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 rounded-2xl border border-indigo-400/20 bg-indigo-500/10 p-4">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300">Brand consistency score</span>
                <span className="font-bold text-emerald-300">94%</span>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                <div className="h-full w-[94%] rounded-full bg-gradient-to-r from-indigo-500 to-cyan-300" />
              </div>
            </div>
          </div>
        </section>
      </main>

      <section id="how-it-works" className="relative z-10 border-y border-white/5 bg-slate-900/30 px-6 py-16 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-indigo-300">
              How it works
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              From brand guidelines to confident publishing.
            </h2>
            <p className="mt-4 text-sm leading-6 text-slate-400">
              BrandGuard turns static documents into an intelligent review layer
              for every piece of communication your team creates.
            </p>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-4">
            {[
              ["01", "Upload", "Add your approved brand guidelines and documents."],
              ["02", "Retrieve", "RAG finds the most relevant rules for each draft."],
              ["03", "Analyze", "Gemini checks voice, terminology, claims, and disclaimers."],
              ["04", "Approve", "Review evidence, accept suggestions, and keep humans in control."],
            ].map(([number, title, description]) => (
              <div key={number} className="glass-card rounded-2xl p-5">
                <span className="text-xs font-bold text-indigo-300">{number}</span>
                <h3 className="mt-5 text-sm font-bold text-white">{title}</h3>
                <p className="mt-2 text-xs leading-5 text-slate-400">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="relative z-10 mx-auto grid max-w-7xl gap-5 px-6 py-16 lg:grid-cols-2 lg:px-8">
        <div className="glass-panel rounded-3xl p-7">
          <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-rose-300">
            The challenge
          </p>
          <h2 className="mt-3 text-2xl font-bold text-white">
            Great teams should not have to police every sentence manually.
          </h2>
          <p className="mt-4 text-sm leading-6 text-slate-400">
            Long guidelines, inconsistent reviews, missed terminology, and
            unsupported claims slow teams down and put brand trust at risk.
          </p>
        </div>
        <div className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-7">
          <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-emerald-300">
            Our approach
          </p>
          <h2 className="mt-3 text-2xl font-bold text-white">
            Evidence-backed AI with a human final say.
          </h2>
          <p className="mt-4 text-sm leading-6 text-slate-300">
            Every finding is grounded in your own approved guidance, with
            explainable suggestions and an approval workflow built for teams.
          </p>
        </div>
      </section>

      <section className="relative z-10 px-6 pb-16 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-cyan-300">
              What&apos;s next
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-white">
              Built today. Ready for what&apos;s next.
            </h2>
            <p className="mt-4 text-sm leading-6 text-slate-400">
              Our roadmap expands BrandGuard from content compliance into a
              complete visual and collaborative brand intelligence layer.
            </p>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              [
                "01",
                "Smarter AI explainability",
                "Improve retrieval quality with stronger evidence links, confidence indicators, and fewer false positives.",
                "from-indigo-400 to-violet-300",
              ],
              [
                "02",
                "Multimodal compliance",
                "Check images, logos, colours, and accessibility alongside written brand communication.",
                "from-cyan-300 to-blue-300",
              ],
              [
                "03",
                "Governance analytics",
                "Bring collaboration, audit trails, approval history, and recurring violation insights into one view.",
                "from-emerald-300 to-teal-200",
              ],
            ].map(([number, title, description, gradient]) => (
              <div key={number} className="glass-card-interactive rounded-2xl p-5">
                <span className={`bg-gradient-to-r ${gradient} bg-clip-text text-xs font-bold text-transparent`}>
                  {number}
                </span>
                <h3 className="mt-4 text-base font-bold text-white">{title}</h3>
                <p className="mt-2 text-xs leading-5 text-slate-400">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="relative z-10 px-6 pb-16 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-5 rounded-3xl border border-indigo-400/20 bg-gradient-to-r from-indigo-500/15 to-cyan-400/10 p-7 sm:flex-row sm:items-center">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-indigo-200">
              Built for CodeZen India 2026
            </p>
            <h2 className="mt-2 text-xl font-bold text-white">
              Meet BrandGuard AI by Team Radhe Radhe.
            </h2>
            <p className="mt-2 text-xs text-slate-400">
              AI / Generative AI &bull; Responsible automation &bull; Human-in-the-loop governance
            </p>
          </div>
          <button
            onClick={onGetStarted}
            className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-indigo-500 px-4 py-3 text-xs font-bold text-white transition hover:bg-indigo-400"
          >
            Explore the workspace
            <ArrowRightIcon className="h-4 w-4" />
          </button>
        </div>
      </section>

      <footer className="relative z-10 border-t border-white/5 px-6 py-5 text-center text-xs text-slate-500">
        BrandGuard AI &bull; Team Radhe Radhe &bull; CodeZen India 2026
      </footer>
    </div>
  );
}
