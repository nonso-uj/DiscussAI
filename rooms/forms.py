from django import forms
from .models import Room, Message, Topic


class RoomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'id': 'room_name', 
            'placeholder': 'E.g. Mastering Python + Django'
            })
        self.fields['topic'].widget.attrs.update({
            'id': 'room_topic',
            })
        self.fields['description'].widget.attrs.update({
            'id': 'room_about',
            'placeholder': 'Write about your chat room...'
        })
    class Meta:
        model = Room
        fields = ['title', 'topic', 'description']

