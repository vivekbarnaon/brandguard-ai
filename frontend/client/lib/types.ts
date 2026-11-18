export type Role = "ADMIN" | "CREATOR" | "MANAGER" | "BRAND_REVIEWER";

export type ProcessingStatus = "PENDING" | "PROCESSING" | "PROCESSED" | "FAILED";

export type ContentStatus = 
  | "DRAFT" 
  | "ANALYZED" 
  | "SUBMITTED" 
  | "REVISION_REQUESTED" 
  | "APPROVED" 
  | "REJECTED";

export type ApprovalDecision = "APPROVED" | "REJECTED" | "REVISION_REQUESTED";

export type ViolationCategory =
  | "BRAND_VOICE"
  | "TERMINOLOGY"
  | "PROHIBITED_LANGUAGE"
  | "UNSUPPORTED_CLAIM"
  | "PRODUCT_ACCURACY"
  | "DISCLAIMER"
  | "MESSAGING"
  | "OTHER";

export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

export type OverallStatus = "COMPLIANT" | "NEEDS_REVIEW" | "NON_COMPLIANT" | "INSUFFICIENT_EVIDENCE";

export type RewriteMode = "minimal_correction" | "professional_rewrite" | "brand_aligned_rewrite";

export interface UserItem {
  id: string;
  email: string;
  name?: string | null;
  created_at: string;
}

export interface OrganisationItem {
  id: string;
  name: string;
  created_at: string;
}

export interface MembershipItem {
  role: Role;
}

export interface OrganisationMemberItem {
  id: string;
  user_id: string;
  email: string;
  name?: string | null;
  role: Role;
}

export interface EvidenceReference {
  chunk_id?: string;
  document_id?: string;
  document_name?: string;
  page_number?: number;
  guideline_text?: string;
}

export interface ReportFinding {
  id?: string;
  category: ViolationCategory;
  severity: Severity;
  problematic_text?: string;
  explanation: string;
  rule?: string;
  evidence?: EvidenceReference;
  confidence: number;
  suggested_correction?: string;
}

export interface ComplianceReport {
  id: string;
  content_id: string;
  score: number;
  overall_status: OverallStatus;
  total_violations?: number;
  summary?: string;
  findings: ReportFinding[];
  human_review_required?: boolean;
  confidence_note?: string;
  created_at: string;
}

export interface SuggestionEvidence {
  document_id?: string;
  document_name?: string;
  page_number?: number;
  chunk_id: string;
}

export interface SuggestionItem {
  finding_id: string;
  original_text: string;
  suggested_text: string;
  reason: string;
  supporting_rule?: string;
  evidence: SuggestionEvidence;
  requires_human_review: boolean;
}

export interface SuggestionResponse {
  status: "suggestions_generated" | "no_suggestions" | "insufficient_evidence";
  original_content: string;
  mode: string;
  suggestions: SuggestionItem[];
  skipped_finding_ids?: string[];
  human_review_required: boolean;
}

export interface DocumentItem {
  id: string;
  organisation_id: string;
  name: string;
  storage_path: string;
  processing_status: ProcessingStatus;
  uploaded_by: string;
  created_at: string;
  chunks_count?: number;
  file_size?: string;
}

export interface ContentItem {
  id: string;
  organisation_id: string;
  title: string;
  body: string;
  created_by: string;
  creator_name?: string;
  status: ContentStatus;
  version: number;
  created_at: string;
  latest_report?: ComplianceReport;
}

export interface ApprovalRecord {
  id: string;
  content_id: string;
  reviewer_id: string;
  decision: ApprovalDecision;
  comments?: string | null;
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  organisation_id: string;
  user_id: string;
  user_name?: string;
  action: string;
  entity_id?: string | null;
  metadata_json?: Record<string, unknown>;
  timestamp: string;
}

export interface DashboardMetrics {
  documents: number;
  content: number;
  reports: number;
  average_score: number | null;
  pending_approvals: number;
}
