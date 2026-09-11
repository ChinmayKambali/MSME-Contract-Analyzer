import { FileText, X } from "lucide-react";

export default function FileCard({ file, onRemove }) {
	if (!file) return null;
	return <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-lg bg-[#fff1e9] text-[#d97745]"><FileText size={20} /></span><div><p className="font-semibold text-slate-800">{file.name}</p><p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p></div></div><button onClick={onRemove} title="Remove file" className="text-slate-400 hover:text-red-500"><X size={18} /></button></div>;
}
