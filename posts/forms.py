from django.forms import ModelForm, Textarea
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст",
            "group": "Группа",
            "image": "Картинка"
        }
        help_texts = {
            "group": "Группу выбирать необязательно",
            "image": "Картинку тоже"
        }

    def edit(self):
        post = self.instance
        post.text = self.cleaned_data["text"]
        post.group = self.cleaned_data["group"]
        post.image = self.cleaned_data["image"]
        post.save()


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": Textarea
        }
