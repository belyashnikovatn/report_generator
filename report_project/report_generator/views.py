import csv
from datetime import datetime
import io

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .utils import generate_docx_report


def format_value(value, field, number_format, unit_divisors=None):
    """Форматирует значение на основе округления и единиц измерения."""
    format_digits = number_format.get(field)
    divisor = unit_divisors.get(field, 1) if unit_divisors else 1

    try:
        numeric_value = float(value) / divisor
        if format_digits is not None:
            numeric_value = round(numeric_value, format_digits)
        return numeric_value
    except (ValueError, TypeError):
        return value


def calculate_total(data, sum_fields, number_format=None, unit_divisors=None):
    """Вычисляет итоговую сумму с учётом единиц измерения и округления."""
    total = 0
    for row in data:
        for field in sum_fields:
            try:
                divisor = unit_divisors.get(field, 1) if unit_divisors else 1
                value = float(row.get(field, 0)) / divisor
                total += value
            except (ValueError, TypeError):
                pass
    if number_format:
        digits = max(number_format.get(f, 3) for f in sum_fields)
        return round(total, digits)
    return total


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
                display_name: row.get(reverse_mapping.get(
                    display_name, ''), '').strip()
                for display_name in display_fields
            }

            if not transformed.get(required_field):
                continue

            filtered_data.append(transformed)

        request.session['report_data'] = filtered_data
        return redirect('show_report')

    return render(request, 'upload.html')


def show_report(request):
    raw_data = request.session.get('report_data', [])
    config = settings.REPORT_CONFIG
    sum_fields = config.get("sum_fields", [])
    number_format = config.get("number_format", {})
    unit_divisors = config.get("unit_divisors", {})

    total = calculate_total(raw_data, sum_fields, number_format, unit_divisors)

    data = []
    for row in raw_data:
        formatted_row = {
            field: format_value(value, field, number_format, unit_divisors)
            for field, value in row.items()
        }
        data.append(formatted_row)

    return render(request, 'report.html', {'data': data, 'total': total})


def download_report(request):
    raw_data = request.session.get('report_data', [])
    config = settings.REPORT_CONFIG
    sum_fields = config.get("sum_fields", [])
    number_format = config.get("number_format", {})
    unit_divisors = config.get("unit_divisors", {})

    total = calculate_total(raw_data, sum_fields, number_format, unit_divisors)

    data = []
    for row in raw_data:
        formatted_row = {
            field: format_value(value, field, number_format, unit_divisors)
            for field, value in row.items()
        }
        data.append(formatted_row)

    document = generate_docx_report(data, total)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{timestamp}.docx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    document.save(response)
    return response
