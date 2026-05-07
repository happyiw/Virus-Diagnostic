from docx import Document

doc = Document('kursach.docx')
for para in doc.paragraphs:
    print(para.text)