from django import forms
from .models import Script


class ScriptForm(forms.ModelForm):
    class Meta:
        model = Script
        fields = '__all__'

    class Media:
        css = {
            'all': (
                'internals/css/codemirror.css',
                'internals/css/monokai.css'
            )
        }
        js = (
            'internals/js/codemirror.js',
            'internals/js/python.js',
        )
