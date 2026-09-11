import ProgressBar from "../common/ProgressBar";
export default function ReportProgress({ value = 82 }) { return <div><div className="mb-2 flex justify-between text-sm"><span className="font-semibold text-slate-700">Report readiness</span><span className="text-slate-500">{value}%</span></div><ProgressBar value={value} /></div>; }
