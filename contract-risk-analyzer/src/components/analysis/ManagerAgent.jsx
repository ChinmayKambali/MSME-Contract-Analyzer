import { Sparkles, AlertCircle } from "lucide-react";

export default function ManagerAgent({ isFailed = false }) {
  if (isFailed) {
    return (
      <div className="flex items-start gap-3 rounded-xl bg-rose-900 p-5 text-white border border-rose-800">
        <AlertCircle className="mt-1 shrink-0 text-rose-300" size={20} />
        <div>
          <p className="font-semibold text-rose-100">Analysis Halted</p>
          <p className="mt-1 text-sm leading-6 text-rose-200">
            Specialist agent pipeline encountered an API/system error. Synthesis cancelled.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 rounded-xl bg-[#163b43] p-5 text-white">
      <Sparkles className="mt-1 shrink-0 text-[#f1b28c]" size={20} />
      <div>
        <p className="font-semibold">Manager agent is synthesizing findings</p>
        <p className="mt-1 text-sm leading-6 text-slate-300">
          The specialists are comparing their results and ranking the clauses that matter most.
        </p>
      </div>
    </div>
  );
}
