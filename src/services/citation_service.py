"""
Centralized Citation Service

Handles citation extraction, formatting, and link generation for both
local development and Azure production environments.
"""

import os
from typing import List, Dict, Any
from urllib.parse import quote


class CitationService:
    """Service for handling document citations and PDF links."""

    def __init__(self):
        self.environment = self._detect_environment()
        self.base_pdf_url = self._get_base_pdf_url()

    def _detect_environment(self) -> str:
        """Detect if running in local Docker or Azure production."""
        # Check for Azure-specific environment variables
        if os.getenv('AZURE_CONTAINER_APP_NAME') or os.getenv('WEBSITE_SITE_NAME'):
            return 'azure'
        elif os.getenv('DOCKER_ENV') or os.path.exists('/.dockerenv'):
            return 'docker'
        else:
            return 'local'

    def _get_base_pdf_url(self) -> str:
        """Get the base URL for PDF files based on environment."""
        
         # Use Azure container app URL or custom PDF base URL
        base_url = os.getenv('AZURE_PDF_BASE_URL', 'https://edu-backend.politeglacier-cb73354c.eastus.azurecontainerapps.io')
        
        if not base_url.startswith('http'):
            base_url = f"https://{base_url}"
        #return f"{base_url}/pdfs"
        return f"{base_url}/pdfs"
       

    def extract_citations_from_documents(self, documents: List[Any]) -> List[Dict[str, Any]]:
        """Extract citation metadata from retrieved documents."""
        citations = []
        seen_files = set()

        for doc in documents:
            citation_data = doc.metadata.get("citation", "")
            if citation_data and citation_data not in seen_files:
                seen_files.add(citation_data)

                citation_info = {
                    "filename": citation_data,
                    "display_name": self._format_display_name(citation_data),
                    "pdf_url": self._generate_pdf_url(citation_data),
                    "clickable_link": self._create_clickable_link(citation_data)
                }
                citations.append(citation_info)

        return citations

    def _format_display_name(self, filename: str) -> str:
        """Format filename into human-readable display name."""
        # Remove .pdf extension and replace underscores with spaces
        display_name = filename.replace('.pdf', '').replace('_', ' ')
        # Clean up "Formatted" suffix if present
        display_name = display_name.replace(' Formatted', '')
        return display_name

    def _generate_pdf_url(self, filename: str) -> str:
        """Generate the appropriate PDF URL based on environment."""
        encoded_filename = quote(filename)
        return f"{self.base_pdf_url}/{encoded_filename}"
        
        

    def _create_clickable_link(self, filename: str) -> str:
        """Create markdown clickable link for the PDF."""
        pdf_url = self._generate_pdf_url(filename)
        display_name = self._format_display_name(filename)

        return f'[{display_name}]({pdf_url})'

    def format_citations_for_response(self, citations: List[Dict[str, Any]]) -> str:
        """Format citations for display in chatbot response."""
        if not citations:
            return ""

        citation_links = []
        for citation in citations:
            citation_links.append(f"- {citation['clickable_link']}")

        formatted_citations = "\n".join(citation_links)

        return f"""

**Sources:**
{formatted_citations}
"""

    def get_environment_info(self) -> Dict[str, Any]:
        """Get current environment configuration info."""
        return {
            "environment": self.environment,
            "base_pdf_url": self.base_pdf_url,
            "azure_container_name": os.getenv('AZURE_CONTAINER_APP_NAME'),
            "docker_env": os.path.exists('/.dockerenv')
        }


# Singleton instance for easy import
citation_service = CitationService()