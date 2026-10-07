from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

# backend/app/services/certificate_generator.py -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
GENERATED_DIR = PROJECT_ROOT / "generated"

PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)
CENTER_X = PAGE_WIDTH / 2
MAX_TEXT_WIDTH = PAGE_WIDTH - 200

GOLD = colors.HexColor("#B08D3C")
NAVY = colors.HexColor("#1F2A44")
GREY = colors.HexColor("#555555")


class CertificateGenerationError(Exception):
    """Raised when a certificate PDF cannot be generated."""


def generate_certificate(
    job_id: int,
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    event_date: date,
) -> str:
    """Generate one certificate PDF and return its project-relative path.

    Output: generated/{job_id}/certificate_{certificate_id}.pdf
    The returned value is what gets stored in the database, so it is relative
    and uses forward slashes (portable across machines and operating systems).
    The filename never contains user input, so it is always filesystem-safe.
    """
    output_path = GENERATED_DIR / str(job_id) / f"certificate_{certificate_id}.pdf"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _render_pdf(output_path, certificate_id, recipient_name, event_name, event_date)
    except Exception as exc:
        output_path.unlink(missing_ok=True)  # never leave a partial file behind
        raise CertificateGenerationError(
            f"Failed to generate certificate {certificate_id}: {exc}"
        ) from exc
    return output_path.relative_to(PROJECT_ROOT).as_posix()


def resolve_certificate_path(relative_path: str) -> Path:
    """Turn a stored project-relative path into an absolute filesystem path."""
    return PROJECT_ROOT / relative_path



def _render_pdf(
    output_path: Path,
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    event_date: date,
) -> None:
    # Page compression is off so the text stays inspectable; the file is tiny anyway.
    pdf = Canvas(str(output_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT), pageCompression=0)
    pdf.setTitle(f"Certificate {certificate_id}")

    _draw_border(pdf)

    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 44)
    pdf.drawCentredString(CENTER_X, PAGE_HEIGHT - 150, "CERTIFICATE")
    pdf.setFillColor(GOLD)
    pdf.setFont("Helvetica", 22)
    pdf.drawCentredString(CENTER_X, PAGE_HEIGHT - 185, "OF COMPLETION")

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Oblique", 15)
    pdf.drawCentredString(CENTER_X, PAGE_HEIGHT - 235, "This certifies that")

    _draw_fitted_text(pdf, recipient_name, "Helvetica-Bold", 36, PAGE_HEIGHT - 285, NAVY)
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1)
    pdf.line(CENTER_X - 180, PAGE_HEIGHT - 297, CENTER_X + 180, PAGE_HEIGHT - 297)

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica-Oblique", 15)
    pdf.drawCentredString(CENTER_X, PAGE_HEIGHT - 330, "has successfully completed")

    _draw_fitted_text(pdf, event_name, "Helvetica-Bold", 26, PAGE_HEIGHT - 372, NAVY)

    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(CENTER_X, PAGE_HEIGHT - 408, _format_date(event_date))

    _draw_footer(pdf, certificate_id)
    pdf.showPage()
    pdf.save()


def _draw_border(pdf: Canvas) -> None:
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(4)
    pdf.rect(25, 25, PAGE_WIDTH - 50, PAGE_HEIGHT - 50)
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1)
    pdf.rect(35, 35, PAGE_WIDTH - 70, PAGE_HEIGHT - 70)


def _draw_fitted_text(
    pdf: Canvas, text: str, font: str, size: int, y: float, color: colors.Color
) -> None:
    """Draw centered text, shrinking the font so long values stay inside the border."""
    while size > 10 and stringWidth(text, font, size) > MAX_TEXT_WIDTH:
        size -= 1
    pdf.setFillColor(color)
    pdf.setFont(font, size)
    pdf.drawCentredString(CENTER_X, y, text)


def _draw_footer(pdf: Canvas, certificate_id: int) -> None:
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1)
    pdf.line(CENTER_X - 100, 90, CENTER_X + 100, 90)
    pdf.setFillColor(GREY)
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(CENTER_X, 74, "Organizer")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(55, 50, f"Certificate ID: {certificate_id}")


def _format_date(value: date) -> str:
    # Built manually: strftime("%-d") is not portable to Windows.
    return f"{value.strftime('%B')} {value.day}, {value.year}"
