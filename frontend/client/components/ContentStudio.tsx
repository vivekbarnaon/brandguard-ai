"use client";

import React, { useEffect, useState } from "react";
import {
  ComplianceReport,
  ContentItem,
  RewriteMode,
  Role,
  SuggestionResponse,
} from "../lib/types";
import { apiClient } from "../lib/api";
import { ScoreRing } from "./ScoreRing";
import { CategoryBadge, SeverityBadge } from "./Badges";
import {
  SparklesIcon,
  SendIcon,
  CheckIcon,
  RefreshCwIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  InfoIcon,
  SlidersIcon,
} from "./icons";

interface ContentStudioProps {
  contents: ContentItem[];
  userRole: Role;
  activeOrgId: string;
  onRefresh: () => void;
  onNavigateToApprovals: () => void;
}

export function ContentStudio({
  contents,
  userRole,
  activeOrgId,
  onRefresh,
  onNavigateToApprovals,
}: ContentStudioProps) {
  const [selectedContentId, setSelectedContentId] = useState<string>(
    contents[0]?.id || ""
  );

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentReport, setCurrentReport] = useState<ComplianceReport | undefined>(undefined);
  const [suggestions, setSuggestions] = useState<SuggestionResponse | null>(null);
  const [rewriteMode, setRewriteMode] = useState<RewriteMode>("minimal_correction");
  const [notification, setNotification] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Sync state when active content selection or contents list changes
  useEffect(() => {
    if (contents.length > 0) {
      const match = contents.find((c) => c.id === selectedContentId) || contents[0];
      setSelectedContentId(match.id);
      setTitle(match.title);
      setBody(match.body);
      setCurrentReport(match.latest_report);
    } else {
      setSelectedContentId("");
      setTitle("");
      setBody("");
      setCurrentReport(undefined);
    }
  }, [contents, selectedContentId]);

  const handleSelectContent = (id: string) => {
    setSelectedContentId(id);
    const item = contents.find((c) => c.id === id);
    if (item) {
      setTitle(item.title);
      setBody(item.body);
      setCurrentReport(item.latest_report);
      setSuggestions(null);
    }
  };

  const handleCreateNew = () => {
    setSelectedContentId("");
    setTitle("");
    setBody("");
    setCurrentReport(undefined);
    setSuggestions(null);
  };

  const handleRunAnalysis = async () => {
    if (!body.trim()) {
      setNotification({ type: "error", text: "Please enter content body to evaluate." });
      return;
    }

    if (!activeOrgId) {
      setNotification({ type: "error", text: "Please select an organisation first." });
      return;
    }

    setIsAnalyzing(true);
    setNotification(null);

    try {
      let targetId = selectedContentId;
      if (!targetId) {
        const created = await apiClient.createContent(
          title.trim() || "Untitled Campaign Copy",
          body,
          activeOrgId
        );
        targetId = created.id;
        setSelectedContentId(targetId);
      } else {
        await apiClient.updateContent(targetId, title.trim() || "Untitled Campaign Copy", body);
      }

      const report = await apiClient.analyzeCompliance(targetId);
      setCurrentReport(report);
      setSuggestions(null);
      setNotification({
        type: "success",
        text: `Analysis complete! Score: ${report.score}/100`,
      });
    } catch (err: unknown) {
      setNotification({
        type: "error",
        text: err instanceof Error ? err.message : "Error running compliance analysis.",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerateSuggestions = async () => {
    if (!selectedContentId || !currentReport || currentReport.findings.length === 0) {
      setNotification({
        type: "error",
        text: "Run analysis first to identify findings before generating suggestions.",
      });
      return;
    }

    setIsGeneratingSuggestions(true);
    try {
      const res = await apiClient.generateSuggestions(selectedContentId, rewriteMode);
      setSuggestions(res);
      setNotification({
        type: "success",
        text: `Generated ${res.suggestions.length} AI correction suggestions.`,
      });
    } catch (err: unknown) {
      setNotification({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to generate suggestions.",
      });
    } finally {
      setIsGeneratingSuggestions(false);
    }
  };

  const handleApplySuggestion = (originalText: string, suggestedText: string) => {
    if (!body.includes(originalText)) {
      setNotification({
        type: "error",
        text: `Original text "${originalText}" not found in current copy.`,
      });
      return;
    }

    const updated = body.replace(originalText, suggestedText);
    setBody(updated);
    setCurrentReport(undefined);
    setSuggestions(null);
    setNotification({
      type: "success",
      text: `Applied replacement. Re-analyze the updated copy before submitting.`,
    });
  };

  const handleSubmitForApproval = async () => {
    if (!selectedContentId) {
      setNotification({
        type: "error",
        text: "Please analyze and save your content before submitting.",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await apiClient.updateContent(selectedContentId, title.trim() || "Untitled Campaign Copy", body);
      await apiClient.submitForApproval(selectedContentId);
      setNotification({
        type: "success",
        text: "Content successfully submitted for human approval! Forwarded to reviewers.",
      });
      onRefresh();
    } catch (err: unknown) {
      setNotification({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to submit for approval.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Studio Top Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <SparklesIcon className="w-6 h-6 text-indigo-400" />
            <span>Content Studio & Compliance Engine</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Author marketing content, run grounded RAG checks, and review evidence-backed AI recommendations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {contents.length > 0 && (
            <select
              value={selectedContentId}
              onChange={(e) => handleSelectContent(e.target.value)}
              className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-700 text-slate-200 cursor-pointer max-w-[200px] truncate"
            >
              {contents.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title} (v{c.version})
                </option>
              ))}
            </select>
          )}

          <button
            onClick={handleCreateNew}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 cursor-pointer whitespace-nowrap"
          >
            + New Copy
          </button>
        </div>
      </div>

      {/* Notification Banner */}
      {notification && (
        <div
          className={`p-3.5 rounded-xl text-xs flex items-center justify-between border ${
            notification.type === "success"
              ? "bg-emerald-950/60 border-emerald-800/60 text-emerald-300"
              : "bg-rose-950/60 border-rose-800/60 text-rose-300"
          }`}
        >
          <div className="flex items-center gap-2">
            {notification.type === "success" ? (
              <CheckCircleIcon className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertTriangleIcon className="w-4 h-4 text-rose-400" />
            )}
            <span>{notification.text}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-[11px] font-bold text-slate-400 hover:text-white ml-2 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* Two Column Layout: Editor & Compliance Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Content Editor (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="glass-panel p-6 rounded-2xl space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Campaign / Content Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter campaign title..."
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-white font-medium text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Marketing Copy Text
                </label>
                <span className="text-[11px] text-slate-500">
                  {body.split(/\s+/).filter(Boolean).length} words &bull; {body.length} characters
                </span>
              </div>
              <textarea
                rows={10}
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Draft or paste marketing content here..."
                className="w-full p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-100 font-sans text-sm leading-relaxed focus:outline-none focus:border-indigo-500 transition-colors resize-y"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <button
                disabled={isAnalyzing || !body.trim()}
                onClick={handleRunAnalysis}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition-all cursor-pointer disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <RefreshCwIcon className="w-4 h-4 animate-spin" />
                ) : (
                  <SparklesIcon className="w-4 h-4" />
                )}
                <span>{isAnalyzing ? "Analyzing Guidelines..." : "Analyze with BrandGuard AI"}</span>
              </button>

              <button
                disabled={isSubmitting || !selectedContentId}
                onClick={handleSubmitForApproval}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-emerald-300 bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-800/60 transition-all cursor-pointer disabled:opacity-50"
                title="Submit content for review by Manager or Brand Reviewer"
              >
                <SendIcon className="w-4 h-4" />
                <span>Submit for Human Approval</span>
              </button>
            </div>
          </div>

          {/* AI Suggestion Engine Box */}
          {currentReport && currentReport.findings && currentReport.findings.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl space-y-4 border border-indigo-500/30 glow-indigo">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <SlidersIcon className="w-5 h-5 text-indigo-400" />
                  <div>
                    <h3 className="text-sm font-bold text-white">AI Correction Suggestion Engine</h3>
                    <p className="text-[11px] text-slate-400">
                      Grounded rewriting options preserving meaning while complying with rules
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <select
                    value={rewriteMode}
                    onChange={(e) => setRewriteMode(e.target.value as RewriteMode)}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 border border-slate-700 text-indigo-300 cursor-pointer"
                  >
                    <option value="minimal_correction">Minimal Correction</option>
                    <option value="professional_rewrite">Professional Rewrite</option>
                    <option value="brand_aligned_rewrite">Brand-Aligned Rewrite</option>
                  </select>

                  <button
                    disabled={isGeneratingSuggestions}
                    onClick={handleGenerateSuggestions}
                    className="px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 cursor-pointer disabled:opacity-50"
                  >
                    {isGeneratingSuggestions ? "Generating..." : "Generate Suggestions"}
                  </button>
                </div>
              </div>

              {/* Suggestions List */}
              {suggestions && suggestions.suggestions && suggestions.suggestions.length > 0 && (
                <div className="space-y-3 pt-2">
                  {suggestions.suggestions.map((sug, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2.5"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-400">
                          Replacement #{idx + 1}
                        </span>
                        {sug.evidence?.document_name && (
                          <span className="text-[11px] text-indigo-400">
                            Citation: {sug.evidence.document_name}
                            {sug.evidence.page_number ? ` (p. ${sug.evidence.page_number})` : ""}
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                        <div className="p-2.5 rounded-lg bg-rose-950/20 border border-rose-900/30 text-rose-300 line-through">
                          {sug.original_text}
                        </div>
                        <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-900/30 text-emerald-300 font-medium">
                          {sug.suggested_text}
                        </div>
                      </div>

                      <p className="text-[11px] text-slate-400 italic">
                        Why: {sug.reason}
                      </p>

                      <div className="flex justify-end">
                        <button
                          onClick={() =>
                            handleApplySuggestion(sug.original_text, sug.suggested_text)
                          }
                          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 cursor-pointer"
                        >
                          <CheckIcon className="w-3.5 h-3.5" />
                          <span>Accept & Apply to Copy</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Real-Time Compliance Analysis Report (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          {currentReport ? (
            <div className="glass-panel p-6 rounded-2xl space-y-6">
              {/* Header / Score Ring */}
              <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-slate-900/50 border border-slate-800 text-center">
                <ScoreRing score={currentReport.score} size={110} strokeWidth={9} />
                {currentReport.summary && (
                  <p className="mt-3 text-xs text-slate-400 max-w-xs">
                    {currentReport.summary}
                  </p>
                )}
                {currentReport.confidence_note && (
                  <div className="mt-2 inline-flex items-center gap-1.5 text-[11px] text-slate-500">
                    <InfoIcon className="w-3.5 h-3.5" />
                    <span>{currentReport.confidence_note}</span>
                  </div>
                )}
              </div>

              {/* Finding Breakdown */}
              <div className="space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <h3 className="text-sm font-bold text-white">
                    Identified Inconsistencies ({currentReport.findings?.length || 0})
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    Human review required
                  </span>
                </div>

                {!currentReport.findings || currentReport.findings.length === 0 ? (
                  <div className="p-6 text-center rounded-xl bg-emerald-950/20 border border-emerald-900/40 text-emerald-300 text-xs">
                    <CheckCircleIcon className="w-8 h-8 mx-auto mb-2 text-emerald-400" />
                    <p className="font-bold">Perfect Brand Compliance</p>
                    <p className="text-[11px] text-slate-400 mt-1">
                      No violations or tone inconsistencies found in this copy.
                    </p>
                  </div>
                ) : (
                  currentReport.findings.map((f, i) => (
                    <div
                      key={f.id || i}
                      className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2 hover:border-slate-700 transition-colors"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <CategoryBadge category={f.category} />
                        <SeverityBadge severity={f.severity} />
                      </div>

                      {f.problematic_text && (
                        <div className="p-2 rounded bg-rose-950/30 border border-rose-900/40 text-xs text-rose-300 font-mono">
                          &ldquo;{f.problematic_text}&rdquo;
                        </div>
                      )}

                      <p className="text-xs text-slate-300 leading-snug">
                        {f.explanation}
                      </p>

                      {/* Evidence Card */}
                      {f.evidence && (
                        <div className="p-2.5 rounded-lg bg-indigo-950/20 border border-indigo-900/30 text-[11px] text-slate-300 space-y-1">
                          <p className="font-semibold text-indigo-400 flex items-center gap-1">
                            <span>Guideline Rule Citation:</span>
                            {f.evidence.document_name && (
                              <span className="text-slate-400 font-normal">
                                {f.evidence.document_name}
                                {f.evidence.page_number ? ` (p. ${f.evidence.page_number})` : ""}
                              </span>
                            )}
                          </p>
                          {f.evidence.guideline_text && (
                            <p className="italic text-slate-400">
                              &ldquo;{f.evidence.guideline_text}&rdquo;
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : (
            <div className="glass-panel p-8 rounded-2xl text-center space-y-3">
              <SparklesIcon className="w-10 h-10 mx-auto text-indigo-400 opacity-60" />
              <h3 className="text-base font-bold text-white">Compliance Report Awaiting Analysis</h3>
              <p className="text-xs text-slate-400">
                Click &ldquo;Analyze with BrandGuard AI&rdquo; to evaluate your content against the brand guidelines.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
