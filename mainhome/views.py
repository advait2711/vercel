from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http.response import HttpResponse
from pdf2docx import Converter
from docx2pdf import convert
import tempfile
import io
import os


@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

def convert_docx_to_pdf(docx_file, buffer):
    """Convert DOCX to PDF and store the result in buffer."""
    
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx:
        temp_docx.write(docx_file.read())
        temp_docx.flush()
        temp_docx_path = temp_docx.name  

   
    temp_pdf_path = temp_docx_path.replace('.docx', '.pdf')

    
    convert(temp_docx_path, temp_pdf_path)

    
    with open(temp_pdf_path, 'rb') as pdf_file:
        buffer.write(pdf_file.read())

    
    os.remove(temp_docx_path)
    os.remove(temp_pdf_path)



def convert_pdf_to_docx(pdf_file, buffer):
    """Convert PDF to DOCX and store the result in buffer."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(pdf_file.read())
        temp_pdf.flush()

    converter = Converter(temp_pdf.name) 
    converter.convert(buffer)
    converter.close()  
    os.remove(temp_pdf.name)


def handle_file_conversion(file, conversion_func, output_mime_type, output_filename):
    """
    Generic handler for file conversion.
    
    Args:
        file: Uploaded file (PDF or DOCX).
        conversion_func: Function to perform conversion (either PDF-to-DOCX or DOCX-to-PDF).
        output_mime_type: The MIME type for the response (application/pdf or DOCX MIME type).
        output_filename: Name for the output file.
    
    Returns:
        HttpResponse with the converted file.
    """
    buffer = io.BytesIO()
    conversion_func(file, buffer)  
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type=output_mime_type)
    response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
    return response


def pdf_to_docx_view(request):
    if request.method == 'POST':
        if 'pdf_file' in request.FILES:
            pdf_file = request.FILES['pdf_file']
            docx_filename = pdf_file.name.replace('.pdf', '.docx')
            return handle_file_conversion(pdf_file, convert_pdf_to_docx,
                                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                           docx_filename)
        
        elif 'docx_file' in request.FILES:
            docx_file = request.FILES['docx_file']
            pdf_filename = docx_file.name.replace('.docx', '.pdf')
            return handle_file_conversion(docx_file, convert_docx_to_pdf, 'application/pdf', pdf_filename)

    return render(request, 'conversion.html')


def logout_user(request):
    logout(request)
    return redirect('login')
