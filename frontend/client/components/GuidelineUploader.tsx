"use client";

import React, { useRef, useState } from "react";
import { DocumentItem, Role } from "../lib/types";
import { apiClient } from "../lib/api";
import { StatusBadge } from "./Badges";
import {
  UploadCloudIcon,
  FileTextIcon,
  TrashIcon,
  LayersIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  RefreshCwIcon,
} from "./icons";

interface GuidelineUploaderProps {
  documents: DocumentItem[];
  userRole: Role;
  activeOrgId: string;
  onRefresh: () => void;
}

export function GuidelineUploader({
  documents,
  userRole,
  activeOrgId,
  onRefresh,
}: GuidelineUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingDocumentId, setDeletingDocumentId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const canUpload = userRole === "ADMIN" || userRole === "CREATOR";

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!activeOrgId) {
      setUploadError("Please select an organisation before uploading guidelines.");
      return;
    }

    if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
      setUploadError("Only official PDF guideline documents are accepted.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError("File exceeds the 10 MB limit.");
      return;
    }

    setUploadError(null);
    setIsUploading(true);
    setSuccessMsg(null);

    try {
      await apiClient.uploadDocument(file, activeOrgId);
      setSuccessMsg(`Successfully uploaded and indexed "${file.name}"`);
      onRefresh();
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : "Failed to upload document.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (docId: string, name: string) => {
    if (!confirm(`Are you sure you want to remove "${name}" from brand guidelines?`)) return;
    setUploadError(null);
    setDeletingDocumentId(docId);
    try {
      await apiClient.deleteDocument(docId);
      setSuccessMsg(`Removed "${name}" from brand guidelines.`);
      onRefresh();
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : "Failed to delete document.");
    } finally {
      setDeletingDocumentId(null);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <LayersIcon className="w-6 h-6 text-indigo-400" />
            <span>Brand Guidelines & Knowledge Base</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Official PDF guidelines indexed into Qdrant vector storage and referenced for RAG compliance citations.
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

      {/* Drag & Drop Upload Zone (if user has permissions) */}
      {canUpload ? (
        <div
          onClick={() => !isUploading && fileInputRef.current?.click()}
          className={`glass-panel border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all cursor-pointer group ${
            isUploading
              ? "border-indigo-500/50 bg-indigo-950/20"
              : "border-slate-700/80 hover:border-indigo-500/60 hover:bg-slate-900/50"
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,application/pdf"
            className="hidden"
          />

          <div className="max-w-md mx-auto space-y-4">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
              {isUploading ? (
                <RefreshCwIcon className="w-7 h-7 animate-spin" />
              ) : (
                <UploadCloudIcon className="w-7 h-7" />
              )}
            </div>

            <div>
              <p className="text-base font-semibold text-white">
                {isUploading ? "Extracting text, chunking & generating embeddings..." : "Upload Brand Guideline PDF"}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Drag and drop your PDF here, or click to browse (Max 10 MB).
              </p>
            </div>

            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
              <FileTextIcon className="w-3.5 h-3.5 text-indigo-400" />
              <span>PyMuPDF Extraction &bull; Gemini Embeddings &bull; Qdrant Ingestion</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 text-xs flex items-center gap-2">
          <AlertTriangleIcon className="w-4 h-4 text-amber-400 shrink-0" />
          <span>You are viewing in <strong className="text-slate-200">{userRole}</strong> mode. Document upload requires <strong>ADMIN</strong> or <strong>CREATOR</strong> role.</span>
        </div>
      )}

      {/* Notifications */}
      {uploadError && (
        <div className="p-3.5 rounded-xl bg-rose-950/50 border border-rose-800/60 text-xs text-rose-300 flex items-center gap-2">
          <AlertTriangleIcon className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-3.5 rounded-xl bg-emerald-950/50 border border-emerald-800/60 text-xs text-emerald-300 flex items-center gap-2">
          <CheckCircleIcon className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Document Catalog */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Active Brand Knowledge Documents</h3>
          <span className="text-xs text-slate-400 font-medium">
            {documents.length} document{documents.length === 1 ? "" : "s"} loaded
          </span>
        </div>

        <div className="divide-y divide-slate-800/80">
          {documents.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">
              No brand guideline documents uploaded yet. Upload a PDF guideline above to begin.
            </div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.id}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-900/40 transition-colors"
              >
                <div className="flex items-start gap-3.5">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                    <FileTextIcon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white tracking-tight">{doc.name}</h4>
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-400 mt-1">
                      <span>Path: {doc.storage_path}</span>
                      <span>&bull;</span>
                      <span>Added {new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-auto">
                  <StatusBadge status={doc.processing_status} />

                  {canUpload && (
                    <button
                      onClick={() => handleDelete(doc.id, doc.name)}
                      disabled={deletingDocumentId === doc.id}
                      className="p-2 rounded-lg text-rose-400 hover:text-rose-300 hover:bg-rose-950/30 border border-rose-900/40 cursor-pointer disabled:opacity-50 disabled:cursor-wait"
                      title="Delete guideline"
                    >
                      {deletingDocumentId === doc.id ? (
                        <RefreshCwIcon className="w-4 h-4 animate-spin" />
                      ) : (
                        <TrashIcon className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
