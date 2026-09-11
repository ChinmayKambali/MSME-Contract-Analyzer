import { BrowserRouter, Routes, Route } from "react-router-dom";

import UploadPage from "../pages/UploadPage";
import ScanPage from "../pages/ScanPage";
import AnalysisPage from "../pages/AnalysisPage";
import CombinePage from "../pages/CombinePage";
import ResultsPage from "../pages/ResultsPage";
import NotFound from "../pages/NotFound";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
        <Route path="/combine" element={<CombinePage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}