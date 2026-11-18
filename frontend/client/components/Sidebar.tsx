"use client";

import type { ComponentType } from "react";

import {
  BarChartIcon,
  SparklesIcon,
  LayersIcon,
  UserCheckIcon,
  SlidersIcon,
} from "./icons";
import { Role } from "../lib/types";

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  role: Role;
  pendingCount: number;
}

const ROLE_ITEMS: Record<
  Role,
  Array<{ id: string; label: string; icon: ComponentType<{ className?: string }> }>
> = {
  CREATOR: [
    { id: "dashboard", label: "Dashboard", icon: BarChartIcon },
    { id: "studio", label: "Content Studio", icon: SparklesIcon },
    { id: "guidelines", label: "Brand Guidelines", icon: LayersIcon },
    { id: "approvals", label: "Approval Hub", icon: UserCheckIcon },
  ],
  MANAGER: [
    { id: "dashboard", label: "Dashboard", icon: BarChartIcon },
    { id: "approvals", label: "Approval Hub", icon: UserCheckIcon },
  ],
  BRAND_REVIEWER: [
    { id: "dashboard", label: "Dashboard", icon: BarChartIcon },
    { id: "guidelines", label: "Brand Guidelines", icon: LayersIcon },
    { id: "approvals", label: "Approval Hub", icon: UserCheckIcon },
  ],
  ADMIN: [
    { id: "dashboard", label: "Dashboard", icon: BarChartIcon },
    { id: "studio", label: "Content Studio", icon: SparklesIcon },
    { id: "guidelines", label: "Brand Guidelines", icon: LayersIcon },
    { id: "approvals", label: "Approval Hub", icon: UserCheckIcon },
    { id: "team", label: "Team & Roles", icon: SlidersIcon },
  ],
};

export function Sidebar({
  currentTab,
  onSelectTab,
  role,
  pendingCount,
}: SidebarProps) {
  return (
    <aside className="w-full border-b border-slate-800 bg-slate-950 md:w-64 md:border-b-0 md:border-r md:min-h-[calc(100vh-4rem)]">
      <div className="md:sticky md:top-16 p-3 md:p-4">
        <p className="mb-3 hidden px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500 md:block">
          {role.replace("_", " ")} workspace
        </p>
        <nav className="flex gap-2 overflow-x-auto md:flex-col md:overflow-visible">
          {ROLE_ITEMS[role].map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-semibold transition md:w-full ${
                  isActive
                    ? "border border-indigo-500/30 bg-indigo-500/15 text-white"
                    : "border border-transparent text-slate-400 hover:bg-slate-900 hover:text-white"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-indigo-400" : "text-slate-500"}`} />
                <span>{item.label}</span>
                {item.id === "approvals" && pendingCount > 0 && (
                  <span className="ml-auto rounded-full border border-amber-500/40 bg-amber-500/20 px-1.5 text-[10px] text-amber-300">
                    {pendingCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
