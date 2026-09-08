import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable)
from reportlab.lib.units import cm

with open("../data/insights.json") as f:
    data = json.load(f)
summary = data["summary"]
insights = data["insights"]

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=20, spaceAfter=4)
sub_style = ParagraphStyle("SubX", parent=styles["Normal"], textColor=colors.grey, fontSize=10, spaceAfter=14)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1a2b4c"))
body = ParagraphStyle("BodyX", parent=styles["Normal"], fontSize=10, leading=14)
bullet = ParagraphStyle("BulletX", parent=body, leftIndent=14, bulletIndent=4)
label = ParagraphStyle("LabelX", parent=body, fontName="Helvetica-Bold")

story = []
story.append(Paragraph("NexaTech Industries", title_style))
story.append(Paragraph(f"Executive Financial Summary &mdash; {summary['period']}", sub_style))
story.append(HRFlowable(width="100%", color=colors.HexColor("#1a2b4c"), thickness=1))

# KPI table
kpi_rows = [
    ["Revenue", f"Rs {summary['total_revenue_cr']} Cr", "Growth", f"{summary['revenue_growth_pct']}%"],
    ["Budget Variance", f"{summary['revenue_variance_pct']}%", "EBITDA", f"Rs {summary['ebitda_cr']} Cr"],
    ["EBITDA Margin", f"{summary['ebitda_margin_pct']}%", "Gross Margin", f"{summary['gross_margin_pct']}%"],
    ["DSO", f"{summary['avg_dso_days']} days", "DPO", f"{summary['avg_dpo_days']} days"],
    ["Cash Conversion Cycle", f"{summary['avg_cash_conversion_cycle']} days", "Cost Variance", f"{summary['cost_variance_pct']}%"],
]
t = Table(kpi_rows, colWidths=[4.3*cm, 3.3*cm, 4.3*cm, 3.3*cm])
t.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#dddddd")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f4f8")),
]))
story.append(Spacer(1, 10))
story.append(t)

story.append(Paragraph("Consulting Question", h2))
story.append(Paragraph(
    "NexaTech's revenue is growing, but management believes profitability and cash "
    "efficiency are deteriorating. This summary analyzes the company's financial "
    "performance and identifies opportunities for improvement.", body))

def fix_rupee(s):
    return s.replace("₹", "Rs. ")

for ins in insights:
    story.append(Paragraph(ins["metric"], h2))
    story.append(Paragraph(f"<b>Finding:</b> {fix_rupee(ins['finding'])}", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Root cause:</b>", body))
    for step in ins["root_cause_chain"]:
        story.append(Paragraph(f"&bull; {fix_rupee(step)}", bullet))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Business impact:</b> {fix_rupee(ins['business_impact'])}", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Recommendation:</b> {fix_rupee(ins['recommendation'])}", body))

story.append(Spacer(1, 16))
story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd"), thickness=0.5))
story.append(Paragraph(
    "Prepared as part of the CFO360 Financial Planning &amp; Performance Intelligence "
    "Platform project. NexaTech Industries is a fictional company used for illustrative purposes.",
    ParagraphStyle("Foot", parent=body, fontSize=8, textColor=colors.grey, spaceBefore=8)))

doc = SimpleDocTemplate("executive_summary.pdf", pagesize=A4,
                         topMargin=1.8*cm, bottomMargin=1.8*cm,
                         leftMargin=1.8*cm, rightMargin=1.8*cm)
doc.build(story)
print("Wrote executive_summary.pdf")
