import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import ProgressBar from "../components/common/ProgressBar";
import AgentGrid from "../components/analysis/AgentGrid";
import ManagerAgent from "../components/analysis/ManagerAgent";
import useAnalysis from "../hooks/useAnalysis";
import { AlertCircle } from "lucide-react";

export default function AnalysisPage() {
  const navigate = useNavigate();
  const { progress, agentStates, complete, error } = useAnalysis(true);
  const isFailed = Boolean(error);

  useEffect(() => {
    if (complete && !error) {
      const timer = setTimeout(() => navigate("/combine"), 600);
      return () => clearTimeout(timer);
    }
  }, [complete, error, navigate]);

  return (
    <MainLayout>
      <StepProgress current={3} />
      <section className="fade-up mx-auto max-w-3xl">
        <div className="mb-7">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">
            Multi-agent review
          </p>
          <h2 className="mt-2 text-3xl font-bold text-[#163b43]">
            Six domain specialists are on it.
          </h2>
          <p className="mt-2 text-slate-500">
            Each specialized AI agent evaluates your agreement against MSME legal and commercial baselines.
          </p>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-xl bg-rose-50 p-4 text-sm font-medium text-rose-700 border border-rose-200 shadow-xs">
            <AlertCircle className="h-5 w-5 shrink-0 text-rose-600" />
            <span>Analysis Error: {error}</span>
          </div>
        )}

        <Card>
          <div className="mb-6 flex items-center justify-between">
            <span className="font-semibold text-slate-700">
              {isFailed ? "Analysis stopped" : "Analysis progress"}
            </span>
            <span className={`text-sm font-semibold ${isFailed ? "text-rose-600" : "text-[#d97745]"}`}>
              {isFailed ? `Failed (${progress}%)` : `${progress}%`}
            </span>
          </div>
          <ProgressBar value={progress} color={isFailed ? "bg-rose-500" : "bg-[#d97745]"} />
          <div className="mt-6">
            <AgentGrid agentStates={agentStates} isFailed={isFailed} />
          </div>
          <div className="mt-6">
            <ManagerAgent isFailed={isFailed} />
          </div>
        </Card>
      </section>
    </MainLayout>
  );
}
