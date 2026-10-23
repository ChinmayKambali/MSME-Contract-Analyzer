import { AlertTriangle, ShieldCheck, TrendingUp } from "lucide-react";
import { renderInline } from "../../utils/renderInline";

/** Format a number with Indian grouping: 1,00,000 */
function fmtINR(amount) {
  if (amount == null) return null;
  const n = Math.round(amount);
  // Real no-break space, not a backslash-u escape (JSX text children don't process those).
  return "Rs\u00a0" + n.toLocaleString("en-IN");
}

export default function RiskSummary({ report }) {
  const te = report?.total_exposure ?? null;

  return (
    <div className="grid gap-5 sm:grid-cols-[auto_1fr] sm:items-center">
      {/* Score ring */}
      <div className="relative grid h-32 w-32 place-items-center rounded-full border-[12px] border-[#f1b28c] bg-white">
        <div className="text-center">
          <strong className="block text-3xl text-[#163b43]">{report.score}</strong>
          <span className="text-[10px] uppercase tracking-wider text-slate-400">risk score</span>
        </div>
      </div>

      {/* Severity + summary */}
      <div>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-700">
            {report.overallRisk} risk
          </span>
          <AlertTriangle size={18} className="text-[#d97745]" />
        </div>
        <p className="mt-3 max-w-2xl leading-7 text-slate-600">
          {renderInline(report.summary)}
        </p>

        {/* Total exposure line */}
        {te && te.total_amount_inr != null && (
          <p className="mt-2 flex items-center gap-1.5 text-xs font-medium text-amber-700">
            <TrendingUp size={13} className="shrink-0" />
            Total financial exposure: {fmtINR(te.total_amount_inr)} across {te.finding_count} finding{te.finding_count !== 1 ? "s" : ""}
            {te.mode === "normalized" && (
              <span className="font-normal text-amber-500 italic ml-1">— Illustrative</span>
            )}
          </p>
        )}

        <p className="mt-3 flex items-center gap-2 text-xs text-slate-400">
          <ShieldCheck size={14} className="text-[#3b8c80]" />
          AI-assisted review, designed to support human judgment.
        </p>
      </div>
    </div>
  );
}
