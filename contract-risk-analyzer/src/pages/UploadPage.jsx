//upload page
import { useState, useEffect } from "react";
import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import Button from "../components/common/Button";
import UploadBox from "../components/upload/UploadBox";
import FileCard from "../components/upload/FileCard";
import SupportedFormats from "../components/upload/SupportedFormats";
import useUpload from "../hooks/useUpload";
import { useContract } from "../context/ContractContext";
import { uploadContract, getAnalysisHistory, getAnalysisResult } from "../utils/apiClient";
import { ArrowRight, LockKeyhole, Loader2, History, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const { file, selectFile, clearFile } = useUpload();
  const { setContract } = useContract();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [historyItems, setHistoryItems] = useState([]);

  useEffect(() => {
    getAnalysisHistory()
      .then((items) => setHistoryItems(items || []))
      .catch(() => setHistoryItems([]));
  }, []);

  const handleStartReview = async () => {
    if (!file) return;
    setLoading(true);
    setErrorMessage("");

    try {
      const result = await uploadContract(file);
      setContract({
        file,
        analysisId: result.analysis_id,
        status: { progress: 0, status: "EXTRACTING", stage: "EXTRACTING", agent_states: {} },
        report: null,
        error: null,
      });
      navigate("/scan");
    } catch (err) {
      setErrorMessage(err.message || "Failed to start contract scan.");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadHistoryItem = async (item) => {
    if (item.status !== "COMPLETE") {
      setErrorMessage(`Selected report is not complete (Status: ${item.status}).`);
      return;
    }
    setLoading(true);
    try {
      const reportData = await getAnalysisResult(item.analysis_id);
      setContract({
        file: null,
        analysisId: item.analysis_id,
        status: { progress: 100, status: "COMPLETE", stage: "COMPLETE" },
        report: reportData,
        error: null,
      });
      navigate("/results");
    } catch (err) {
      setErrorMessage(err.message || "Failed to load historical report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <StepProgress current={1} />
      <section className="fade-up mx-auto max-w-3xl">
        <div className="mb-8">
          <p className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">
            Start a review
          </p>
          <h2 className="text-4xl font-bold tracking-tight text-[#163b43] sm:text-5xl">
            Understand the risk<br />before you sign.
          </h2>
          <p className="mt-4 max-w-xl text-lg leading-8 text-slate-500">
            Upload a contract and let ContractGuard AI surface the clauses that deserve a closer look.
          </p>
        </div>

        {errorMessage && (
          <div className="mb-6 flex items-center gap-3 rounded-xl bg-rose-50 p-4 text-sm font-medium text-rose-700 border border-rose-200">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <Card className="p-3 sm:p-5">
          <UploadBox onFile={selectFile} />
          {file && (
            <div className="mt-4">
              <FileCard file={file} onRemove={clearFile} />
            </div>
          )}
          <div className="mt-5">
            <SupportedFormats />
          </div>
        </Card>

        <div className="mt-6 flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="flex items-center gap-2 text-sm text-slate-500">
            <LockKeyhole size={16} className="text-[#3b8c80]" /> Your document is processed securely and privately.
          </p>
          <Button disabled={!file || loading} onClick={handleStartReview}>
            {loading ? (
              <>
                <Loader2 size={17} className="animate-spin" /> Uploading...
              </>
            ) : (
              <>
                Scan contract <ArrowRight size={17} />
              </>
            )}
          </Button>
        </div>

        {historyItems.length > 0 && (
          <div className="mt-12">
            <div className="mb-4 flex items-center gap-2">
              <History size={18} className="text-[#d97745]" />
              <h3 className="text-lg font-bold text-[#163b43]">Recent Analysis History</h3>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {historyItems.map((item) => (
                <div
                  key={item.analysis_id}
                  onClick={() => handleLoadHistoryItem(item)}
                  className="cursor-pointer rounded-xl border border-slate-200 bg-white p-4 shadow-xs transition hover:border-[#3b8c80] hover:shadow-md"
                >
                  <p className="font-semibold text-slate-800 truncate">{item.fileName}</p>
                  <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                    <span>{item.analyzedAt || "Recent"}</span>
                    <span className={`px-2 py-0.5 rounded-full font-medium ${
                      item.overallRisk === "High" ? "bg-rose-100 text-rose-700" :
                      item.overallRisk === "Moderate" ? "bg-amber-100 text-amber-700" :
                      "bg-emerald-100 text-emerald-700"
                    }`}>
                      {item.overallRisk ? `${item.overallRisk} Risk` : item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </MainLayout>
  );
}