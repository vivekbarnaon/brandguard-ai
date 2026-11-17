import React from "react";

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  showStatus?: boolean;
}

export function ScoreRing({
  score,
  size = 120,
  strokeWidth = 10,
  showStatus = true,
}: ScoreRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.max(0, Math.min(100, score));
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  let colorClass = "text-emerald-500 stroke-emerald-500";
  let bgGlow = "shadow-[0_0_30px_rgba(16,185,129,0.2)]";
  let statusText = "Compliant";
  let statusBadgeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";

  if (clampedScore < 60) {
    colorClass = "text-rose-500 stroke-rose-500";
    bgGlow = "shadow-[0_0_30px_rgba(244,63,94,0.2)]";
    statusText = "Non-Compliant";
    statusBadgeClass = "bg-rose-500/10 text-rose-400 border-rose-500/30";
  } else if (clampedScore < 85) {
    colorClass = "text-amber-500 stroke-amber-500";
    bgGlow = "shadow-[0_0_30px_rgba(245,158,11,0.2)]";
    statusText = "Needs Review";
    statusBadgeClass = "bg-amber-500/10 text-amber-400 border-amber-500/30";
  }

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className={`relative flex items-center justify-center rounded-full ${bgGlow}`}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-slate-800"
            fill="transparent"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${colorClass} transition-all duration-1000 ease-out`}
            fill="transparent"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-3xl font-extrabold tracking-tight text-white">
            {clampedScore}
          </span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
            Score
          </span>
        </div>
      </div>

      {showStatus && (
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${statusBadgeClass}`}
        >
          {statusText}
        </span>
      )}
    </div>
  );
}
