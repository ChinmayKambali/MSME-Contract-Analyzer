import { FileText, CalendarDays, Layers3 } from "lucide-react";

export default function DocumentInfo({ report }) {
  const pageCount = report.pages ?? null;
  const pageLabel = pageCount === 1 ? "1 page" : pageCount ? `${pageCount} pages` : "—";

  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <div className="flex items-center gap-3">
        <FileText size={17} className="text-[#d97745]" />
        <div>
          <p className="text-xs text-slate-400">Document</p>
          <p className="truncate text-sm font-semibold text-slate-700">{report.fileName}</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Layers3 size={17} className="text-[#d97745]" />
        <div>
          <p className="text-xs text-slate-400">Length</p>
          <p className="text-sm font-semibold text-slate-700">{pageLabel}</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <CalendarDays size={17} className="text-[#d97745]" />
        <div>
          <p className="text-xs text-slate-400">Reviewed</p>
          <p className="text-sm font-semibold text-slate-700">{report.analyzedAt}</p>
        </div>
      </div>
    </div>
  );
}
