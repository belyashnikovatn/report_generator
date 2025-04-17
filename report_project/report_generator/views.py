import csv
import io
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import CSVUploadForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from .utils import generate_docx_report


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file:
            return render(request, 'upload.html', {
                'error': 'Файл не был загружен. Пожалуйста, выберите .csv файл.'
            })

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        config = settings.REPORT_CONFIG
        display_fields = config['fields_to_display']
        required_field = config['required_field']
        mapping = config.get('field_mappings', {})
        reverse_mapping = {v: k for k, v in mapping.items()}

        filtered_data = []
        for row in reader:
            transformed = {
                display_name: row.get(reverse_mapping.get(display_name, ''), '').strip()
                for display_name in display_fields
            }

            if not transformed.get(required_field):
                continue

            filtered_data.append(transformed)

        request.session['report_data'] = filtered_data
        return redirect('show_report')

    return render(request, 'upload.html')


def show_report(request):
    data = request.session.get('report_data', [])
    total = 0
    config = settings.REPORT_CONFIG
    sum_fields = config.get("sum_fields", [])

    for row in data:
        for field in sum_fields:
            try:
                total += float(row.get(field, 0))
            except (ValueError, TypeError):
                pass

    return render(request, 'report.html', {'data': data, 'total': round(total, 3)})


def download_report(request):
    data = request.session.get('report_data', [])
    config = settings.REPORT_CONFIG
    sum_fields = config.get("sum_fields", [])

    total = 0
    for row in data:
        for field in sum_fields:
            try:
                total += float(row.get(field, 0))
            except (ValueError, TypeError):
                pass

    document = generate_docx_report(data, round(total, 3))

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = 'attachment; filename="report.docx"'
    document.save(response)
    return response
