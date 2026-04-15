from django import forms


class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(label="Upload PDF")

    def clean_pdf_file(self):
        uploaded = self.cleaned_data["pdf_file"]
        if not uploaded.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        return uploaded
