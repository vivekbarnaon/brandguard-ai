"use client";

import React, { useState } from "react";
import {
  ApprovalDecision,
  ApprovalRecord,
  ComplianceReport,
  ContentItem,
  Role,
} from "../lib/types";
import { apiClient } from "../lib/api";
import { StatusBadge } from "./Badges";
import {
  UserCheckIcon,
  CheckCircleIcon,
  XCircleIcon,
  AlertTriangleIcon,
  ClockIcon,
  EyeIcon,
  RefreshCwIcon,
} from "./icons";

interface ApprovalHubProps {
  contents: ContentItem[];
  userRole: Role;
  onRefresh: () => void;
}

export function ApprovalHub({
  contents,
  userRole,
  onRefresh,
}: ApprovalHubProps) {
  const [filter, setFilter] = useState<string>("SUBMITTED");
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null);
  const [selectedReport, setSelectedReport] = useState<ComplianceReport | null>(null);
  const [comments, setComments] = useState("");
  const [history, setHistory] = useState<ApprovalRecord[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const canReview =
    userRole === "BRAND_REVIEWER" || userRole === "MANAGER" || userRole === "ADMIN";

  const filteredContents = contents.filter((c) => {
    if (filter === "ALL") return true;
    return c.status === filter;
  });

  const handleOpenReview = async (item: ContentItem) => {
    setSelectedContent(item);
    setSelectedReport(null);
    setComments("");
    setFeedbackMsg(null);
    try {
      const [records, reports] = await Promise.all([
        apiClient.getApprovalHistory(item.id),
        apiClient.listComplianceReports(item.organisation_id),
      ]);
      setHistory(records);
      setSelectedReport(
        reports.find((report) => report.content_id === item.id) || null
      );
    } catch {
      setHistory([]);
      setFeedbackMsg({
        type: "error",
        text: "Unable to load the compliance report for this submission.",
      });
    }
  };

  const handleMakeDecision = async (decision: ApprovalDecision) => {
    if (!selectedContent) return;

    if (decision === "REVISION_REQUESTED" && !comments.trim()) {
      setFeedbackMsg({
        type: "error",
        text: "Please provide comments explaining what revisions are required.",
      });
      return;
    }

    setIsSubmitting(true);
    setFeedbackMsg(null);

    try {
      await apiClient.reviewApproval(selectedContent.id, decision, comments);
      setFeedbackMsg({
        type: "success",
        text: `Successfully recorded decision: ${decision}!`,
      });
      const updated = await apiClient.getApprovalHistory(selectedContent.id);
      setHistory(updated);
      onRefresh();
    } catch (err: unknown) {
      setFeedbackMsg({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to record approval decision.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <UserCheckIcon className="w-6 h-6 text-indigo-400" />
            <span>Human-in-the-Loop Approval Hub</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Authorised human reviewers have final approval authority. Review AI compliance reports and decide next steps.
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

      {/* Permission Notice */}
      {!canReview && (
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 text-xs flex items-center gap-2">
          <AlertTriangleIcon className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            You are viewing in <strong className="text-slate-200">{userRole}</strong> mode. 
            Creators can view their submission statuses here. Making approval decisions requires <strong>BRAND_REVIEWER</strong> or <strong>MANAGER</strong> role.
          </span>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "SUBMITTED", label: "Pending Approvals" },
          { id: "APPROVED", label: "Approved" },
          { id: "REVISION_REQUESTED", label: "Revisions Requested" },
          { id: "REJECTED", label: "Rejected" },
          { id: "ALL", label: "All Submissions" },
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

      {/* Submissions List */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="divide-y divide-slate-800/80">
          {filteredContents.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">
              No content submissions found in this status category.
            </div>
          ) : (
            filteredContents.map((item) => (
              <div
                key={item.id}
                className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-900/40 transition-colors"
              >
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <h3 className="text-base font-semibold text-white truncate">
                      {item.title}
                    </h3>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      v{item.version}
                    </span>
                    <StatusBadge status={item.status} />
                  </div>

                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {item.body}
                  </p>

                  <div className="flex items-center gap-3 text-[11px] text-slate-500 pt-1">
                    <span>Added {new Date(item.created_at).toLocaleDateString()}</span>
                    {item.latest_report && (
                      <>
                        <span>&bull;</span>
                        <span className="font-semibold text-indigo-400">
                          AI Score: {item.latest_report.score}/100
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end md:self-auto shrink-0">
                  <button
                    onClick={() => handleOpenReview(item)}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 shadow-sm cursor-pointer"
                  >
                    <EyeIcon className="w-3.5 h-3.5" />
                    <span>{canReview ? "Review & Decide" : "View Details"}</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Review Modal / Drawer */}
      {selectedContent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-4xl rounded-2xl border border-slate-700 p-6 space-y-6 max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-lg font-bold text-white">
                    {selectedContent.title}
                  </h3>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    Version {selectedContent.version}
                  </span>
                  <StatusBadge status={selectedContent.status} />
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Submitted on {new Date(selectedContent.created_at).toLocaleString()}
                </p>
              </div>

              <button
                onClick={() => setSelectedContent(null)}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 cursor-pointer"
              >
                Close
              </button>
            </div>

            {/* Modal Feedback Message */}
            {feedbackMsg && (
              <div
                className={`p-3 rounded-xl text-xs flex items-center gap-2 border ${
                  feedbackMsg.type === "success"
                    ? "bg-emerald-950/60 border-emerald-800/60 text-emerald-300"
                    : "bg-rose-950/60 border-rose-800/60 text-rose-300"
                }`}
              >
                {feedbackMsg.type === "success" ? (
                  <CheckCircleIcon className="w-4 h-4 text-emerald-400" />
                ) : (
                  <AlertTriangleIcon className="w-4 h-4 text-rose-400" />
                )}
                <span>{feedbackMsg.text}</span>
              </div>
            )}

            {/* Modal Content Split Body */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 overflow-y-auto pr-1">
              {/* Left: Submitted Content Copy */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Submitted Marketing Content
                </h4>
                <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-200 text-xs leading-relaxed font-sans whitespace-pre-wrap">
                  {selectedContent.body}
                </div>

                {/* Prior Approval History Timeline */}
                <div className="space-y-2 pt-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Review History ({history.length})
                  </h4>
                  {history.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">
                      No review actions recorded yet.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {history.map((rec) => (
                        <div
                          key={rec.id}
                          className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-slate-300">
                              Reviewer ID: {rec.reviewer_id.slice(0, 8)}...
                            </span>
                            <StatusBadge status={rec.decision} />
                          </div>
                          {rec.comments && (
                            <p className="text-slate-400 italic">
                              &ldquo;{rec.comments}&rdquo;
                            </p>
                          )}
                          <p className="text-[10px] text-slate-500">
                            {new Date(rec.created_at).toLocaleString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Right: AI Compliance Findings & Reviewer Controls */}
              <div className="space-y-4">
                {selectedReport ? (
                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">AI Compliance Score</span>
                      <span className="text-sm font-extrabold text-indigo-400">
                        {selectedReport.score}/100
                      </span>
                    </div>

                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {selectedReport.findings.map((f, i) => (
                        <div
                          key={i}
                          className="p-2.5 rounded bg-slate-950/80 border border-slate-800 text-[11px] space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-300">{f.category}</span>
                            <span className="text-rose-400 font-semibold">{f.severity}</span>
                          </div>
                          <p className="text-slate-400">{f.explanation}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic">
                    No compliance report attached to this content.
                  </p>
                )}

                {/* Reviewer Action Decision Panel (Only if authorized) */}
                {canReview && (
                  <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-800/40 space-y-3">
                    <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                      <UserCheckIcon className="w-4 h-4 text-indigo-400" />
                      <span>Reviewer Decision & Feedback</span>
                    </h4>

                    <textarea
                      rows={3}
                      value={comments}
                      onChange={(e) => setComments(e.target.value)}
                      placeholder="Add reviewer comments or specific revision instructions..."
                      className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    />

                    <div className="flex flex-wrap items-center gap-2 pt-1">
                      <button
                        disabled={isSubmitting}
                        onClick={() => handleMakeDecision("APPROVED")}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 cursor-pointer disabled:opacity-50"
                      >
                        <CheckCircleIcon className="w-3.5 h-3.5" />
                        <span>Approve Copy</span>
                      </button>

                      <button
                        disabled={isSubmitting}
                        onClick={() => handleMakeDecision("REVISION_REQUESTED")}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-amber-300 bg-amber-950/60 border border-amber-800/60 hover:bg-amber-900/60 cursor-pointer disabled:opacity-50"
                      >
                        <ClockIcon className="w-3.5 h-3.5" />
                        <span>Request Revision</span>
                      </button>

                      <button
                        disabled={isSubmitting}
                        onClick={() => handleMakeDecision("REJECTED")}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-rose-300 bg-rose-950/60 border border-rose-800/60 hover:bg-rose-900/60 cursor-pointer disabled:opacity-50"
                      >
                        <XCircleIcon className="w-3.5 h-3.5" />
                        <span>Reject</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
