import {
  ApprovalDecision,
  ApprovalRecord,
  ComplianceReport,
  ContentItem,
  DashboardMetrics,
  DocumentItem,
  OrganisationItem,
  RewriteMode,
  SuggestionResponse,
  UserItem,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_PUBLISHABLE_KEY =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

const TOKEN_STORAGE_KEY = "brandguard_auth_token";
const REFRESH_TOKEN_STORAGE_KEY = "brandguard_refresh_token";
const ORG_STORAGE_KEY = "brandguard_active_org_id";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

function getStoredRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
}

function setStoredRefreshToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
  }
}

function requireSupabaseConfig(): {
  url: string;
  publishableKey: string;
} {
  if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
    throw new Error(
      "Supabase login is not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY."
    );
  }
  return {
    url: SUPABASE_URL.replace(/\/$/, ""),
    publishableKey: SUPABASE_PUBLISHABLE_KEY,
  };
}

interface SupabaseSession {
  access_token: string;
  refresh_token: string;
}

async function saveSession(response: Response): Promise<void> {
  let payload: Partial<SupabaseSession> & { error_description?: string };
  try {
    payload = await response.json();
  } catch {
    throw new Error("Supabase returned an invalid authentication response.");
  }

  if (!response.ok || !payload.access_token || !payload.refresh_token) {
    throw new Error(
      payload.error_description || "Authentication failed. Check your email and password."
    );
  }

  setStoredToken(payload.access_token);
  setStoredRefreshToken(payload.refresh_token);
}

async function refreshSession(): Promise<boolean> {
  const refreshToken = getStoredRefreshToken();
  if (!refreshToken) return false;

  const { url, publishableKey } = requireSupabaseConfig();
  const response = await fetch(`${url}/auth/v1/token?grant_type=refresh_token`, {
    method: "POST",
    headers: {
      apikey: publishableKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    setStoredToken(null);
    setStoredRefreshToken(null);
    return false;
  }

  await saveSession(response);
  return true;
}

export function getStoredOrgId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ORG_STORAGE_KEY);
}

