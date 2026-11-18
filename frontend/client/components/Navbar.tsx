"use client";

import React, { useEffect, useState } from "react";
import {
  ShieldIcon,
  UserCheckIcon,
  BuildingIcon,
  SparklesIcon,
  LayersIcon,
  BarChartIcon,
  SlidersIcon,
  UserIcon,
} from "./icons";
import { OrganisationItem, Role } from "../lib/types";
import { apiClient, getStoredToken } from "../lib/api";

interface NavbarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  currentRole: Role;
  organisations: OrganisationItem[];
  activeOrgId: string;
  onSelectOrg: (orgId: string) => void;
  onCreateOrg: (name: string) => void;
  pendingCount?: number;
  onRefreshAll: () => void;
  onSignedOut?: () => void;
  userEmail?: string;
}

export function Navbar({
  currentTab,
  onSelectTab,
  currentRole,
  organisations,
  activeOrgId,
  onSelectOrg,
  onCreateOrg,
  pendingCount = 0,
  onRefreshAll,
  onSignedOut,
  userEmail = "",
}: NavbarProps) {
  const [showSettings, setShowSettings] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [newOrgName, setNewOrgName] = useState("");

  useEffect(() => {
    setIsAuthenticated(Boolean(getStoredToken()));
  }, []);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setAuthError("Enter your email and password.");
      return;
    }

    setIsAuthenticating(true);
    setAuthError(null);
    try {
      await apiClient.signIn(email.trim(), password);
      setIsAuthenticated(true);
      setPassword("");
      setShowSettings(false);
      onRefreshAll();
    } catch (error: unknown) {
      setAuthError(
        error instanceof Error ? error.message : "Unable to sign in."
      );
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleSignOut = async () => {
    setIsAuthenticating(true);
    setAuthError(null);
    try {
      await apiClient.signOut();
      setIsAuthenticated(false);
      setShowSettings(false);
      onSignedOut?.();
      onRefreshAll();
    } catch (error: unknown) {
      setAuthError(
        error instanceof Error ? error.message : "Unable to sign out."
      );
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleCreateOrg = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    onCreateOrg(newOrgName.trim());
    setNewOrgName("");
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChartIcon },
    { id: "studio", label: "Content Studio", icon: SparklesIcon },
    { id: "guidelines", label: "Brand Guidelines", icon: LayersIcon },
    {
      id: "approvals",
      label: "Approval Hub",
      icon: UserCheckIcon,
      badge: pendingCount > 0 ? pendingCount : null,
    },
  ];

  const roles: { role: Role; label: string }[] = [
    { role: "CREATOR", label: "Creator" },
    { role: "MANAGER", label: "Manager" },
    { role: "BRAND_REVIEWER", label: "Brand Reviewer" },
    { role: "ADMIN", label: "Admin" },
  ];

  const activeOrg = organisations.find((o) => o.id === activeOrgId);

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Platform Name */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => onSelectTab("dashboard")}
                className="flex items-center gap-2.5 group text-left cursor-pointer"
              >
                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-400 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:shadow-indigo-500/40 transition-all">
                  <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                    <ShieldIcon className="w-5 h-5 text-indigo-400 group-hover:scale-110 transition-transform" />
                  </div>
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-base font-bold tracking-tight text-white">
                      BrandGuard
                    </span>
                    <span className="text-xs font-black uppercase px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                      AI
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 font-medium">Enterprise Governance</p>
                </div>
              </button>

              {/* Organisation Selector */}
              <div className="hidden lg:flex items-center gap-2 pl-4 ml-4 border-l border-slate-800">
                <BuildingIcon className="w-3.5 h-3.5 text-slate-400" />
                {organisations.length > 0 ? (
                  <select
                    value={activeOrgId}
                    onChange={(e) => onSelectOrg(e.target.value)}
                    className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer max-w-[160px] truncate"
                  >
                    {organisations.map((org) => (
                      <option key={org.id} value={org.id} className="bg-slate-900 text-slate-100">
                        {org.name}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className="text-xs text-slate-400">
                    {activeOrg?.name || "No Organisation"}
                  </span>
                )}
              </div>
            </div>

            {/* Right actions: Account */}
            <div className="flex items-center gap-2">
              <div className="hidden rounded-xl border border-slate-800 bg-slate-900/90 px-3 py-2 text-[10px] font-bold uppercase tracking-wide text-indigo-300 sm:block">
                {roles.find((role) => role.role === currentRole)?.label}
              </div>
              <button
                onClick={() => setShowProfile(true)}
                className={`flex items-center justify-center w-10 h-10 rounded-xl border transition-colors cursor-pointer ${
                  isAuthenticated
                    ? "border-indigo-500/40 bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20"
                    : "border-slate-800 text-slate-400 hover:text-white hover:bg-slate-900"
                }`}
                title={isAuthenticated ? "View profile" : "Sign in"}
                aria-label={isAuthenticated ? "View profile" : "Sign in"}
              >
                <UserIcon className="w-5 h-5" />
              </button>
            </div>
          </div>

        </div>
      </header>

      {showProfile && isAuthenticated && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md">
          <div className="glass-panel w-full max-w-md rounded-3xl border border-slate-700 p-6 shadow-2xl shadow-black/50">
            <div className="flex items-start justify-between border-b border-slate-800 pb-5">
              <div className="flex items-center gap-3">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-400 to-cyan-300 text-xl font-bold text-slate-950">
                  {(userEmail || "U").charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-indigo-300">
                    Your profile
                  </p>
                  <h3 className="mt-1 text-lg font-bold text-white">
                    {userEmail || "BrandGuard User"}
                  </h3>
                  <p className="mt-1 text-xs text-emerald-300">Active session</p>
                </div>
              </div>
              <button
                onClick={() => setShowProfile(false)}
                className="rounded-lg px-2.5 py-1 text-slate-400 hover:bg-slate-800 hover:text-white"
                aria-label="Close profile"
              >
                &times;
              </button>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div className="glass-card rounded-2xl p-4">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">Workspace role</p>
                <p className="mt-2 text-sm font-bold text-indigo-200">
                  {roles.find((role) => role.role === currentRole)?.label}
                </p>
              </div>
              <div className="glass-card rounded-2xl p-4">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">Organisation</p>
                <p className="mt-2 truncate text-sm font-bold text-white">
                  {activeOrg?.name || "Not selected"}
                </p>
              </div>
            </div>

            <div className="mt-3 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4">
              <p className="text-xs font-semibold text-emerald-200">Workspace access</p>
              <p className="mt-1 text-xs leading-5 text-slate-400">
                Your guidelines, content studio, compliance reports, and approvals are available.
              </p>
            </div>

            <div className="mt-5 flex gap-2">
              <button
                onClick={() => {
                  setShowProfile(false);
                  setShowSettings(true);
                }}
                className="flex-1 rounded-xl border border-slate-700 bg-slate-900/60 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:bg-slate-800"
              >
                Account settings
              </button>
              <button
                onClick={() => setShowProfile(false)}
                className="flex-1 rounded-xl bg-indigo-500 px-4 py-2.5 text-xs font-bold text-white hover:bg-indigo-400"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings / Auth Modal */}
      {showSettings && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="glass-panel w-full max-w-lg rounded-2xl border border-slate-700 p-6 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <SlidersIcon className="w-5 h-5 text-indigo-400" />
                <span>Account & Authentication</span>
              </h3>
              <button
                onClick={() => setShowSettings(false)}
                className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              {!isAuthenticated ? (
                <form onSubmit={handleSignIn} className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-300">Email</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@company.com"
                      autoComplete="email"
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="font-semibold text-slate-300">Password</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Your password"
                      autoComplete="current-password"
                      className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  {authError && (
                    <p className="rounded-lg border border-rose-800/60 bg-rose-950/40 p-2.5 text-rose-300">
                      {authError}
                    </p>
                  )}
                  <button
                    type="submit"
                    disabled={isAuthenticating}
                    className="w-full px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 cursor-pointer"
                  >
                    {isAuthenticating ? "Signing in..." : "Sign in"}
                  </button>
                </form>
              ) : (
                <div className="space-y-3">
                  <p className="text-slate-300">
                    You are signed in. Your session is refreshed automatically.
                  </p>
                  {authError && (
                    <p className="rounded-lg border border-rose-800/60 bg-rose-950/40 p-2.5 text-rose-300">
                      {authError}
                    </p>
                  )}
                  <button
                    onClick={handleSignOut}
                    disabled={isAuthenticating}
                    className="w-full px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-rose-700 hover:bg-rose-600 disabled:opacity-50 cursor-pointer"
                  >
                    {isAuthenticating ? "Signing out..." : "Sign out"}
                  </button>
                </div>
              )}

              <div className="pt-2 border-t border-slate-800 space-y-2">
                <label className="font-semibold text-slate-300">
                  Create New Organisation
                </label>
                <form onSubmit={handleCreateOrg} className="flex gap-2">
                  <input
                    type="text"
                    value={newOrgName}
                    onChange={(e) => setNewOrgName(e.target.value)}
                    placeholder="Organisation Name..."
                    className="flex-1 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    type="submit"
                    className="px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 cursor-pointer"
                  >
                    Create
                  </button>
                </form>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowSettings(false)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
