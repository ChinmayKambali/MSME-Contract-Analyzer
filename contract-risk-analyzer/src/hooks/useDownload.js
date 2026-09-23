export default function useDownload() {
  return (report) => {
    if (!report || !report.clauses || report.clauses.length === 0) return;

    let content = `========================================================\n`;
    content += `           MSME CONTRACT RISK REPORT\n`;
    content += `========================================================\n\n`;
    content += `Document Name: ${report.fileName || "Contract Document"}\n`;
    content += `Overall Risk:  ${report.overallRisk || "N/A"}\n`;
    content += `Risk Score:    ${report.score || 0} / 100\n\n`;
    content += `EXECUTIVE SUMMARY:\n`;
    content += `${report.summary || "No summary available."}\n\n`;
    content += `========================================================\n`;
    content += `               PRIORITIZED RISK CLAUSES\n`;
    content += `========================================================\n\n`;

    report.clauses.forEach((c, idx) => {
      content += `CLAUSE #${String(idx + 1).padStart(2, "0")}: ${c.title}\n`;
      content += `Risk Level: ${c.risk || c.risk_level || "Medium"} | Location: ${c.location || "Contract Body"}\n`;
      content += `Category:   ${c.category || c.ui_category || "General"}\n`;
      content += `Contract Text: "${c.text || c.what_it_says}"\n`;
      if (c.why_risky) content += `Why Risky:     ${c.why_risky}\n`;
      if (c.legal_flag) content += `Legal Flag:    ${c.legal_flag}\n`;
      if (c.benchmark_comparison) content += `Benchmark:     ${c.benchmark_comparison}\n`;
      if (c.recommendation || c.suggested_alternative) {
        content += `Recommended Alternative: ${c.recommendation || c.suggested_alternative}\n`;
      }
      content += `\n` + `-`.repeat(56) + `\n\n`;
    });

    const safeFileName = (report.fileName || "contract").replace(/\.[^/.]+$/, "");
    const downloadName = `${safeFileName}-risk-report.txt`;

    const url = URL.createObjectURL(new Blob([content], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = downloadName;
    link.click();
    URL.revokeObjectURL(url);
  };
}
