import { FileUp } from "lucide-react";

export default function UploadBox({ onFile }) {
	return <label className="grid min-h-56 cursor-pointer place-items-center rounded-2xl border-2 border-dashed border-[#8cc6bd] bg-[#f2fbf8] p-8 text-center transition hover:bg-[#e9f7f2]">
		<input type="file" accept=".pdf,.doc,.docx" className="sr-only" onChange={(event) => onFile(event.target.files?.[0] ?? null)} />
		<span><span className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-full bg-white text-[#d97745] shadow-sm"><FileUp size={26} /></span><strong className="block text-lg text-slate-800">Drop your contract here</strong><span className="mt-1 block text-sm text-slate-500">or click to browse from your device</span></span>
	</label>;
}
