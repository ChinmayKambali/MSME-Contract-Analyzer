import { Download, RotateCcw } from "lucide-react";
import { Link } from "react-router-dom";
import Button from "../common/Button";
import useDownload from "../../hooks/useDownload";
export default function ActionButtons() { const download = useDownload(); return <div className="flex flex-col gap-3 sm:flex-row"><Button onClick={() => download()}><Download size={17} /> Download report</Button><Link to="/" className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-5 py-3 font-semibold text-slate-600 hover:bg-slate-50"><RotateCcw size={17} /> Analyze another</Link></div>; }
