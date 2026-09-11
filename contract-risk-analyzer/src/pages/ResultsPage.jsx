import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import RiskSummary from "../components/results/RiskSummary";
import ClauseCard from "../components/results/ClauseCard";
import DocumentInfo from "../components/results/DocumentInfo";
import ActionButtons from "../components/results/ActionButtons";
import { useContract } from "../context/ContractContext";

export default function ResultsPage() { const { contract } = useContract(); const report = contract.report; return <MainLayout><StepProgress current={5} /><section className="fade-up"><div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">Analysis complete</p><h2 className="mt-2 text-4xl font-bold tracking-tight text-[#163b43]">Your risk report</h2></div><ActionButtons /></div><Card><DocumentInfo report={report} /><div className="my-7 border-t border-slate-100" /><RiskSummary report={report} /></Card><div className="mt-8 grid gap-8 lg:grid-cols-[1fr_320px]"><div><div className="mb-4 flex items-end justify-between"><div><h3 className="text-xl font-bold text-[#163b43]">Clauses to review</h3><p className="mt-1 text-sm text-slate-500">Prioritized by potential business impact.</p></div><span className="text-sm text-slate-400">{report.clauses.length} findings</span></div><div className="space-y-3">{report.clauses.map((clause) => <ClauseCard key={clause.id} clause={clause} />)}</div></div><aside className="h-fit rounded-2xl bg-[#163b43] p-6 text-white"><p className="text-sm font-semibold text-[#f1b28c]">A useful next step</p><h3 className="mt-3 text-xl font-bold">Share the priorities with counsel.</h3><p className="mt-3 text-sm leading-6 text-slate-300">This report highlights where a human review can have the greatest payoff.</p></aside></div></section></MainLayout>; }
