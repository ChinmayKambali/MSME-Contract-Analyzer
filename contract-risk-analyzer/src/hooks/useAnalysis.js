import { useEffect, useState } from "react";

export default function useAnalysis(active = false) {
	const [progress, setProgress] = useState(0);
	useEffect(() => {
		if (!active) return undefined;
		const timer = window.setInterval(() => setProgress((value) => Math.min(value + 8, 100)), 160);
		return () => window.clearInterval(timer);
	}, [active]);
	return { progress, complete: progress === 100 };
}
