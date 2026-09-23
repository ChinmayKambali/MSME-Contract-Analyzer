import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import CompletionList from "../components/combine/CompletionList";
import MergeFlow from "../components/combine/MergeFlow";
import ReportProgress from "../components/combine/ReportProgress";
import { useContract } from "../context/ContractContext";
import { getAnalysisResult } from "../utils/apiClient";
import { AlertCircle } from "lucide-react";

export default function CombinePage() {
  const navigate = useNavigate();
  const { contract, setContract } = useContract();
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!contract.analysisId) {
      const timer = setTimeout(() => navigate("/results"), 1200);
      return () => clearTimeout(timer);
    }

    let isMounted = true;
    const fetchReport = async () => {
      try {
        const reportData = await getAnalysisResult(contract.analysisId);
        if (!isMounted) return;

        setContract((prev) => ({
          ...prev,
          report: reportData,
        }));

        setTimeout(() => {
          if (isMounted) navigate("/results");
        }, 800);
      } catch (err) {
        if (isMounted) setError(err.message || "Failed to load report results.");
      }
    };

    fetchReport();
    return () => {
      isMounted = false;
    };
  }, [contract.analysisId, navigate, setContract]);

  return (
    <MainLayout>
      <StepProgress current={4} />
      <section className="fade-up mx-auto max-w-3xl">
        <div className="mb-7">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">
            Final assembly
          </p>
          <h2 className="mt-2 text-3xl font-bold text-[#163b43]">
            Making the findings useful.
          </h2>
          <p className="mt-2 text-slate-500">
            We are synthesizing domain agent outputs into an actionable executive report.
          </p>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-xl bg-rose-50 p-4 text-sm font-medium text-rose-700 border border-rose-200">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <Card>
          <MergeFlow />
          <div className="my-7 grid gap-8 sm:grid-cols-2">
            <CompletionList />
            <ReportProgress />
          </div>
          <p className="text-center text-xs text-slate-400">
            Your report will be ready in a moment.
          </p>
        </Card>
      </section>
    </MainLayout>
  );
}
