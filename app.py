import streamlit as st
from fpdf import FPDF
import datetime
import tempfile
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="LLC Proof Generator", page_icon="📄")

# --- PDF GENERATION CLASS ---
class PDF(FPDF):
    def header(self):
        # We will handle headers manually in the functions to allow for Logo placement
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_letter(company_name, company_address, ein, employee_name, role, salary, start_date, logo_path=None):
    pdf = PDF()
    pdf.add_page()
    
    # Logo
    if logo_path:
        pdf.image(logo_path, 10, 8, 33)
        pdf.ln(35)
    else:
        pdf.ln(10)

    # Header Info
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, company_name, 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, company_address, 0, 1)
    pdf.cell(0, 5, f"EIN/Tax ID: {ein}", 0, 1)
    pdf.ln(10)
    
    # Date
    pdf.cell(0, 10, datetime.date.today().strftime("%B %d, %Y"), 0, 1)
    pdf.ln(10)

    # Title
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "SUBJECT: VERIFICATION OF EMPLOYMENT AND INCOME", 0, 1)
    pdf.ln(5)

    # Body
    pdf.set_font('Arial', '', 11)
    body_text = (
        f"To Whom It May Concern,\n\n"
        f"This letter serves to verify that {employee_name} is currently employed with "
        f"{company_name}. They hold the position of {role} and have been with the company "
        f"since {start_date.strftime('%B %d, %Y')}.\n\n"
        f"{employee_name} is considered an active employee in good standing. "
        f"Their current compensation is ${salary:,.2f} USD per month, paid via direct deposit/transfer.\n\n"
        f"If you require any further information regarding this employment, please do not hesitate "
        f"to contact us at the address above."
    )
    pdf.multi_cell(0, 6, body_text)
    
    # Signature
    pdf.ln(30)
    pdf.cell(0, 5, "Sincerely,", 0, 1)
    pdf.ln(15)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 5, "Authorized Signatory", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 5, f"{company_name} | HR Department", 0, 1)

    return pdf

def create_paystub(company_name, company_address, employee_name, employee_address, salary, pay_date, logo_path=None):
    pdf = PDF()
    pdf.add_page()

    # Logo and Company Info
    if logo_path:
        pdf.image(logo_path, 10, 8, 25)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_xy(40, 10)
    pdf.cell(0, 10, company_name.upper(), 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_xy(40, 18)
    pdf.cell(0, 5, company_address, 0, 1)
    
    pdf.ln(20)
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "EARNINGS STATEMENT", 0, 1, 'C')
    pdf.ln(5)

    # Employee & Pay Period Grid
    pdf.set_font('Arial', '', 10)
    
    # Draw a box
    pdf.rect(10, 55, 190, 30)
    
    # Inside Box
    pdf.set_xy(12, 58)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(90, 5, "EMPLOYEE NAME & ADDRESS", 0, 0)
    pdf.cell(90, 5, "PAY PERIOD / DATE", 0, 1)
    
    pdf.set_xy(12, 65)
    pdf.set_font('Arial', '', 10)
    pdf.cell(90, 5, employee_name, 0, 0)
    pdf.cell(90, 5, f"Pay Date: {pay_date.strftime('%Y-%m-%d')}", 0, 1)
    
    pdf.set_xy(12, 70)
    pdf.cell(90, 5, employee_address, 0, 0)
    pdf.cell(90, 5, "Pay Period: Monthly", 0, 1)

    pdf.ln(25)

    # Financial Table Header
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(95, 8, "DESCRIPTION", 1, 0, 'C', 1)
    pdf.cell(95, 8, "AMOUNT (USD)", 1, 1, 'C', 1)

    # Financial Table Rows
    pdf.set_font('Arial', '', 10)
    pdf.cell(95, 8, "Gross Salary / Contractor Fee", 1, 0)
    pdf.cell(95, 8, f"${salary:,.2f}", 1, 1, 'R')
    
    pdf.cell(95, 8, "Federal Tax (Non-US Resident)", 1, 0)
    pdf.cell(95, 8, "$0.00", 1, 1, 'R')

    pdf.cell(95, 8, "State Tax", 1, 0)
    pdf.cell(95, 8, "$0.00", 1, 1, 'R')

    # Total
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(95, 10, "NET PAY", 1, 0)
    pdf.cell(95, 10, f"${salary:,.2f}", 1, 1, 'R')

    return pdf

# --- STREAMLIT UI ---

st.title("🇺🇸 US LLC Income Proof Generator")
st.markdown("Generate compliant employment letters and paystubs for Fintech verification.")

# Sidebar - Company Details (The "Employer")
st.sidebar.header("🏢 Company Details (The LLC)")
company_name = st.sidebar.text_input("LLC Name", "My Awesome LLC")
company_address = st.sidebar.text_area("US Address", "123 Innovation Dr, Suite 100, Wyoming, USA")
ein_number = st.sidebar.text_input("EIN (Tax ID)", "XX-XXXXXXX")
uploaded_logo = st.sidebar.file_uploader("Upload Company Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])

# Main Area - Employee Details (You)
st.header("👤 Employee / Contractor Details")
col1, col2 = st.columns(2)
with col1:
    emp_name = st.text_input("Your Full Name", "John Doe")
    emp_title = st.text_input("Job Title", "Director of Operations")
    salary_amount = st.number_input("Monthly Income ($)", min_value=0.0, value=3000.0, step=100.0)

with col2:
    emp_address = st.text_input("Your Local Address", "House 123, Street 4, City, Country")
    start_date = st.date_input("Date Joined", datetime.date(2023, 1, 1))
    pay_date = st.date_input("Paystub Date", datetime.date.today())

st.markdown("---")
st.subheader("📄 Select Document to Generate")

doc_type = st.radio("Choose Document Type:", ["Employment Verification Letter", "Monthly Paystub"])

# Generate Logic
if st.button(f"Generate {doc_type}"):
    if not company_name or not emp_name:
        st.error("Please fill in at least the Company Name and Your Name.")
    else:
        # Handle Logo Temp File
        logo_path = None
        if uploaded_logo:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(uploaded_logo.getvalue())
                logo_path = tmp_file.name

        # Create PDF object
        pdf_out = None
        file_name = ""

        if doc_type == "Employment Verification Letter":
            pdf_out = create_letter(company_name, company_address, ein_number, emp_name, emp_title, salary_amount, start_date, logo_path)
            file_name = f"Employment_Letter_{emp_name.replace(' ', '_')}.pdf"
        
        elif doc_type == "Monthly Paystub":
            pdf_out = create_paystub(company_name, company_address, emp_name, emp_address, salary_amount, pay_date, logo_path)
            file_name = f"Paystub_{pay_date}_{emp_name.replace(' ', '_')}.pdf"

        # Save to byte string for download
        pdf_bytes = pdf_out.output(dest='S').encode('latin-1')
        
        st.success("Document Generated Successfully!")
        
        # Download Button
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf"
        )

        # Cleanup temp logo
        if logo_path:
            os.remove(logo_path)
