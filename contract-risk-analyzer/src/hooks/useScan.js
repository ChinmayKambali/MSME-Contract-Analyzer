import { useEffect, useState } from "react";
import { useContract } from "../context/ContractContext";
import { getAnalysisStatus } from "../utils/apiClient";

export default function useScan(active = false) {
  const { contract, setContract } = useContract();
  const [progress, setProgress] = useState(contract.status?.progress || 0);
  const [complete, setComplete] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!active) return;
    if (!contract.analysisId) {
      // Fallback for demo without backend
      const timer = window.setInterval(() => {
        setProgress((val) => {
          if (val >= 30) {
            setComplete(true);
            return 30;
          }
          return val + 10;
        });
      }, 200);
      return () => window.clearInterval(timer);
    }

    let isMounted = true;
    const pollStatus = async () => {
      try {
        const data = await getAnalysisStatus(contract.analysisId);
        if (!isMounted) return;

        setProgress(data.progress || 0);
        setContract((prev) => ({ ...prev, status: data }));

        if (data.status === "FAILED") {
          setError(data.error_message || "Document processing failed.");
          setComplete(true);
        } else if (data.progress >= 30 || data.stage !== "EXTRACTING") {
          setComplete(true);
        }
      } catch (err) {
        if (isMounted) setError(err.message);
      }
    };

    pollStatus();
    const interval = window.setInterval(pollStatus, 1000);
    return () => {
      isMounted = false;
      window.clearInterval(interval);
    };
  }, [active, contract.analysisId, setContract]);

  return { progress, complete, error };
}
