"use client";

import React, { useState } from "react";
import { AuditLogItem } from "../lib/types";
import { ClockIcon, RefreshCwIcon, FileTextIcon, UserCheckIcon, ShieldIcon } from "./icons";

interface AuditTrailProps {
  logs: AuditLogItem[];
  onRefresh: () => void;
}

export function AuditTrail({ logs, onRefresh }: AuditTrailProps) {
  const [filter, setFilter] = useState("ALL");

  const filteredLogs = logs.filter((log) => {
    if (filter === "ALL") return true;
    return log.action.includes(filter);
  });

  const getActionBadge = (action: string) => {
    if (action.includes("approved")) {
      return "bg-emerald-950/60 text-emerald-400 border-emerald-800/50";
    }
    if (action.includes("rejected")) {
      return "bg-rose-950/60 text-rose-400 border-rose-800/50";
    }
    if (action.includes("revision")) {
      return "bg-amber-950/60 text-amber-400 border-amber-800/50";
    }
    if (action.includes("compliance") || action.includes("analyzed")) {
      return "bg-indigo-950/60 text-indigo-400 border-indigo-800/50";
    }
    if (action.includes("uploaded")) {
      return "bg-blue-950/60 text-blue-400 border-blue-800/50";
    }
    return "bg-slate-900 text-slate-300 border-slate-700/60";
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <ClockIcon className="w-6 h-6 text-indigo-400" />
            <span>Immutable Governance Audit Trail</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Complete compliance event log tracking guideline uploads, AI analyses, submissions, and human approvals.
          </p>
        </div>

        <button
          onClick={onRefresh}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 cursor-pointer self-start sm:self-auto"
        >
          <RefreshCwIcon className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "ALL", label: "All Audit Events" },
          { id: "reviewed", label: "Approval Decisions" },
          { id: "compliance", label: "AI Analysis" },
          { id: "content", label: "Content Changes" },
          { id: "document", label: "Guideline Uploads" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              filter === tab.id
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="divide-y divide-slate-800/80">
          {filteredLogs.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">
              No audit records matching this filter.
            </div>
          ) : (
            filteredLogs.map((log) => (
              <div
                key={log.id}
                className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-900/40 transition-colors"
              >
                <div className="flex items-start gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                    <ShieldIcon className="w-4 h-4" />
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-bold text-white">{log.user_name || `User ${log.user_id.slice(0, 8)}`}</span>
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${getActionBadge(
                          log.action
                        )}`}
                      >
                        {log.action}
                      </span>
                    </div>

                    {log.metadata_json && Object.keys(log.metadata_json).length > 0 && (
                      <p className="text-[11px] font-mono text-slate-400 truncate max-w-xl">
                        {JSON.stringify(log.metadata_json)}
                      </p>
                    )}
                  </div>
                </div>

                <div className="text-right sm:self-center shrink-0">
                  <span className="text-xs text-slate-400 font-medium">
                    {new Date(log.timestamp).toLocaleDateString()}{" "}
                    {new Date(log.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
