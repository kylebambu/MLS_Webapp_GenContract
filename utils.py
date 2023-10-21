import requests
import streamlit as st
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64

@st.cache_data
def make_http_request(url, params=None, headers=None):
    try:
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()  # If the response is in JSON format
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed with error: {e}")
        return None
    
def get_form_field_coordinates(pdf_template):
    pdf_reader = PyPDF2.PdfReader(open(pdf_template, "rb"))

    # Create a list to store form field information
    form_fields = []

    for page in pdf_reader.pages:
        if '/Annots' in page and '/Fields' in page['/Annots'][0]:
            for field in page['/Annots'][0]['/Fields']:
                field_info = page['/Annots'][0]['/Fields'][field]
                field_type = field_info.get('/FT')
                field_name = field_info.get('/T')
                field_rect = field_info['/Rect']

                form_fields.append({
                    "type": field_type,
                    "name": field_name,
                    "coordinates": field_rect
                })

    return form_fields

def fill_form_field(pdf_template, pdf_output, field_name, field_value):
    pdf_reader = PyPDF2.PdfReader(open(pdf_template, "rb"))
    pdf_writer = PyPDF2.PdfWriter()

    form_fields = get_form_field_coordinates(pdf_template)

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)

    # Find the coordinates of the specified form field
    for field in form_fields:
        if field['name'] == field_name:
            x, y, width, height = field['coordinates']
            break

    # Use ReportLab to add text to the specified coordinates
    c = canvas.Canvas(pdf_output, pagesize=letter)
    c.setLineWidth(1)
    c.drawString(x, y, field_value)
    c.save()

def pdf_to_data_url(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
        data_url = base64.b64encode(data).decode("utf-8")
    return data_url