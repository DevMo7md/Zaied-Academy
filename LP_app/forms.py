from django import forms
from .models import Lesson, Category
class Lesson_Form(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="التصنيف",
        empty_label="اختر تصنيف",
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'التصنيف'})
    )
    class Meta:
        model = Lesson
        fields = [
            'title',
            'lesson',
            'category',
            'thumnale_image',
            'discrebtion',
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'عنوان الفيديو', 'lable':'العنوان'}),
            'lesson': forms.FileInput(attrs={'class': 'form-control', 'placeholder':'الفيديو', 'lable':'الفيديو'}),
            'discrebtion': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'وصف الفيديو', 'lable':'الوصف'}),
            'thumnale_image': forms.FileInput(attrs={'class': 'form-control', 'placeholder':'صورة الغلاف', 'lable':'صوره الغلاف'}),
        }
