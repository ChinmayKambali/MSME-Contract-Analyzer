export default function useDownload() {
	return (fileName = "contract-risk-report.txt") => {
		const content = "ContractGuard AI risk report\nGenerated locally from the analyzed contract.";
		const url = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
		const link = document.createElement("a");
		link.href = url;
		link.download = fileName;
		link.click();
		URL.revokeObjectURL(url);
	};
}
