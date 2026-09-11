import { createContext, useContext, useState } from "react";

const UploadContext = createContext(null);

export function UploadProvider({ children }) {
	const [file, setFile] = useState(null);
	return <UploadContext.Provider value={{ file, setFile }}>{children}</UploadContext.Provider>;
}

export function useUploadContext() {
	const context = useContext(UploadContext);
	if (!context) throw new Error("useUploadContext must be used inside UploadProvider");
	return context;
}
