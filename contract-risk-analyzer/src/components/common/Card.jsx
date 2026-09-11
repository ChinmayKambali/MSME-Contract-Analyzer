export default function Card({ children, className = "" }) {
  return (
    <div className={`rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_12px_35px_rgba(22,59,67,0.06)] ${className}`}>
      {children}
    </div>
  );
}