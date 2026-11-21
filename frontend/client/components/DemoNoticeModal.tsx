"use client";

import React, { useEffect, useState } from "react";
import { ArrowRightIcon, ShieldIcon, SparklesIcon } from "./icons";

interface DemoNoticeModalProps {
  onAction?: () => void;
}

export function DemoNoticeModal({ onAction }: DemoNoticeModalProps) {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Show automatically for any new browser session unless dismissed
    const dismissed = sessionStorage.getItem("brandguard_demo_notice_dismissed");
    if (!dismissed) {
      setIsOpen(true);
    }
  }, []);

  const handleClose = () => {
    sessionStorage.setItem("brandguard_demo_notice_dismissed", "true");
    setIsOpen(false);
  };

  const handleAction = () => {
    handleClose();
    if (onAction) {
      onAction();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      onClick={handleAction}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-md animate-in fade-in duration-300"
    >
      {/* Modal Container */}
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-xl overflow-hidden rounded-[2rem] border border-white/20 bg-gradient-to-br from-purple-900/95 via-indigo-900/95 to-pink-800/90 p-6 text-white shadow-2xl shadow-purple-950/80 sm:p-8"
      >
        {/* Glow Accents */}
        <div className="pointer-events-none absolute -left-12 -top-12 h-40 w-40 rounded-full bg-pink-500/30 blur-2xl" />
        <div className="pointer-events-none absolute -bottom-12 -right-12 h-48 w-48 rounded-full bg-cyan-400/20 blur-2xl" />

        {/* Close Button ('X') at Top Right */}
        <button
          onClick={handleClose}
          aria-label="Close demo notice"
          className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full bg-white/15 text-white/90 backdrop-blur-sm transition-all hover:scale-105 hover:bg-white/25 hover:text-white"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2.5}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Modal Content Grid */}
        <div className="relative z-10 grid gap-6 sm:grid-cols-[1.25fr_0.75fr] sm:items-center">
          {/* Left: Text Content */}
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-pink-300/30 bg-pink-500/20 px-3 py-1 text-[11px] font-semibold text-pink-200">
              <SparklesIcon className="h-3 w-3" />
              <span>CodeZen India 2026 • Demo Site</span>
            </div>

            <h3 className="text-xl font-bold leading-snug tracking-tight sm:text-2xl">
              BrandGuard AI is a <span className="underline decoration-pink-400 decoration-2 underline-offset-2">Demo Platform</span> built for the CodeZen India hackathon.
            </h3>

            <p className="text-xs leading-relaxed text-purple-100/90 sm:text-sm">
              Please <strong className="font-semibold text-white">do not</strong> use it for real production or legal compliance without official human review.
            </p>

            <p className="text-[11px] leading-relaxed text-purple-200/80">
              Designed &amp; built by <strong className="text-white font-medium">Team RADHE RADHE</strong>. Test with sample brand guidelines and marketing drafts to experience real-time AI compliance auditing.
            </p>

            {/* Action Buttons & Links */}
            <div className="pt-2 flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <button
                onClick={handleAction}
                className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-bold text-purple-950 shadow-lg shadow-black/30 transition-all hover:-translate-y-0.5 hover:bg-purple-50 hover:shadow-xl"
              >
                <span>Explore Demo</span>
                <ArrowRightIcon className="h-3.5 w-3.5" />
              </button>

              <button
                onClick={handleClose}
                className="text-[11px] font-medium text-purple-200 underline underline-offset-4 hover:text-white transition-colors"
              >
                Dismiss &amp; Continue
              </button>
            </div>
          </div>

          {/* Right: 3D-styled Visual Graphic / Siren-Shield Badge */}
          <div className="flex items-center justify-center sm:justify-end">
            <div className="relative flex h-32 w-32 items-center justify-center">
              {/* Outer Pulsing Waves / Rings */}
              <div className="absolute inset-0 animate-ping rounded-full bg-pink-500/20 duration-1000" />
              <div className="absolute -inset-2 rounded-full border border-pink-400/40 bg-pink-500/10 blur-sm" />

              {/* Central 3D Siren / Shield Glow Base */}
              <div className="relative flex h-28 w-28 items-center justify-center rounded-3xl border border-white/30 bg-gradient-to-tr from-pink-600 via-rose-500 to-amber-400 p-4 shadow-2xl shadow-rose-500/50">
                {/* Inner Light Flare */}
                <div className="absolute left-2 top-2 h-6 w-12 -rotate-45 rounded-full bg-white/40 blur-[2px]" />

                <div className="flex flex-col items-center justify-center text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20 text-white shadow-inner backdrop-blur-sm">
                    <ShieldIcon className="h-7 w-7 text-white drop-shadow" />
                  </div>
                  <span className="mt-1 text-[9px] font-extrabold uppercase tracking-widest text-white/90">
                    Demo Mode
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="relative z-10 mt-5 border-t border-white/10 pt-3 text-[10px] text-purple-200/70 flex items-center justify-between">
          <span>BrandGuard AI &copy; 2026 Team RADHE RADHE</span>
          <span>CodeZen India Hackathon</span>
        </div>
      </div>
    </div>
  );
}
