import { useUploadContext } from "../context/UploadContext";

export default function useUpload() {
	const { file, setFile } = useUploadContext();
	const selectFile = (nextFile) => setFile(nextFile);
	return { file, selectFile, clearFile: () => setFile(null) };
}
