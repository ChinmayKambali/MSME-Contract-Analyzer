import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import ProgressBar from "../components/common/ProgressBar";
import AgentGrid from "../components/analysis/AgentGrid";
import ManagerAgent from "../components/analysis/ManagerAgent";
import useAnalysis from "../hooks/useAnalysis";

export default function AnalysisPage() {
	const navigate = useNavigate(); const { progress, complete } = useAnalysis(true);
	useEffect(() => { if (complete) { const timer = setTimeout(() => navigate("/combine"), 600); return () => clearTimeout(timer); } }, [complete, navigate]);
	return <MainLayout><StepProgress current={3} /><section className="fade-up mx-auto max-w-3xl"><div className="mb-7"><p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">Multi-agent review</p><h2 className="mt-2 text-3xl font-bold text-[#163b43]">Four specialists are on it.</h2><p className="mt-2 text-slate-500">Each agent reads the agreement through a different risk lens.</p></div><Card><div className="mb-6 flex items-center justify-between"><span className="font-semibold text-slate-700">Analysis progress</span><span className="text-sm font-semibold text-[#d97745]">{progress}%</span></div><ProgressBar value={progress} /><div className="mt-6"><AgentGrid /></div><div className="mt-6"><ManagerAgent /></div></Card></section></MainLayout>;
}
