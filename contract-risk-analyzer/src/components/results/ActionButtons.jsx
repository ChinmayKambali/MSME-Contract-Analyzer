import { Download, RotateCcw } from "lucide-react";
import { Link } from "react-router-dom";
import Button from "../common/Button";
import useDownload from "../../hooks/useDownload";
import { useContract } from "../../context/ContractContext";

export default function ActionButtons() {
  const { contract } = useContract();
  const download = useDownload();
  const hasClauses = contract.report?.clauses && contract.report.clauses.length > 0;
  const isFailed = contract.status?.status === "FAILED" || !hasClauses;

  return (
    <div className="flex flex-col gap-3 sm:flex-row">
      {!isFailed && (
        <Button onClick={() => download(contract.report)}>
          <Download size={17} /> Download report
        </Button>
      )}
      <Link to="/" className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-5 py-3 font-semibold text-slate-600 hover:bg-slate-50 transition">
        <RotateCcw size={17} /> Analyze another
      </Link>
    </div>
  );
}
