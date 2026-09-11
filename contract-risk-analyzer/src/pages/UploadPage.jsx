import MainLayout from "../layouts/MainLayout";
import StepProgress from "../components/layout/StepProgress";
import Card from "../components/common/Card";
import Button from "../components/common/Button";
import UploadBox from "../components/upload/UploadBox";
import FileCard from "../components/upload/FileCard";
import SupportedFormats from "../components/upload/SupportedFormats";
import useUpload from "../hooks/useUpload";
import { ArrowRight, LockKeyhole } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const { file, selectFile, clearFile } = useUpload();
  const navigate = useNavigate();
  return (
    <MainLayout>
      <StepProgress current={1} />
      <section className="fade-up mx-auto max-w-3xl"><div className="mb-8"><p className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-[#d97745]">Start a review</p><h2 className="text-4xl font-bold tracking-tight text-[#163b43] sm:text-5xl">Understand the risk<br />before you sign.</h2><p className="mt-4 max-w-xl text-lg leading-8 text-slate-500">Upload a contract and let ContractGuard AI surface the clauses that deserve a closer look.</p></div>
        <Card className="p-3 sm:p-5"><UploadBox onFile={selectFile} />{file && <div className="mt-4"><FileCard file={file} onRemove={clearFile} /></div>}<div className="mt-5"><SupportedFormats /></div></Card>
        <div className="mt-6 flex flex-col items-center justify-between gap-4 sm:flex-row"><p className="flex items-center gap-2 text-sm text-slate-500"><LockKeyhole size={16} className="text-[#3b8c80]" /> Your document is processed securely and privately.</p><Button disabled={!file} onClick={() => navigate("/scan")}>Scan contract <ArrowRight size={17} /></Button></div>
      </section>
    </MainLayout>
  );
}