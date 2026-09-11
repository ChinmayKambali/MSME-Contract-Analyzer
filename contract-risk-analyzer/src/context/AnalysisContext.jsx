import { createContext, useContext, useState } from "react";

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
	const [analysis, setAnalysis] = useState({ progress: 0, complete: false });
	return <AnalysisContext.Provider value={{ analysis, setAnalysis }}>{children}</AnalysisContext.Provider>;
}

export function useAnalysisContext() {
	const context = useContext(AnalysisContext);
	if (!context) throw new Error("useAnalysisContext must be used inside AnalysisProvider");
	return context;
}
