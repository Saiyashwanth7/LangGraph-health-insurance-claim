import fitz
import base64

def extract_pages(pdf_source):
    """
    Accepts either a file path (str) or raw PDF bytes.
    Returns a list of dicts with page_num, text, and base64 image.
    """
    if isinstance(pdf_source, bytes):
        doc = fitz.open(stream=pdf_source, filetype="pdf")
    else:
        doc = fitz.open(pdf_source)
    pages=[]
    for i,page in enumerate(doc):
        #Store text if there is any text in the page
        text=page.get_text()
        
        #PDFs may use images as the pages, so we need to store the image of the same page as a back up
        pix=page.get_pixmap()
        img=pix.tobytes("png")      
        page_image = base64.standard_b64encode(img).decode()
        pages.append(
            {
                'page_num':i+1,
                'text':text,
                'image':page_image
            }
        )
    doc.close()
    return pages

