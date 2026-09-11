import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle2, FileSearch } from "lucide-react";
import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import ProgressBar from "../components/common/ProgressBar";
import useScan from "../hooks/useScan";

export default function ScanPage() {
	const navigate = useNavigate(); const { progress, complete } = useScan(true);
	useEffect(() => { if (complete) { const timer = setTimeout(() => navigate("/analysis"), 500); return () => clearTimeout(timer); } }, [complete, navigate]);
	return <MainLayout><StepProgress current={2} /><section className="fade-up mx-auto max-w-2xl"><Card className="grid-paper p-8 text-center sm:p-12"><span className="mx-auto mb-5 grid h-16 w-16 place-items-center rounded-2xl bg-[#fff1e9] text-[#d97745]"><FileSearch size={30} /></span><p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">Step 2 of 5</p><h2 className="mt-3 text-3xl font-bold text-[#163b43]">Reading your contract</h2><p className="mx-auto mt-3 max-w-md text-slate-500">We are extracting pages, headings, and clauses so the review is grounded in your document.</p><div className="mx-auto mt-10 max-w-md"><div className="mb-2 flex justify-between text-sm font-semibold"><span>{complete ? "Scan complete" : "Scanning pages..."}</span><span>{progress}%</span></div><ProgressBar value={progress} /></div><div className="mt-8 flex justify-center gap-6 text-sm text-slate-500"><span className="flex items-center gap-2"><CheckCircle2 size={16} className={progress > 30 ? "text-[#3b8c80]" : "text-slate-300"} /> Text extraction</span><span className="flex items-center gap-2"><CheckCircle2 size={16} className={progress > 70 ? "text-[#3b8c80]" : "text-slate-300"} /> Structure map</span></div></Card></section></MainLayout>;
}
