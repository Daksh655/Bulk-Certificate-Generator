from datetime import date
from pathlib import Path
from backend.app.services.certificate_generator import _render_pdf, PAGE_WIDTH, PAGE_HEIGHT

output_path = Path("scratch/test_cert.pdf")
output_path.parent.mkdir(exist_ok=True)
_render_pdf(
    output_path=output_path,
    certificate_id=9999,
    recipient_name="Rahul Sharma",
    event_name="Advanced Python Workshop",
    event_date=date(2026, 10, 12)
)

print(f"Generated test PDF at {output_path.absolute()}")
