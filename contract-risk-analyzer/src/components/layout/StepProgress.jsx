export default function StepProgress({ current }) {
  const steps = [
    "Upload",
    "Scan",
    "Analyze",
    "Combine",
    "Results",
  ];

  return (
    <div className="mb-10 flex items-start">
      {steps.map((step, index) => (
        <div key={step} className="relative flex flex-1 flex-col items-center text-center">
          {index < steps.length - 1 && <span className={`absolute left-1/2 top-4 -z-0 h-px w-full ${current > index + 1 ? "bg-[#d97745]" : "bg-slate-200"}`} />}
          <div
            className={`z-10 grid h-8 w-8 place-items-center rounded-full text-xs font-bold ${current >= index + 1 ? "bg-[#d97745] text-white" : "border border-slate-200 bg-white text-slate-400"}`}
          >
            {index + 1}
          </div>

          <p className={`mt-2 text-xs ${current >= index + 1 ? "font-semibold text-slate-700" : "text-slate-400"}`}>{step}</p>
        </div>
      ))}
    </div>
  );
}