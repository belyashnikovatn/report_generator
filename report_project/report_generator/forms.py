from django import forms


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Выберите CSV файл',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
