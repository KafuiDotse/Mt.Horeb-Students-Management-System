from fpdf import FPDF

pdf=FPDF()
class PDFWithTable():
    def add_table(self, header, data):
        # Add header
        for col in header:
            pdf.set_font("Arial","B",12)
            pdf.cell(60, 10, col, 1)
        pdf.set_font("Arial",size=12)
        pdf.ln()

        # Add data
        for row in data:
            for col in row:
                pdf.cell(60, 10, str(col), 1)
            pdf.ln()

def info(id,name,gender,dob,pob,nationality,admission_date):
    pdf.cell(70,7,"Student ID",1)
    pdf.cell(120,7,id,1)
    pdf.ln()
    pdf.cell(70,7,"Student Name",1)
    pdf.cell(120,7,name,1)
    pdf.ln()
    pdf.cell(70,7,"Gender",1)
    pdf.cell(30,7,gender,1)
    pdf.cell(50,7,"Date of Birth:",1)
    pdf.cell(40,7,dob,1)
    pdf.ln()
    pdf.cell(70,7,"Place of Birth",1)
    pdf.cell(30,7,pob,1)
    pdf.cell(50,7,"Nationality:",1)
    pdf.cell(40,7,nationality,1)
    pdf.ln()
    pdf.cell(70,7,"Admission Date",1)
    pdf.cell(120,7,admission_date,1)