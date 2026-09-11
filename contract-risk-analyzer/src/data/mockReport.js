export const mockReport = {
	title: "Vendor Services Agreement",
	fileName: "vendor-services-agreement.pdf",
	pages: 18,
	analyzedAt: "September 9, 2026",
	overallRisk: "Moderate",
	score: 62,
	summary: "The agreement is workable, but several clauses shift operational and financial risk to your business. Prioritize the liability cap, renewal terms, and data protection language before signing.",
	clauses: [
		{ id: 1, title: "Limitation of liability", category: "Financial", risk: "High", location: "Section 11, page 14", text: "Vendor's aggregate liability is limited to fees paid in the preceding three months, excluding indirect damages.", recommendation: "Request a cap tied to annual contract value and carve-outs for confidentiality, data protection, and gross negligence." },
		{ id: 2, title: "Auto-renewal", category: "Commercial", risk: "Medium", location: "Section 4, page 5", text: "This agreement renews automatically for successive one-year terms unless notice is provided 60 days before expiry.", recommendation: "Add a renewal reminder and reduce the notice period to 30 days." },
		{ id: 3, title: "Data processing", category: "Privacy", risk: "Medium", location: "Schedule B, page 17", text: "The vendor may engage subprocessors with written notice, but the agreement does not provide a complete subprocessor list.", recommendation: "Attach the current list and require approval or timely objection for material changes." },
		{ id: 4, title: "Termination for convenience", category: "Exit", risk: "Low", location: "Section 9, page 12", text: "Either party may terminate with 90 days' written notice without an early termination fee.", recommendation: "Keep this clause and confirm transition support is included in the services schedule." }
	]
};