export function setStoredOrgId(orgId: string | null): void {
  if (typeof window === "undefined") return;
  if (orgId) {
    localStorage.setItem(ORG_STORAGE_KEY, orgId);
  } else {
    localStorage.removeItem(ORG_STORAGE_KEY);
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  allowRefresh = true
): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = path.startsWith("http") ? path : `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (allowRefresh && response.status === 401 && getStoredRefreshToken()) {
    const refreshed = await refreshSession();
    if (refreshed) {
      return request<T>(path, options, false);
    }
  }

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorDetail =
          typeof errJson.detail === "string"
            ? errJson.detail
            : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const apiClient = {
  // Check backend health
  async checkHealth(): Promise<{ online: boolean; message?: string }> {
    try {
      const rootUrl = API_BASE_URL.replace("/api/v1", "");
      const res = await fetch(`${rootUrl}/health`, {
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        return { online: true, message: "Backend API Live" };
      }
      return { online: false, message: `Status ${res.status}` };
    } catch {
      return { online: false, message: "Backend offline" };
    }
  },

  // Auth & Profile
  async signIn(email: string, password: string): Promise<void> {
    const { url, publishableKey } = requireSupabaseConfig();
    const response = await fetch(`${url}/auth/v1/token?grant_type=password`, {
      method: "POST",
      headers: {
        apikey: publishableKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });
    await saveSession(response);
  },

  async signOut(): Promise<void> {
    const token = getStoredToken();
    if (token) {
      try {
        const { url, publishableKey } = requireSupabaseConfig();
        await fetch(`${url}/auth/v1/logout`, {
          method: "POST",
          headers: {
            apikey: publishableKey,
            Authorization: `Bearer ${token}`,
          },
        });
      } finally {
        setStoredToken(null);
        setStoredRefreshToken(null);
      }
    } else {
      setStoredToken(null);
      setStoredRefreshToken(null);
    }
  },

  async restoreSession(): Promise<boolean> {
    if (getStoredToken()) return true;
    return refreshSession();
  },

  async getMe(): Promise<UserItem> {
    return request<UserItem>("/auth/me");
  },

  // Organisations
  async listOrganisations(): Promise<OrganisationItem[]> {
    return request<OrganisationItem[]>("/organisations");
  },

  async createOrganisation(name: string): Promise<OrganisationItem> {
    return request<OrganisationItem>("/organisations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
  },

  async getOrganisation(organisationId: string): Promise<OrganisationItem> {
    return request<OrganisationItem>(`/organisations/${organisationId}`);
  },

  // Documents
  async listDocuments(organisationId: string): Promise<DocumentItem[]> {
    return request<DocumentItem[]>(`/documents?organisation_id=${organisationId}`);
  },

  async uploadDocument(
    file: File,
    organisationId: string
  ): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("file", file);
    return request<DocumentItem>(
      `/documents/upload?organisation_id=${organisationId}`,
      {
        method: "POST",
        body: formData,
      }
    );
  },

  async getDocument(documentId: string): Promise<DocumentItem> {
    return request<DocumentItem>(`/documents/${documentId}`);
  },

  async deleteDocument(documentId: string): Promise<void> {
    return request<void>(`/documents/${documentId}`, {
      method: "DELETE",
    });
  },

  // Content
  async listContent(organisationId: string): Promise<ContentItem[]> {
    return request<ContentItem[]>(`/content?organisation_id=${organisationId}`);
  },

  async createContent(
    title: string,
    body: string,
    organisationId: string
  ): Promise<ContentItem> {
    return request<ContentItem>(`/content?organisation_id=${organisationId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, body }),
    });
  },

  async getContent(contentId: string): Promise<ContentItem> {
    return request<ContentItem>(`/content/${contentId}`);
  },

  async updateContent(
    contentId: string,
    title: string,
    body: string
  ): Promise<ContentItem> {
    return request<ContentItem>(`/content/${contentId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, body }),
    });
  },

  // Compliance Analysis
  async analyzeCompliance(contentId: string): Promise<ComplianceReport> {
    return request<ComplianceReport>(
      `/compliance/analyze?content_id=${contentId}`,
      {
        method: "POST",
      }
    );
  },

  async listComplianceReports(
    organisationId: string
  ): Promise<ComplianceReport[]> {
    return request<ComplianceReport[]>(
      `/compliance/reports?organisation_id=${organisationId}`
    );
  },

  async getComplianceReport(reportId: string): Promise<ComplianceReport> {
    return request<ComplianceReport>(`/compliance/reports/${reportId}`);
  },

  // AI Correction Suggestions
  async generateSuggestions(
    contentId: string,
    mode: RewriteMode = "minimal_correction"
  ): Promise<SuggestionResponse> {
    return request<SuggestionResponse>(
      `/suggestions/generate?content_id=${contentId}`,
      {
        method: "POST",
      }
    );
  },

  // Approval Workflow
  async submitForApproval(contentId: string): Promise<ContentItem> {
    return request<ContentItem>(`/approvals/${contentId}/submit`, {
      method: "POST",
    });
  },

  async reviewApproval(
    contentId: string,
    decision: ApprovalDecision,
    comments?: string
  ): Promise<ApprovalRecord> {
    return request<ApprovalRecord>(`/approvals/${contentId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, comments }),
    });
  },

  async getPendingApprovals(organisationId: string): Promise<ContentItem[]> {
    return request<ContentItem[]>(
      `/approvals/pending?organisation_id=${organisationId}`
    );
  },

  async getApprovalHistory(contentId: string): Promise<ApprovalRecord[]> {
    return request<ApprovalRecord[]>(`/approvals/${contentId}/history`);
  },

  // Dashboard Metrics
  async getDashboardMetrics(
    organisationId: string
  ): Promise<DashboardMetrics> {
    return request<DashboardMetrics>(`/dashboard/${organisationId}`);
  },
};
