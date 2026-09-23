import fitz  # PyMuPDF
import docx
from pathlib import Path
from typing import Dict, Any, List

class DocumentParserService:
    def extract_text(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Extracts structured text from PDF or DOCX file.
        Returns: {
            "text": str,
            "pages": Optional[int],
            "sections": List[Dict[str, str]]
        }
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_type == "pdf":
            return self._parse_pdf(file_path)
        elif file_type == "docx":
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        doc = fitz.open(file_path)
        page_count = len(doc)
        full_text_list = []

        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                full_text_list.append(f"--- Page {page_num + 1} ---\n" + text)

        full_text = "\n\n".join(full_text_list).strip()

        if not full_text or len(full_text) < 20:
            raise ValueError("PDF contains no extractable text. Scanned contracts requiring OCR are not supported.")

        return {
            "text": full_text,
            "pages": page_count,
            "sections": self._split_into_sections(full_text)
        }

    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        doc = docx.Document(file_path)
        full_text_list = []
        for p in doc.paragraphs:
            t = p.text.strip()
            if t:
                full_text_list.append(t)

        full_text = "\n\n".join(full_text_list).strip()
        if not full_text:
            raise ValueError("DOCX document is empty.")

        # Estimate page count for DOCX (~350 words per page)
        word_count = len(full_text.split())
        estimated_pages = max(1, round(word_count / 350))

        return {
            "text": full_text,
            "pages": estimated_pages,  # Estimated for DOCX
            "sections": self._split_into_sections(full_text)
        }

    def _split_into_sections(self, full_text: str) -> List[Dict[str, str]]:
        """Splits full contract text into sections based on numbered headings."""
        lines = full_text.split("\n")
        sections = []
        current_heading = "Preamble / General"
        current_lines = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            # Simple heading heuristic: lines starting with section numbers e.g. "1. ", "14. PENALTY"
            if len(line_str) < 100 and line_str[0].isdigit() and ("." in line_str[:5] or " " in line_str[:5]):
                if current_lines:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_lines)
                    })
                    current_lines = []
                current_heading = line_str
            else:
                current_lines.append(line_str)

        if current_lines:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_lines)
            })

        return sections

parser_service = DocumentParserService()
