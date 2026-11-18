"use client";

import { useEffect, useState } from "react";
import { apiClient } from "../lib/api";
import { OrganisationMemberItem, Role } from "../lib/types";
import { SlidersIcon, RefreshCwIcon, AlertTriangleIcon } from "./icons";

interface TeamManagementProps {
  organisationId: string;
  onRoleChanged: () => void;
}

const roles: Role[] = ["CREATOR", "MANAGER", "BRAND_REVIEWER", "ADMIN"];

export function TeamManagement({
  organisationId,
  onRoleChanged,
}: TeamManagementProps) {
  const [members, setMembers] = useState<OrganisationMemberItem[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<Role>("CREATOR");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadMembers = async () => {
    setLoading(true);
    setMessage(null);
    try {
      setMembers(await apiClient.listOrganisationMembers(organisationId));
    } catch (error: unknown) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Unable to load team members.",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadMembers();
  }, [organisationId]);

  const addMember = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!email.trim()) return;
    setMessage(null);
    try {
      await apiClient.addOrganisationMember(organisationId, email.trim(), role);
      setEmail("");
      setRole("CREATOR");
      setMessage({ type: "success", text: "Member role assigned successfully." });
      await loadMembers();
      onRoleChanged();
    } catch (error: unknown) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Unable to add member.",
      });
    }
  };

  const updateRole = async (member: OrganisationMemberItem, nextRole: Role) => {
    setMessage(null);
    try {
      const updated = await apiClient.updateOrganisationMemberRole(
        organisationId,
        member.id,
        nextRole
      );
      setMembers((items) =>
        items.map((item) => (item.id === member.id ? updated : item))
      );
      setMessage({ type: "success", text: `Role changed to ${nextRole}.` });
      onRoleChanged();
    } catch (error: unknown) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Unable to change role.",
      });
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold text-white">
          <SlidersIcon className="h-6 w-6 text-indigo-400" />
          Team & Roles
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Assign organisation permissions. Members must sign up before being added.
        </p>
      </div>

      <form
        onSubmit={addMember}
        className="grid gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-5 md:grid-cols-[1fr_220px_auto]"
      >
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="member@company.com"
          className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white"
        />
        <select
          value={role}
          onChange={(event) => setRole(event.target.value as Role)}
          className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white"
        >
          {roles.map((item) => (
            <option key={item} value={item}>
              {item.replace("_", " ")}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-bold text-white hover:bg-indigo-500"
        >
          Add Member
        </button>
      </form>

      {message && (
        <div
          className={`flex items-center gap-2 rounded-xl border p-3 text-xs ${
            message.type === "success"
              ? "border-emerald-800/60 bg-emerald-950/40 text-emerald-300"
              : "border-rose-800/60 bg-rose-950/40 text-rose-300"
          }`}
        >
          {message.type === "error" && <AlertTriangleIcon className="h-4 w-4" />}
          {message.text}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/40">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <h2 className="text-sm font-bold text-white">Organisation members</h2>
          <button
            onClick={() => void loadMembers()}
            className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white"
          >
            <RefreshCwIcon className="h-3.5 w-3.5" />
            Refresh
          </button>
        </div>
        {loading ? (
          <p className="p-6 text-sm text-slate-400">Loading members...</p>
        ) : members.length === 0 ? (
          <p className="p-6 text-sm text-slate-400">No members found.</p>
        ) : (
          <div className="divide-y divide-slate-800">
            {members.map((member) => (
              <div
                key={member.id}
                className="flex flex-col gap-3 px-5 py-4 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <p className="text-sm font-semibold text-white">
                    {member.name || member.email}
                  </p>
                  <p className="text-xs text-slate-500">{member.email}</p>
                </div>
                <select
                  value={member.role}
                  onChange={(event) =>
                    void updateRole(member, event.target.value as Role)
                  }
                  className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs font-semibold text-white"
                >
                  {roles.map((item) => (
                    <option key={item} value={item}>
                      {item.replace("_", " ")}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
