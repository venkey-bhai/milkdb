# from turtle import width,height, header,footer 

from fastapi import APIRouter, Depends, HTTPException,Query

from fastapi.responses import StreamingResponse, FileResponse

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer, MilkEntry

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib import styles as reportlab_styles

from datetime import date

import csv
import io
import pandas as pd

from reportlab.pdfgen import canvas

router = APIRouter(tags=["Reports"])


# ==================================================
# REPORTS API (NO AUTH)
# ==================================================

@router.get("/reports")
def get_reports(
    report_date: date = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(MilkEntry)

    # FILTER BY DATE
    if report_date:
        query = query.filter(MilkEntry.date == report_date)

    milk_entries = query.all()

    # CUSTOMER IDS
    customer_ids = list(set([e.customer_id for e in milk_entries]))

    # FETCH CUSTOMERS
    customers = db.query(Customer).filter(
        Customer.id.in_(customer_ids)
    ).all()

    customer_map = {c.id: c for c in customers}

    reports = []

    for entry in milk_entries:

        customer = customer_map.get(entry.customer_id)

        reports.append({
            "id": entry.id, 
            "customer_no": customer.customer_no if customer else None,
            "customer_name": customer.name if customer else "Unknown",
            "customer_phone": customer.phone if customer else "",
            "session": entry.session,
            "date": str(entry.date),
            "total_liters": entry.liters,
            "milk_type":entry.customer.milk_type,
            "rate": entry.rate,
            "total_amount": entry.total
        })

    return {
        "success": True,
        "data": reports
    }



@router.delete("/reports/{id}")
def delete_report(id: int, db: Session = Depends(get_db)):

    entry = db.query(MilkEntry).filter(MilkEntry.id == id).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(entry)
    db.commit() 

    return {"message": "Report deleted successfully"}


@router.get("/monthly-buying")
def monthly_buying_report(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):
    results = (
        db.query(
            Customer.customer_no,
            Customer.name,
            Customer.milk_type,
            func.sum(MilkEntry.liters).label("total_liters"),
            func.sum(MilkEntry.total).label("total_amount"),
        )
        .join(Customer, MilkEntry.customer_id == Customer.id)
        .filter(
            extract("month", MilkEntry.date) == month,
            extract("year", MilkEntry.date) == year,
        )
        .group_by(
            Customer.customer_no,
            Customer.name,
            Customer.milk_type,
        )
        .all()
    )
    report = []

    grand_liters = 0
    grand_amount = 0

    for row in results:
        report.append({
            "customer_no": row.customer_no,
            "customer_name": row.name,
            "milk_type": row.milk_type,
            "total_liters": float(row.total_liters or 0),
            "total_amount": float(row.total_amount or 0),
        })

        grand_liters += float(row.total_liters or 0)
        grand_amount += float(row.total_amount or 0)

    return {
        "success": True,
        "month": month,
        "year": year,
        "grand_total_liters": grand_liters,
        "grand_total_amount": grand_amount,
        "data": report,
    }


# ==================================================
# CSV EXPORT (NO AUTH)
# ==================================================

@router.get("/reports/csv")
def download_csv(db: Session = Depends(get_db)):

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Customer",
        "Date",
        "Session",
        "Liters",
        "Rate",
        "Total"
    ])

    entries = db.query(MilkEntry).all()

    for entry in entries:

        customer = db.query(Customer).filter(
            Customer.id == entry.customer_id
        ).first()

        writer.writerow([
            customer.name if customer else "Unknown",
            entry.date,
            entry.session,
            entry.liters,
            entry.rate,
            entry.total
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=milk_report.csv"
        }
    )


# ==================================================
# EXCEL EXPORT (NO AUTH)
# ==================================================

