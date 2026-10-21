import { ShieldAlert, MapPin } from "lucide-react";

/**
 * InjectionBanner – shown above the clause list when security.injection_detected is true.
 * All excerpt text is rendered as plain text only (no dangerouslySetInnerHTML).
 */
export default function InjectionBanner({ security }) {
  if (!security?.injection_detected) return null;

  const matches = Array.isArray(security.matches) ? security.matches : [];

  return (
    <div className="mb-6 rounded-xl border border-amber-300 bg-amber-50 px-5 py-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start gap-3">
        <ShieldAlert size={20} className="mt-0.5 shrink-0 text-amber-600" />
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-amber-900">
            Suspicious instructions found in this document
          </p>
          <p className="mt-1 text-sm leading-6 text-amber-800">
            These lines tried to influence the AI review. They were treated as
            plain text, and the findings below were checked against your
            original document.
          </p>
        </div>
      </div>

      {/* Match rows */}
      {matches.length > 0 && (
        <ul className="mt-4 space-y-3">
          {matches.map((m, i) => (
            <li
              key={i}
              className="rounded-lg border border-amber-200 bg-white/70 px-4 py-3"
            >
              {/* Label chip + section */}
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="inline-flex items-center rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-800 border border-amber-300">
                  {m.label}
                </span>
                {m.section && (
                  <span className="flex items-center gap-1 text-xs text-amber-700">
                    <MapPin size={11} />
                    {m.section}
                  </span>
                )}
              </div>
              {/* Excerpt – plain text only, monospace quote block */}
              <pre className="whitespace-pre-wrap break-words rounded bg-amber-50 border border-amber-100 px-3 py-2 font-mono text-xs leading-5 text-amber-900">
                {m.excerpt}
              </pre>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
