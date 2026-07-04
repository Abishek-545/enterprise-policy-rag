from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "sample_docs"

COMPANY = "Northstar Analytics Group"


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(0.7 * inch, 0.45 * inch, f"{COMPANY} - Internal Policy Knowledge Base")
    canvas.drawRightString(7.8 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(name="DocTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.HexColor("#0f172a"), spaceAfter=14))
    base.add(ParagraphStyle(name="Section", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#1d4ed8"), spaceBefore=12, spaceAfter=6))
    base.add(ParagraphStyle(name="Subsection", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#334155"), spaceBefore=8, spaceAfter=4))
    base.add(ParagraphStyle(name="BodyTextCustom", parent=base["BodyText"], fontSize=9.5, leading=13, textColor=colors.HexColor("#111827"), spaceAfter=5))
    base.add(ParagraphStyle(name="Small", parent=base["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#475569")))
    return base


def make_doc(filename: str, title: str, owner: str, effective: str, sections: list[tuple[str, list[str]]], tables=None):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    doc = BaseDocTemplate(str(path), pagesize=LETTER, rightMargin=0.65 * inch, leftMargin=0.65 * inch, topMargin=0.65 * inch, bottomMargin=0.7 * inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="policy", frames=[frame], onPage=footer)])
    s = styles()
    story = [Paragraph(title, s["DocTitle"])]
    meta = [["Document owner", owner], ["Effective date", effective], ["Review cycle", "Annual or after material regulatory/process change"], ["Audience", "All employees, contractors, and people managers"]]
    table = Table(meta, colWidths=[1.6 * inch, 5.2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#dbeafe")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, Spacer(1, 10)])

    for heading, paragraphs in sections:
        story.append(Paragraph(heading, s["Section"]))
        for paragraph in paragraphs:
            story.append(Paragraph(paragraph, s["BodyTextCustom"]))
        if tables and heading in tables:
            story.append(Spacer(1, 4))
            t = Table(tables[heading], colWidths=[2.0 * inch, 2.3 * inch, 2.5 * inch], repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([t, Spacer(1, 8)])
    doc.build(story)
    return path


def main():
    docs = []
    docs.append(make_doc(
        "leave_and_vacation_policy.pdf",
        "Leave, Vacation, and Time-Off Policy",
        "People Operations",
        "2026-01-01",
        [
            ("Purpose and Scope", ["This policy defines how employees request, approve, record, and use paid time off, sick leave, parental leave, bereavement leave, public holidays, and unpaid leave. It applies to full-time and part-time employees unless a local employment contract or law provides a greater benefit.", "Managers are responsible for planning team coverage fairly and approving requests consistently. Employees are responsible for submitting requests early, documenting urgent absences, and keeping calendars current."]),
            ("Annual Vacation Entitlement", ["Full-time employees receive 20 working days of paid vacation per calendar year, accrued monthly. Employees with five or more years of service receive 25 working days. Part-time employees accrue vacation on a pro-rated basis.", "Unused vacation may carry over up to five days into the next calendar year and must be used by March 31. Carryover above five days requires written approval from People Operations due to business-critical constraints or documented leave interruption."]),
            ("Request and Approval Process", ["Vacation requests of one to five days should be submitted at least ten business days in advance. Requests longer than five consecutive working days should be submitted at least thirty calendar days in advance.", "Managers should approve or decline requests within three business days. Declines must include a business reason and an alternative time window when possible. Employees should not book non-refundable travel before approval is recorded in the HR system."]),
            ("Sick Leave and Medical Absence", ["Employees may use paid sick leave when they are unable to work due to illness, injury, medical appointments, or care for an immediate family member. Employees should notify their manager before the start of the workday when practical.", "A medical certificate may be requested after three consecutive working days of absence or where required by local regulation. Managers must not ask for diagnosis details; only fitness-for-work and expected return date may be requested."]),
            ("Parental, Caregiver, and Bereavement Leave", ["Eligible employees may request parental leave according to local law and company benefit plans. People Operations coordinates documentation, payroll treatment, and return-to-work planning.", "Employees receive up to five paid working days for bereavement involving an immediate family member and up to two paid working days for extended family. Additional unpaid leave may be approved for travel, estate duties, or cultural observances."]),
            ("Holiday Scheduling and Coverage", ["Company holidays are published annually by region. Teams supporting customer-facing operations must maintain minimum coverage plans for peak periods and public holidays.", "Where multiple employees request the same high-demand period, managers should consider business criticality, prior holiday allocation, dependency coverage, and fairness across the team."]),
            ("Compliance and Records", ["All leave must be recorded in the HR system by the employee or manager. Off-system approvals in chat or email should be transferred into the HR system before payroll close.", "Retaliation for lawful leave use is prohibited. Questions about eligibility, medical privacy, or local statutory rights should be escalated to People Operations."]),
        ],
        {"Annual Vacation Entitlement": [["Employee group", "Annual vacation", "Carryover rule"], ["Full-time, under 5 years", "20 working days", "Up to 5 days until March 31"], ["Full-time, 5+ years", "25 working days", "Up to 5 days until March 31"], ["Part-time", "Pro-rated by scheduled hours", "Same pro-rated carryover principle"]]},
    ))

    docs.append(make_doc(
        "workplace_safety_policy.pdf",
        "Workplace Safety and Emergency Response Policy",
        "Facilities and Risk Management",
        "2026-01-01",
        [
            ("Purpose and Safety Principles", ["The company is committed to maintaining a workplace that protects employees, visitors, contractors, and customers from preventable harm. Every person has authority to stop work that appears unsafe.", "Safety practices apply to offices, labs, warehouses, customer sites, company events, and remote work locations where company equipment is used."]),
            ("Incident and Near-Miss Reporting", ["Injuries, hazards, property damage, security threats, and near-miss events must be reported through the Safety Portal within 24 hours. Serious incidents involving medical treatment, fire, violence, or regulatory notification must be reported immediately to the emergency contact line and Facilities.", "Reports should include location, time, people involved, photos if safe, immediate controls applied, and whether emergency services were contacted. The goal of reporting is prevention, not blame."]),
            ("Emergency Evacuation", ["Employees must follow posted evacuation routes and assembly point instructions. Elevators must not be used during fire alarms unless emergency responders instruct otherwise.", "Floor wardens confirm evacuation zones, assist visitors, and report missing persons to emergency responders. Employees should not re-enter a building until cleared by Facilities or local authorities."]),
            ("Ergonomics and Remote Work Safety", ["Employees working remotely should maintain a safe workspace with adequate lighting, stable internet, secure equipment placement, and ergonomic seating. The company may provide ergonomic assessments for employees with recurring discomfort.", "Electrical cords should be managed to avoid trip hazards. Company devices must be stored securely and protected from heat, liquids, and unauthorized access."]),
            ("Visitors, Contractors, and Restricted Areas", ["Visitors must sign in, wear badges, and be escorted in non-public areas. Contractors performing maintenance, electrical, construction, or lab work must provide required permits, insurance, and method statements before work begins.", "Restricted areas may require badge access, safety training, personal protective equipment, or written authorization. Tailgating into secured areas is prohibited."]),
            ("Corrective Actions and Training", ["Facilities and Risk Management assign corrective actions after incident reviews. Action owners must complete remediation by the agreed due date or escalate blockers.", "Employees must complete annual safety training and any role-specific modules, including fire safety, lab safety, first aid, equipment handling, or travel safety where applicable."]),
        ],
        {"Incident and Near-Miss Reporting": [["Event type", "Required timing", "Primary channel"], ["Near miss or minor hazard", "Within 24 hours", "Safety Portal"], ["Injury requiring first aid", "Same business day", "Safety Portal and manager"], ["Fire, violence, medical emergency", "Immediately", "Emergency services and Facilities line"]]},
    ))

    docs.append(make_doc(
        "employee_code_of_conduct.pdf",
        "Employee Code of Conduct and Workplace Rules",
        "Legal and People Operations",
        "2026-01-01",
        [
            ("Professional Conduct", ["Employees are expected to act with integrity, respect, accountability, and good judgment in all company-related activities. This includes work performed in offices, remote environments, client sites, business travel, and digital collaboration spaces.", "Managers are expected to model company values, address conduct concerns promptly, and escalate sensitive matters to People Operations or Legal."]),
            ("Anti-Harassment and Respectful Workplace", ["Harassment, discrimination, bullying, intimidation, retaliation, and abusive conduct are prohibited. Protected characteristics include those defined by applicable law and company equal opportunity standards.", "Employees may report concerns to their manager, People Operations, Legal, or the confidential ethics channel. Reports are reviewed promptly and handled with appropriate confidentiality."]),
            ("Conflicts of Interest", ["Employees must avoid personal, financial, or outside business interests that could interfere with company responsibilities. Potential conflicts must be disclosed before decisions are made or commitments are accepted.", "Examples include supervising a family member, accepting gifts from vendors, holding outside employment with a competitor, or influencing procurement involving a personal relationship."]),
            ("Gifts, Entertainment, and Vendor Interactions", ["Employees may not request gifts, cash, or personal favors from suppliers, customers, or candidates. Modest business meals or promotional items may be accepted when they are infrequent, transparent, and not intended to influence a decision.", "Gifts valued above 75 USD, travel benefits, event tickets, or hospitality involving government officials require Legal review before acceptance."]),
            ("Use of Company Assets", ["Company assets must be used responsibly and primarily for business purposes. Assets include devices, networks, credentials, software licenses, data, facilities, brand materials, and intellectual property.", "Employees must not bypass security controls, share accounts, install unapproved software, or use company systems for unlawful, offensive, or high-risk personal activities."]),
            ("Disciplinary Process", ["Policy violations may result in coaching, written warnings, access restriction, reimbursement denial, termination, or legal action depending on severity and local law.", "The company considers intent, impact, prior history, cooperation, and remediation when determining outcomes."]),
        ],
    ))

    docs.append(make_doc(
        "security_and_data_protection_policy.pdf",
        "Information Security and Data Protection Policy",
        "Security Office",
        "2026-01-01",
        [
            ("Data Classification", ["Company information is classified as Public, Internal, Confidential, or Restricted. Customer data, employee records, credentials, source code, unreleased financials, and security findings are Confidential or Restricted unless formally reclassified.", "Employees must apply the minimum access necessary to perform their role and store sensitive information only in approved systems."]),
            ("Password and Authentication Rules", ["Employees must use unique passwords managed through the approved password manager. Multi-factor authentication is required for company systems, cloud applications, source repositories, and administrative tools.", "Passwords, API keys, recovery codes, and session tokens must not be shared in chat, email, documents, screenshots, or code repositories."]),
            ("Security Incident Reporting", ["Suspected phishing, lost devices, malware alerts, accidental data sharing, credential exposure, or unauthorized access must be reported to security@example.com within one hour of discovery.", "Employees should preserve evidence, avoid deleting suspicious emails or logs, and disconnect affected devices from networks if instructed by Security."]),
            ("Device and Network Security", ["Company laptops must run approved endpoint protection, disk encryption, automatic screen lock, and operating system updates. Jailbroken or rooted devices must not access company systems.", "Public Wi-Fi should be used only with company-approved VPN where required. Sensitive work must not be performed on shared public computers."]),
            ("Data Retention and Sharing", ["Documents should be retained according to the retention schedule and legal hold requirements. Restricted data must not be exported to personal storage, consumer AI tools, or unapproved collaboration platforms.", "External sharing requires a business purpose, appropriate recipient verification, and approved access controls such as expiration dates or watermarking when available."]),
            ("Third-Party and AI Tool Use", ["Vendors handling company or customer data must complete security review before access is granted. Employees must not paste Confidential or Restricted data into external AI tools unless the tool is approved for that data class.", "Generated content used for customer, legal, financial, or security decisions must be reviewed by a qualified employee before use."]),
        ],
        {"Data Classification": [["Classification", "Examples", "Handling rule"], ["Public", "Published marketing pages", "Approved for external use"], ["Internal", "Team procedures, internal roadmaps", "Company access only"], ["Confidential", "Customer contracts, employee data", "Need-to-know access"], ["Restricted", "Credentials, regulated data", "Highest controls and logging"]]},
    ))

    docs.append(make_doc(
        "travel_and_expense_policy.pdf",
        "Travel, Expense, and Reimbursement Policy",
        "Finance Operations",
        "2026-01-01",
        [
            ("Purpose and General Rules", ["This policy explains which business expenses are reimbursable, what approvals are required, and how employees submit accurate expense reports. Expenses must be reasonable, documented, and directly related to company business.", "Employees are expected to use preferred suppliers and company booking tools where available. Personal upgrades, fines, family travel, and expenses lacking business purpose are not reimbursable."]),
            ("Pre-Approval Requirements", ["Manager approval is required before incurring expenses above 100 USD. Department head approval is required for expenses above 1,000 USD, international travel, conference sponsorships, and non-standard equipment purchases.", "Emergency expenses may be submitted after the fact with an explanation, but repeated late approvals may result in reimbursement delay."]),
            ("Travel Booking", ["Air travel should be booked in economy class for flights under six hours. Premium economy may be approved for flights over six hours. Business class requires executive approval unless mandated by medical accommodation or local policy.", "Hotels should be booked within the city rate cap unless event pricing, safety, or availability requires an exception. Employees should choose practical transportation options and avoid luxury services."]),
            ("Meals and Incidentals", ["Meal reimbursement should be reasonable for the location and business context. Alcohol is reimbursable only when part of an approved customer or team event and must comply with local law.", "Per diem arrangements, where used, replace individual meal reimbursement unless Finance approves an exception."]),
            ("Receipts and Submission Timing", ["Receipts are required for expenses above 25 USD and for all lodging, airfare, conference registration, and customer entertainment. Credit card statements alone are not sufficient unless the original receipt is unavailable and an explanation is provided.", "Expense reports should be submitted within 30 calendar days of the transaction or trip completion. Late submissions may require additional approval."]),
            ("Non-Reimbursable Expenses", ["Non-reimbursable expenses include traffic fines, personal entertainment, minibar charges, commuting costs, lost personal items, unauthorized software, and expenses for family members or companions.", "Finance may reject expenses that are excessive, inadequately documented, outside policy, or inconsistent with company values."]),
        ],
        {"Pre-Approval Requirements": [["Expense type", "Approval threshold", "Approver"], ["General business expense", "Above 100 USD", "Manager"], ["Large purchase", "Above 1,000 USD", "Department head"], ["International travel", "Any amount", "Manager and department head"]]},
    ))

    print("Created policy PDFs:")
    for doc in docs:
        print(f"- {doc}")


if __name__ == "__main__":
    main()
