import os
import uuid
import shutil
from pathlib import Path
from app.config import settings

class StorageService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file_name: str, file_bytes: bytes) -> tuple[str, str, str]:
        """
        Saves uploaded file.
        Returns: (file_id, file_path, file_type)
        """
        ext = Path(file_name).suffix.lower()
        if ext == ".doc":
            raise ValueError("Legacy .doc format is not supported. Please upload a PDF or .docx file.")
        if ext not in [".pdf", ".docx"]:
            raise ValueError("Unsupported file format. Please upload a .pdf or .docx file.")

        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{Path(file_name).name}"
        destination = self.upload_dir / safe_filename

        with open(destination, "wb") as f:
            f.write(file_bytes)

        file_type = "pdf" if ext == ".pdf" else "docx"
        return file_id, str(destination), file_type

storage_service = StorageService()
