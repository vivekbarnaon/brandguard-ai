import React from "react";
import { ContentStatus, OverallStatus, ProcessingStatus, Severity, ViolationCategory } from "../lib/types";

export function SeverityBadge({ severity }: { severity: Severity }) {
  const styles: Record<Severity, string> = {
    CRITICAL: "bg-red-950/70 text-red-400 border-red-800/60 shadow-[0_0_12px_rgba(239,68,68,0.2)]",
    HIGH: "bg-rose-950/60 text-rose-400 border-rose-800/50",
    MEDIUM: "bg-amber-950/60 text-amber-400 border-amber-800/50",
    LOW: "bg-blue-950/60 text-blue-400 border-blue-800/50",
    INFO: "bg-slate-900 text-slate-300 border-slate-700/50",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-semibold tracking-wide uppercase border ${
        styles[severity] || styles.INFO
      }`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {severity}
    </span>
  );
}

export function CategoryBadge({ category }: { category: ViolationCategory }) {
  const labels: Record<ViolationCategory, string> = {
    BRAND_VOICE: "Brand Voice",
    TERMINOLOGY: "Terminology",
    PROHIBITED_LANGUAGE: "Prohibited Language",
    UNSUPPORTED_CLAIM: "Unsupported Claim",
    PRODUCT_ACCURACY: "Product Accuracy",
    DISCLAIMER: "Missing Disclaimer",
    MESSAGING: "Messaging Consistency",
    OTHER: "General Compliance",
  };

  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800/80 text-slate-300 border border-slate-700/60">
      {labels[category] || category}
    </span>
  );
}

export function StatusBadge({ status }: { status: ContentStatus | OverallStatus | ProcessingStatus }) {
  let badgeStyle = "bg-slate-800 text-slate-300 border-slate-700";
  let label = status;

  switch (status) {
    case "APPROVED":
    case "COMPLIANT":
    case "PROCESSED":
      badgeStyle = "bg-emerald-950/60 text-emerald-300 border-emerald-800/60";
      break;
    case "REJECTED":
    case "NON_COMPLIANT":
    case "FAILED":
      badgeStyle = "bg-rose-950/60 text-rose-300 border-rose-800/60";
      break;
    case "REVISION_REQUESTED":
    case "NEEDS_REVIEW":
      badgeStyle = "bg-amber-950/60 text-amber-300 border-amber-800/60";
      break;
    case "SUBMITTED":
    case "PROCESSING":
      badgeStyle = "bg-indigo-950/60 text-indigo-300 border-indigo-800/60 animate-pulse";
      break;
    case "ANALYZED":
      badgeStyle = "bg-purple-950/60 text-purple-300 border-purple-800/60";
      break;
    case "DRAFT":
    case "PENDING":
      badgeStyle = "bg-slate-800/70 text-slate-400 border-slate-700/50";
      break;
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeStyle}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {label.replace("_", " ")}
    </span>
  );
}
