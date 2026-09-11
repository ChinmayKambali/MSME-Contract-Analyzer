import { createContext, useContext, useState } from "react";
import { mockReport } from "../data/mockReport";

const ContractContext = createContext(null);

export function ContractProvider({ children }) {
	const [contract, setContract] = useState({ file: null, report: mockReport });
	return <ContractContext.Provider value={{ contract, setContract }}>{children}</ContractContext.Provider>;
}

export function useContract() {
	const context = useContext(ContractContext);
	if (!context) throw new Error("useContract must be used inside ContractProvider");
	return context;
}
