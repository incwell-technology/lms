from django import forms
from leave_manager.models import Holiday

class DateInput(forms.DateInput):
    input_type = 'date'

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = '__all__'
        widgets = {
            'from_date': DateInput(),
            'to_date': DateInput()
        }
    def __init__(self, *args, **kwargs):
        super(HolidayForm, self).__init__(*args, **kwargs)
        self.fields['from_date'].widget.attrs={
            'id': 'datepicker_to',
        }
        self.fields['to_date'].widget.attrs={
            'id': 'datepicker_to',
        }