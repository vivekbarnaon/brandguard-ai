"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Navbar } from "../components/Navbar";
import { DashboardOverview } from "../components/DashboardOverview";
import { ContentStudio } from "../components/ContentStudio";
import { GuidelineUploader } from "../components/GuidelineUploader";
import { ApprovalHub } from "../components/ApprovalHub";
import { Sidebar } from "../components/Sidebar";
import { TeamManagement } from "../components/TeamManagement";
import { AuthModal } from "../components/AuthModal";
import { LandingPage } from "../components/LandingPage";
import { ProfileCard } from "../components/ProfileCard";
import { DemoNoticeModal } from "../components/DemoNoticeModal";
import {
  ContentItem,
  DashboardMetrics,
  DocumentItem,
  OrganisationItem,
  Role,
} from "../lib/types";
import {
  apiClient,
  getStoredOrgId,
  setStoredOrgId,
} from "../lib/api";
import { AlertTriangleIcon, BuildingIcon, RefreshCwIcon } from "../components/icons";

export default function Home() {
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileCard, setShowProfileCard] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const [currentTab, setCurrentTab] = useState("dashboard");
  const [currentRole, setCurrentRole] = useState<Role>("ADMIN");
  const [roleLoaded, setRoleLoaded] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [organisations, setOrganisations] = useState<OrganisationItem[]>([]);
  const [activeOrgId, setActiveOrgId] = useState<string>("");

  const [metrics, setMetrics] = useState<DashboardMetrics>({
    documents: 0,
    content: 0,
    reports: 0,
    average_score: 0,
    pending_approvals: 0,
  });
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [contents, setContents] = useState<ContentItem[]>([]);

  // Load Organisations
  const loadOrganisations = useCallback(async () => {
    try {
      const orgs = await apiClient.listOrganisations();
      setOrganisations(orgs);
      if (orgs.length > 0) {
        const saved = getStoredOrgId();
        const found = orgs.find((o) => o.id === saved);
        const selected = found ? found.id : orgs[0].id;
        setActiveOrgId(selected);
        setStoredOrgId(selected);
      }
    } catch {
      // If unauthenticated or no orgs found
    }
  }, []);

  // Load Workspace Data
  const loadWorkspaceData = useCallback(async (orgId: string) => {
    if (!orgId) return;
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [m, docs, c] = await Promise.all([
        apiClient.getDashboardMetrics(orgId).catch(() => ({
          documents: 0,
          content: 0,
          reports: 0,
          average_score: 0,
          pending_approvals: 0,
        })),
        apiClient.listDocuments(orgId).catch(() => []),
        apiClient.listContent(orgId).catch(() => []),
      ]);

      setMetrics(m);
      setDocuments(docs);
      setContents(c);
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error
          ? err.message
          : "Failed to load workspace data from backend."
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize
  useEffect(() => {
    async function init() {
      setIsLoading(true);
      const restored = await apiClient.restoreSession().catch(() => false);
      setIsAuthenticated(restored);
      setAuthChecked(true);
      if (restored) {
        try {
          const me = await apiClient.getMe();
          if (me) {
            if (me.email) setUserEmail(me.email);
            if (me.role) setCurrentRole(me.role);
          }
        } catch {
          setCurrentRole("ADMIN");
        }
        await loadOrganisations();
      }
      setIsLoading(false);
    }
    init();
  }, [loadOrganisations]);

  // Load when activeOrgId changes
  useEffect(() => {
    if (activeOrgId) {
      loadWorkspaceData(activeOrgId);
    }
  }, [activeOrgId, loadWorkspaceData]);

  useEffect(() => {
    if (!activeOrgId) return;
    let cancelled = false;
    setRoleLoaded(false);
    apiClient
      .getMembership(activeOrgId)
      .then((membership) => {
        if (cancelled) return;
        const role = membership?.role || "ADMIN";
        setCurrentRole(role);
        setCurrentTab((tab) => {
          const allowed: Record<Role, string[]> = {
            CREATOR: ["dashboard", "studio", "guidelines", "approvals"],
            MANAGER: ["dashboard", "approvals"],
            BRAND_REVIEWER: ["dashboard", "guidelines", "approvals"],
            ADMIN: ["dashboard", "studio", "guidelines", "approvals", "team"],
          };
          const allowedTabs = allowed[role] || allowed.ADMIN;
          return allowedTabs.includes(tab) ? tab : allowedTabs[0];
        });
        setRoleLoaded(true);
      })
      .catch(() => {
        if (!cancelled) {
          setCurrentRole("ADMIN");
          setRoleLoaded(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeOrgId]);

  const handleSelectOrg = (orgId: string) => {
    setRoleLoaded(false);
    setActiveOrgId(orgId);
    setStoredOrgId(orgId);
  };

  const handleCreateOrg = async (name: string) => {
    try {
      const newOrg = await apiClient.createOrganisation(name);
      const updated = [...organisations, newOrg];
      setOrganisations(updated);
      setActiveOrgId(newOrg.id);
      setStoredOrgId(newOrg.id);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to create organisation");
    }
  };

  const handleRefreshAll = () => {
    if (activeOrgId) {
      loadWorkspaceData(activeOrgId);
    } else {
      loadOrganisations();
    }
  };

  const handleAuthenticated = async (email: string) => {
    setUserEmail(email);
    setIsAuthenticated(true);
    setShowAuthModal(false);
    setShowProfileCard(true);
    try {
      const me = await apiClient.getMe();
      if (me?.role) {
        setCurrentRole(me.role);
      } else {
        setCurrentRole("ADMIN");
      }
    } catch {
      setCurrentRole("ADMIN");
    }
    loadOrganisations();
  };

  if (!authChecked) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-400">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <LandingPage onGetStarted={() => setShowAuthModal(true)} />
        {showAuthModal && (
          <AuthModal
            onClose={() => setShowAuthModal(false)}
            onAuthenticated={handleAuthenticated}
          />
        )}
        <DemoNoticeModal onAction={() => setShowAuthModal(false)} />
      </>
    );
  }

  if (showProfileCard) {
    return (
      <ProfileCard
        email={userEmail}
        role={currentRole}
        onContinue={() => setShowProfileCard(false)}
      />
    );
  }

  if (activeOrgId && !roleLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
          <p className="text-xs font-medium">Verifying your workspace role...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        currentRole={currentRole}
        organisations={organisations}
        activeOrgId={activeOrgId}
        onSelectOrg={handleSelectOrg}
        onCreateOrg={handleCreateOrg}
        pendingCount={metrics.pending_approvals}
        onRefreshAll={handleRefreshAll}
        userEmail={userEmail}
        onSignedOut={() => {
          setIsAuthenticated(false);
          setUserEmail("");
          setShowProfileCard(false);
        }}
      />
      <div className="flex flex-1 flex-col md:flex-row">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          role={currentRole}
          pendingCount={metrics.pending_approvals}
        />

        {/* Main Container */}
        <main className="w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        {errorMessage && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangleIcon className="w-5 h-5 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={handleRefreshAll}
              className="px-3 py-1 rounded-lg bg-rose-900/60 hover:bg-rose-900 text-white font-semibold flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCwIcon className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center min-h-[50vh]">
            <div className="flex flex-col items-center gap-3 text-slate-400">
              <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs font-medium">Connecting to BrandGuard AI Backend...</p>
            </div>
          </div>
        ) : !activeOrgId ? (
          /* Empty Organisation State */
          <div className="glass-panel max-w-lg mx-auto my-12 p-8 rounded-2xl text-center space-y-4 border border-slate-800">
            <BuildingIcon className="w-12 h-12 mx-auto text-indigo-400 opacity-80" />
            <h2 className="text-lg font-bold text-white">No Organisation Selected</h2>
            <p className="text-xs text-slate-400">
              Create an organisation or configure your Supabase authentication token in the top settings to access your brand workspace.
            </p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const input = (e.currentTarget.elements.namedItem("orgName") as HTMLInputElement);
                if (input?.value.trim()) {
                  handleCreateOrg(input.value.trim());
                  input.value = "";
                }
              }}
              className="flex gap-2 max-w-sm mx-auto pt-2"
            >
              <input
                name="orgName"
                type="text"
                placeholder="New Organisation Name..."
                className="flex-1 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 cursor-pointer"
              >
                Create
              </button>
            </form>
          </div>
        ) : (
          <>
            {currentTab === "dashboard" && (
              <DashboardOverview
                metrics={metrics}
                userRole={currentRole}
                onNavigate={setCurrentTab}
              />
            )}

            {currentTab === "studio" && (
              <ContentStudio
                contents={contents}
                userRole={currentRole}
                activeOrgId={activeOrgId}
                onRefresh={handleRefreshAll}
                onNavigateToApprovals={() => setCurrentTab("approvals")}
              />
            )}

            {currentTab === "guidelines" && (
              <GuidelineUploader
                documents={documents}
                userRole={currentRole}
                activeOrgId={activeOrgId}
                onRefresh={handleRefreshAll}
              />
            )}

            {currentTab === "approvals" && (
              <ApprovalHub
                contents={contents}
                userRole={currentRole}
                onRefresh={handleRefreshAll}
              />
            )}
            {currentTab === "team" && currentRole === "ADMIN" && (
              <TeamManagement
                organisationId={activeOrgId}
                onRoleChanged={handleRefreshAll}
              />
            )}
          </>
        )}
        </main>
      </div>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-slate-950/90 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>
            &copy; 2026 BrandGuard AI &bull; Enterprise Brand Governance Platform
          </p>
        </div>
      </footer>

      {/* Demo Notice Modal */}
      <DemoNoticeModal onAction={() => setCurrentTab("dashboard")} />
    </div>
  );
}
