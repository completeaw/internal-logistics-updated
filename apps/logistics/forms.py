from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select Excel File',
        help_text='Please upload a valid Excel file (.xls or .xlsx)',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        if not file.name.endswith(('.xls', '.xlsx')):
            raise forms.ValidationError('Only Excel files are allowed')
        return file 