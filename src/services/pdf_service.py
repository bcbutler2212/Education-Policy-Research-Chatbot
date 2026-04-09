"""
PDF Service for serving PDF files in both local and Azure environments.
"""

import os
from flask import send_from_directory, abort
from typing import Optional


class PDFService:
    """Service for serving PDF files."""

    def __init__(self, docs_directory: str = "docs"):
        self.docs_directory = docs_directory
        self.full_docs_path = os.path.abspath(docs_directory)

    def serve_pdf(self, filename: str):
        """Serve a PDF file from the docs directory."""
        # Security check - ensure filename is safe
        if not self._is_safe_filename(filename):
            abort(404)

        # Check if file exists
        file_path = os.path.join(self.full_docs_path, filename)
        if not os.path.exists(file_path):
            abort(404)

        try:
            return send_from_directory(
                directory=self.full_docs_path,
                path=filename,
                mimetype='application/pdf',
                as_attachment=False  # Display in browser instead of downloading
            )
        except Exception:
            abort(404)

    def _is_safe_filename(self, filename: str) -> bool:
        """Check if the filename is safe (no directory traversal)."""
        # Ensure filename doesn't contain path separators
        if '/' in filename or '\\' in filename or '..' in filename:
            return False

        # Ensure it's a PDF file
        if not filename.lower().endswith('.pdf'):
            return False

        return True

    def list_available_pdfs(self) -> list:
        """List all available PDF files."""
        try:
            pdf_files = [
                f for f in os.listdir(self.full_docs_path)
                if f.lower().endswith('.pdf')
            ]
            return sorted(pdf_files)
        except OSError:
            return []


# Singleton instance
pdf_service = PDFService()