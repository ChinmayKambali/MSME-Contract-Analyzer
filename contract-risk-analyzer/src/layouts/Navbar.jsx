import { ShieldCheck, CircleHelp } from "lucide-react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="border-b border-slate-200/80 bg-white/85 px-5 py-4 backdrop-blur sm:px-8">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <Link to="/" className="flex items-center gap-3 text-slate-900">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-[#163b43] text-white"><ShieldCheck size={20} /></span>
          <span className="font-semibold tracking-tight">ContractGuard <span className="text-[#d97745]"></span></span>
        </Link>
        <div className="flex items-center gap-5 text-sm text-slate-500">
          <Link to="/" className="hidden hover:text-[#163b43] sm:block">New analysis</Link>
          <button className="flex items-center gap-2 hover:text-[#163b43]" title="Help"><CircleHelp size={17} /> Help</button>
        </div>
      </div>
    </nav>
  );
}