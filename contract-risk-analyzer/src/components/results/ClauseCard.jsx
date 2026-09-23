import { ChevronDown, MapPin, AlertTriangle, Scale, BookOpen } from "lucide-react";
import Badge from "../common/Badge";
import { riskColors } from "../../utils/riskColors";

export default function ClauseCard({ clause }) {
  return (
    <details className="group rounded-xl border border-slate-200 bg-white transition hover:border-slate-300">
      <summary className="flex cursor-pointer list-none items-center gap-4 p-5">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-slate-50 text-sm font-bold text-slate-500">
          {String(clause.id).padStart(2, "0")}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold text-slate-800">{clause.title}</h3>
            <Badge text={clause.risk || clause.risk_level || "Medium"} color={riskColors[clause.risk || clause.risk_level || "Medium"]} />
            {clause.legal_flag && (
              <span className="inline-flex items-center gap-1 rounded-md bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800 border border-amber-200">
                <Scale size={11} /> {clause.legal_flag}
              </span>
            )}
          </div>
          <p className="mt-1 flex items-center gap-1 text-xs text-slate-400">
            <MapPin size={12} /> {clause.location} <span className="mx-1">•</span> {clause.category || clause.ui_category}
          </p>
        </div>
        <ChevronDown size={18} className="text-slate-400 transition group-open:rotate-180" />
      </summary>

      <div className="border-t border-slate-100 px-5 pb-5 pt-4 space-y-4">
        {/* Exact Clause Text */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Contract Clause Text</p>
          <p className="text-sm italic leading-6 text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-100">
            “{clause.text || clause.what_it_says}”
          </p>
        </div>

        {/* Why Risky Explanation */}
        {clause.why_risky && (
          <div className="flex gap-3 rounded-lg bg-rose-50/60 p-3.5 text-sm text-rose-900 border border-rose-100">
            <AlertTriangle size={18} className="text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-rose-700">Why this is risky</p>
              <p className="mt-0.5 leading-relaxed">{clause.why_risky}</p>
            </div>
          </div>
        )}

        {/* Benchmark Comparison */}
        {clause.benchmark_comparison && (
          <div className="flex gap-3 rounded-lg bg-slate-50 p-3.5 text-sm text-slate-700 border border-slate-200">
            <BookOpen size={18} className="text-slate-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Benchmark Comparison</p>
              <p className="mt-0.5 leading-relaxed">{clause.benchmark_comparison}</p>
            </div>
          </div>
        )}

        {/* Recommended Safer Alternative */}
        <div className="rounded-lg bg-[#f1f8f6] p-4 border border-[#d2eae4]">
          <p className="text-xs font-bold uppercase tracking-wider text-[#287365]">Recommended Action / Safer Alternative</p>
          <p className="mt-1 text-sm leading-6 text-slate-700 font-medium">
            {clause.recommendation || clause.suggested_alternative}
          </p>
        </div>
      </div>
    </details>
  );
}
