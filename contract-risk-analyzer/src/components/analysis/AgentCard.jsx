import { Loader2, AlertCircle, CheckCircle2 } from "lucide-react";

export default function AgentCard({ icon: Icon, title, detail, state = "working" }) {
  const isDone = state === "done";
  const isFailed = state === "failed";
  const isWorking = state === "working";

  return (
    <div className={`flex items-center gap-4 rounded-xl border p-4 transition ${
      isFailed 
        ? "border-rose-200 bg-rose-50/40" 
        : isDone 
        ? "border-slate-200 bg-white" 
        : "border-slate-200 bg-white"
    }`}>
      <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${
        isFailed
          ? "bg-rose-100 text-rose-600"
          : isDone 
          ? "bg-[#e8f5f1] text-[#3b8c80]" 
          : "bg-[#fff1e9] text-[#d97745]"
      }`}>
        <Icon size={19} />
      </span>

      <div className="min-w-0 flex-1">
        <p className="font-semibold text-slate-800">{title}</p>
        <p className="text-sm text-slate-500">{detail}</p>
      </div>

      {isDone && (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-[#e8f5f1] px-2.5 py-1 text-xs font-semibold text-[#3b8c80]">
          <CheckCircle2 size={13} /> Complete
        </span>
      )}

      {isFailed && (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700">
          <AlertCircle size={13} /> Stopped
        </span>
      )}

      {isWorking && (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-[#fff1e9] px-2.5 py-1 text-xs font-semibold text-[#d97745]">
          <Loader2 size={13} className="animate-spin text-[#d97745]" /> Working
        </span>
      )}
    </div>
  );
}
