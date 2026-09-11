import AppRoutes from "./routes/AppRoutes";
import { ContractProvider } from "./context/ContractContext";
import { UploadProvider } from "./context/UploadContext";
import { AnalysisProvider } from "./context/AnalysisContext";

function App() {
  return <ContractProvider><UploadProvider><AnalysisProvider><AppRoutes /></AnalysisProvider></UploadProvider></ContractProvider>;
}

export default App;