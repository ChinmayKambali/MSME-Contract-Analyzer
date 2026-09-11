import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import CompletionList from "../components/combine/CompletionList";
import MergeFlow from "../components/combine/MergeFlow";
import ReportProgress from "../components/combine/ReportProgress";

export default function CombinePage() { const navigate = useNavigate(); useEffect(() => { const timer = setTimeout(() => navigate("/results"), 1600); return () => clearTimeout(timer); }, [navigate]); return <MainLayout><StepProgress current={4} /><section className="fade-up mx-auto max-w-3xl"><div className="mb-7"><p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">Final assembly</p><h2 className="mt-2 text-3xl font-bold text-[#163b43]">Making the findings useful.</h2><p className="mt-2 text-slate-500">We are turning the analysis into a practical review you can share with your team.</p></div><Card><MergeFlow /><div className="my-7 grid gap-8 sm:grid-cols-2"><CompletionList /><ReportProgress /></div><p className="text-center text-xs text-slate-400">Your report will be ready in a moment.</p></Card></section></MainLayout>; }
