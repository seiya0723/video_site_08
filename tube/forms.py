from django import forms
from .models import Video


class VideoEditForm(forms.ModelForm):
    class Meta:
        model  = Video
        fields = ["title", "description", "dt",]

