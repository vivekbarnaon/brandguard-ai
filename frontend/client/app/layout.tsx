import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BrandGuard AI — Enterprise Brand Governance & Compliance Platform",
  description: "AI-powered brand governance platform ensuring messaging consistency, guideline compliance, and human-in-the-loop approvals.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
        {children}
      </body>
    </html>
  );
}
