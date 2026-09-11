import { useEffect, useState } from "react";

export default function useScan(active = false) {
	const [progress, setProgress] = useState(0);
	useEffect(() => {
		if (!active) return undefined;
		setProgress(0);
		const timer = window.setInterval(() => setProgress((value) => Math.min(value + 10, 100)), 180);
		return () => window.clearInterval(timer);
	}, [active]);
	return { progress, complete: progress === 100 };
}
