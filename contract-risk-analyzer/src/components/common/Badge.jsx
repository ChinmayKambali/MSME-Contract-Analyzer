export default function Badge({ text, color = "bg-slate-100 text-slate-600" }) {
  return (
    <span className={`px-3 py-1 rounded-full text-sm ${color}`}>
      {text}
    </span>
  );
}