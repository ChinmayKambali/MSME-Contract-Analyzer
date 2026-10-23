import { ChevronDown, MapPin, AlertTriangle, Scale, BookOpen, CheckCircle2, TrendingUp, ShieldCheck, ShieldAlert, ShieldQuestion } from "lucide-react";
import Badge from "../common/Badge";
import { riskColors } from "../../utils/riskColors";
import { renderInline } from "../../utils/renderInline";

// ---------- helpers ----------

/** Format a number with Indian grouping: 1,00,000 */
function fmtINR(amount) {
  if (amount == null) return null;
  const n = Math.round(amount);
  // Use a real no-break space character ( ), NOT a backslash-u escape,
  // because JSX text children do not process backslash sequences.
  return "Rs " + n.toLocaleString("en-IN");
}

/**
 * Format a date string as "7 Oct 2026".
 * Accepts ISO 8601 dates ("2026-10-07") or already-formatted strings.
 * Falls back to the raw string if parsing fails.
 */
function fmtDate(raw) {
  if (!raw) return raw;
  const d = new Date(raw);
  if (isNaN(d.getTime())) return raw;
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

/** Build caption parts from exposure fields, skipping nulls */
function buildCaption(exp) {
  const parts = [];
  if (exp.extra_days != null && exp.statutory_days != null) {
    parts.push(`${exp.extra_days} day${exp.extra_days !== 1 ? "s" : ""} over the ${exp.statutory_days}-day limit`);
  }
  if (exp.rate_used_pct != null) {
    parts.push(`${exp.rate_used_pct}% a year`);
  }
  if (exp.rate_date) {
    parts.push(`bank rate as on ${fmtDate(exp.rate_date)}`);
  }
  return parts.join(", ");
}

// ---------- ExposureChip ----------

function ExposureChip({ exposure }) {
  if (!exposure) return null;
  const { mode, amount_inr, note } = exposure;

  if (mode === "not_computable") {
    return (
      <div className="mt-2 inline-flex flex-col gap-0.5">
        <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2.5 py-1 text-xs text-slate-500 border border-slate-200">
          <TrendingUp size={11} className="shrink-0" />
          {note || "Exposure not computable"}
        </span>
      </div>
    );
  }

  // within-limit: amount is 0 and note mentions limit
  const isWithinLimit =
    (amount_inr === 0 || amount_inr === null) &&
    note &&
    /limit/i.test(note);

  if (isWithinLimit) {
    return (
      <div className="mt-2 inline-flex flex-col gap-0.5">
        <span className="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 border border-emerald-200">
          <ShieldCheck size={11} className="shrink-0" />
          Within statutory limit
        </span>
      </div>
    );
  }

  const caption = buildCaption(exposure);

  return (
    <div className="mt-2 inline-flex flex-col gap-0.5">
      <span className="inline-flex items-center gap-1.5 flex-wrap rounded-md bg-amber-50 px-2.5 py-1 text-base font-semibold text-amber-800 border border-amber-200">
        <TrendingUp size={13} className="shrink-0" />
        {fmtINR(amount_inr)}
        {mode === "normalized" && (
          <span className="ml-1 font-normal text-amber-600 italic text-sm">Illustrative, per Rs{' '}1,00,000 of invoice value</span>
        )}
      </span>
      {caption && (
        <span className="pl-0.5 text-xs text-slate-400 leading-snug">
          For payment: {caption}
        </span>
      )}
    </div>
  );
}

// ---------- VerificationBadge ----------

const CONFIDENCE_MAP = {
  high:   { label: "Verified against source",  icon: ShieldCheck,    cls: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  medium: { label: "Partly verified",           icon: ShieldQuestion, cls: "bg-amber-50   text-amber-700   border-amber-200" },
  low:    { label: "Low confidence",            icon: ShieldAlert,    cls: "bg-rose-50    text-rose-700    border-rose-200" },
};

function VerificationBadge({ verification }) {
  if (!verification) return null;
  const conf = verification.confidence;
  const meta = CONFIDENCE_MAP[conf];
  if (!meta) return null;
  const Icon = meta.icon;
  const tooltip = verification.flags && verification.flags.length
    ? verification.flags.join(" • ")
    : undefined;

  return (
    <span
      title={tooltip}
      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium border ${meta.cls}`}
    >
      <Icon size={11} className="shrink-0" />
      {meta.label}
    </span>
  );
}

// ---------- ClauseCard ----------

export default function ClauseCard({ clause }) {
  return (
    <details className="group rounded-xl border border-slate-200 bg-white transition hover:border-slate-300">
      <summary className="flex cursor-pointer list-none items-center gap-4 p-5">
        {/* Clause number badge */}
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-slate-50 text-sm font-bold text-slate-500">
          {String(clause.id).padStart(2, "0")}
        </span>

        <div className="min-w-0 flex-1">
          {/* Title + severity pill + legal flag chip */}
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold text-slate-800">{clause.title}</h3>
            <Badge
              text={clause.risk || clause.risk_level || "Medium"}
              color={riskColors[clause.risk || clause.risk_level || "Medium"]}
            />
            {clause.legal_flag && (
              <span className="inline-flex items-center gap-1 rounded-md bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800 border border-amber-200">
                <Scale size={11} /> {clause.legal_flag}
              </span>
            )}
            <VerificationBadge verification={clause.verification} />
          </div>
          {/* Section + category */}
          <p className="mt-1 flex items-center gap-1 text-xs text-slate-400">
            <MapPin size={12} /> {clause.location}
            <span className="mx-1">•</span>
            {clause.category || clause.ui_category}
          </p>
          {/* Exposure chip */}
          <ExposureChip exposure={clause.exposure} />
        </div>

        <ChevronDown size={18} className="text-slate-400 transition group-open:rotate-180" />
      </summary>

      {/* Expanded body */}
      <div className="border-t border-slate-100 px-5 pb-6 pt-4 space-y-4">

        {/* What it says */}
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
            What it says
          </p>
          <p className="text-sm italic leading-6 text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-100">
            "{renderInline(clause.text || clause.what_it_says)}"
          </p>
        </div>

        {/* Why it is risky */}
        {clause.why_risky && (
          <div className="flex gap-3 rounded-lg bg-rose-50/60 p-3.5 text-sm text-rose-900 border border-rose-100">
            <AlertTriangle size={18} className="text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-rose-700">
                Why it is risky
              </p>
              <p className="mt-1 leading-relaxed">{renderInline(clause.why_risky)}</p>
            </div>
          </div>
        )}

        {/* Benchmark comparison */}
        {clause.benchmark_comparison && (
          <div className="flex gap-3 rounded-lg bg-slate-50 p-3.5 text-sm text-slate-700 border border-slate-200">
            <BookOpen size={18} className="text-slate-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Benchmark comparison
              </p>
              <p className="mt-1 leading-relaxed">{renderInline(clause.benchmark_comparison)}</p>
            </div>
          </div>
        )}

        {/* Suggested alternative */}
        <div className="flex gap-3 rounded-lg bg-[#f1f8f6] p-4 border border-[#d2eae4]">
          <CheckCircle2 size={18} className="text-[#287365] shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-[#287365]">
              Suggested alternative
            </p>
            <p className="mt-1 text-sm leading-6 text-slate-700">
              {renderInline(clause.recommendation || clause.suggested_alternative)}
            </p>
          </div>
        </div>

      </div>
    </details>
  );
}
