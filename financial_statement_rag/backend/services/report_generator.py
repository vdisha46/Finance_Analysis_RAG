from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class ReportGenerator:
    """Generate report PDFs for analysis results."""

    @staticmethod
    def generate_pdf_report(title: str, content: str) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(title, styles["Title"]), Spacer(1, 20)]

        for paragraph in content.split("\n"):
            if paragraph.strip():
                story.append(Paragraph(paragraph, styles["BodyText"]))
                story.append(Spacer(1, 12))

        document.build(story)
        return buffer.getvalue()
