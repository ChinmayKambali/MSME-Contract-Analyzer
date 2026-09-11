export default function AgentCard({ icon: Icon, title, detail, done }) {
	return <div className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4"><span className={`grid h-10 w-10 place-items-center rounded-lg ${done ? "bg-[#e8f5f1] text-[#3b8c80]" : "bg-slate-100 text-slate-400"}`}><Icon size={19} /></span><div className="min-w-0"><p className="font-semibold text-slate-800">{title}</p><p className="text-sm text-slate-500">{detail}</p></div><span className="ml-auto text-xs font-semibold text-[#3b8c80]">{done ? "Complete" : "Working"}</span></div>;
}
