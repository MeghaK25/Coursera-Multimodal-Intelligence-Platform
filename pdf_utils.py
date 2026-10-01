from PyPDF2 import PdfReader

def extract_pdf_text(file_path: str):
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            cleaned_text = " ".join(page_text.split())
            pages.append({
                "text": cleaned_text,
                "page": page_number
            })

    return pages
