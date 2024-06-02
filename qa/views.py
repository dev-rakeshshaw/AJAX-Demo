# pdf_project/qa/views.py

from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import File, Pages
from PyPDF2 import PdfReader,PdfWriter
from django.conf import settings
from pdf2image import convert_from_path
# import pytesseract
from urllib.parse import urljoin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import os
import uuid


def upload_and_list_files(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for file in files:
            # Extract filename without extension
            filename, extension = os.path.splitext(file.name)
            
            # Create directory based on filename inside 'media' directory
            pdf_dir = os.path.join(settings.MEDIA_ROOT, filename)
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            
            # Save the uploaded file to the created directory
            pdf_path = os.path.join(pdf_dir, file.name)
            with open(pdf_path, 'wb+') as pdf_file:
                for chunk in file.chunks():
                    pdf_file.write(chunk)
            
            # Calculate number of pages
            reader = PdfReader(pdf_path)
            number_of_pages = len(reader.pages)
            
            # Save the file info to the database
            File.objects.create(name=file.name, number_of_pages=number_of_pages, pdf_file=pdf_path.replace(settings.MEDIA_ROOT, ''))
        return redirect('upload_and_list_files')
    
    files = File.objects.all()
    return render(request, 'qa/upload_and_list.html', {'files': files})



def process_pages(request, file_id):
    # Step 1: Retrieve the PDF file path from the "File" model based on the provided file_id
    file_obj = get_object_or_404(File, pk=file_id)
    pdf_relative_path = file_obj.pdf_file.url.split(settings.MEDIA_URL)[-1]

    print("\n\n pdf_relative_path: ", pdf_relative_path)

    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_relative_path)

    print("\n\n pdf_path: ", pdf_path, "\n\n")

    # Step 2: Split the PDF into single pages
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    # Step 3 & 4: Store each single page PDF in "/media/<filename>/splitted_pdfs/" 
    # and convert each single page PDF to JPG images and store them in "/media/<filename>/splitted_images/"
    filename, _ = os.path.splitext(file_obj.name)
    filename = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in filename)  # Replace invalid characters
    for page_num in range(total_pages):
        # Create directory paths based on the filename if they don't exist
        pdf_dir = os.path.join(settings.MEDIA_ROOT, filename, 'splitted_pdfs')
        image_dir = os.path.join(settings.MEDIA_ROOT, filename, 'splitted_images')
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        # Split PDF into single pages and save each page
        page = reader.pages[page_num]
        page_name = f'{filename}_{page_num + 1}'
        print("Processing Page: ",page_name,"\n\n")
        single_page_pdf_path = os.path.join(pdf_dir, f'{page_name}.pdf')
        with open(single_page_pdf_path, 'wb') as single_page_pdf_file:
            single_page_pdf_writer = PdfWriter()
            single_page_pdf_writer.add_page(page)
            single_page_pdf_writer.write(single_page_pdf_file)
        
        # Convert single page PDF to JPG image
        images = convert_from_path(single_page_pdf_path)
        single_page_image_path = os.path.join(image_dir, f'{page_name}.jpg')
        images[0].save(single_page_image_path, 'JPEG')
        
        # Create Pages object and save the paths and raw text
        page_obj = Pages.objects.create(
            file=file_obj,
            name=page_name,
            splitted_pdf_path=os.path.relpath(single_page_pdf_path, settings.MEDIA_ROOT),
            splitted_image_path=os.path.relpath(single_page_image_path, settings.MEDIA_ROOT),
            raw_text=""
        )

    return redirect('upload_and_list_files')


def view_duplicates(request, file_id):
    file_obj = get_object_or_404(File, pk=file_id)
    pages = Pages.objects.filter(file=file_obj)

    date_images_dict = {}
    for page in pages:
        date = page.date
        if date not in date_images_dict:
            date_images_dict[date] = []
        absolute_image_url = urljoin(settings.MEDIA_URL, page.splitted_image_path)
        date_images_dict[date].append({
            'file_id': file_id,
            'page_id': page.id,
            'image_url': absolute_image_url,
            "name":page.name,
            "is_duplicate":str(page.is_duplicate).lower(),

        })

    # print("\n\n",date_images_dict)
    context = {
        'date_images_dict': date_images_dict,
        'file': file_obj
    }

    return render(request, 'qa/duplicate_viewer.html', context)


@csrf_exempt  # You might want to set up CSRF tokens properly in a real-world scenario
def mark_duplicate(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        page_id = request.POST.get('page_id')
        mark_duplicate = request.POST.get('mark_duplicate')
        
        # Handle the data as needed, e.g., updating the database
        if mark_duplicate == 'yes':
            # Mark the page as duplicate in your database
            page = Pages.objects.get(id=page_id)
            page.is_duplicate = True  # Assuming you have an 'is_duplicate' field
            page.save()
        
        # Redirect back to the view_duplicates page
        return HttpResponseRedirect(reverse('view_duplicates', args=[file_id]))