@router.get("/reports/excel")
def download_excel(db: Session = Depends(get_db)):

    entries = db.query(MilkEntry).all()

    data = []

    for entry in entries:

        customer = db.query(Customer).filter(
            Customer.id == entry.customer_id
        ).first()

        data.append({
            "Customer": customer.name if customer else "Unknown",
            "Date": entry.date,
            "Session": entry.session,
            "Liters": entry.liters,
            "Rate": entry.rate,
            "Total": entry.total
        })

    df = pd.DataFrame(data)

    file_path = "milk_report.xlsx"

    df.to_excel(file_path, index=False)

    return FileResponse(
        path=file_path,
        filename="milk_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==================================================
# PDF EXPORT (NO AUTH)
# ==================================================

# @router.get("/reports/pdf")
# def download_pdf(db: Session = Depends(get_db)):

#     file_path = "milk_report.pdf"

#     c = canvas.Canvas(file_path)

#     y = 800
#     c.drawString(220, y, "Milk Report")
#     y -= 40

    
#     entries = db.query(MilkEntry).all()

# # Column headers
#     c.drawString(40, y, "Customer")
#     c.drawString(140, y, "Date")
#     c.drawString(240, y, "Session")
#     c.drawString(320, y, "Liters")
#     c.drawString(400, y, "Total")

#     y -= 30

#     for entry in entries:

#         customer = (
#             db.query(Customer)
#             .filter(
#                 Customer.id == entry.customer_id
#             )
#             .first()
#         )

#         c.drawString(
#             40,
#             y,
#             customer.name if customer else "Unknown"
#         )

#         c.drawString(
#             140,
#             y,
#             str(entry.date)
#         )

#         c.drawString(
#             240,
#             y,
#             entry.session
#         )

#         c.drawString(
#             320,
#             y,
#             f"{entry.liters} L"
#         )

#         c.drawString(
#             400,
#             y,
#             f"Rs.{entry.total}"
#         )

#         y -= 25
#     c.save()

#     return FileResponse(
#         file_path,
#         filename="milk_report.pdf",
#         media_type="application/pdf"
#         )  
    
class NumberedCanvas(canvas.Canvas):
# """
# A canvas that enables "Page X of Y" numbering by capturing 
# page details on the first pass and drawing them on the second pass.
# """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        # Position at bottom right (Page X of Y)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 36, page_text)


def draw_header_footer(canvas, doc):
    canvas.saveState()
    width, height = letter
    
    # 1. Center Top: Company Name
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawCentredString(width / 2, height - 45, "MILK DAIRY CORPORATION")
    
    # 2. Left Side Top (Next line): Address & Contact
    canvas.setFont("Helvetica", 9)
    canvas.drawString(54, height - 65, "123, Dairy Farm Road, Green Valley")
    canvas.drawString(54, height - 77, "Contact: +91 9876543210")
    
    # 3. Right Side Top (Next line): GST No & Email
    canvas.drawRightString(width - 54, height - 65, "GSTIN: 29AAAAA1111A1Z1")
    canvas.drawRightString(width - 54, height - 77, "Email: info@milkdairy.com")
    
    # 4. Draw a clean divider line
    canvas.setStrokeColor(colors.HexColor("#A0A0A0"))
    canvas.setLineWidth(1)
    canvas.line(54, height - 90, width - 54, height - 90)
    
    canvas.restoreState()


@router.get("/reports/pdf")
def download_pdf(db: Session = Depends(get_db)):
    # Create an in-memory buffer instead of saving to local disk
    buffer = io.BytesIO()
    
    # Initialize document template with top margin large enough to clear the header
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=54, leftMargin=54, 
        topMargin=110, bottomMargin=54
    )
    
    header_style = reportlab_styles.ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=10, textColor=colors.whitesmoke)
    cell_style = reportlab_styles.ParagraphStyle('TableCell', fontName='Helvetica', fontSize=10)

    # Compile table headers
    data = [[
        Paragraph("Customer", header_style),
        Paragraph("Date", header_style),
        Paragraph("Session", header_style),
        Paragraph("Liters", header_style),
        Paragraph("Total", header_style)
    ]]

    # Fetch and populate data rows
    entries = db.query(MilkEntry).all()
    for entry in entries:
        customer = db.query(Customer).filter(Customer.id == entry.customer_id).first()
        customer_name = customer.name if customer else "Unknown"
        
        data.append([
            Paragraph(customer_name, cell_style),
            Paragraph(str(entry.date), cell_style),
            Paragraph(entry.session, cell_style),
            Paragraph(f"{entry.liters} L", cell_style),
            Paragraph(f"Rs. {entry.total}", cell_style)
        ])

    # Convert to ReportLab Table and assign structural widths
    # Total printable width is 504 points (612 page width - 108 margins)
    milk_table = Table(data, colWidths=[164, 90, 80, 80, 90])
    
    # Apply clean accounting-style table styling
    milk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9F9F9")]),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story = []
    # Add a title header right above the table content
    title_style = reportlab_styles.ParagraphStyle('ReportTitle', fontName='Helvetica-Bold', fontSize=14, spaceAfter=12)
    story.append(Paragraph("Milk Collection Report", title_style))
    story.append(milk_table)

    # Build document using our custom header layout callbacks and page counter
    doc.build(
        story, 
        onFirstPage=draw_header_footer, 
        onLaterPages=draw_header_footer, 
        canvasmaker=NumberedCanvas
    )

    buffer.seek(0)
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=milk_report.pdf"}
    )
