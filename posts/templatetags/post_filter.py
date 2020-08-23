from django import template

register = template.Library()


@register.filter
def get_followed_authors(user):
    return user.follower.all().values_list("author", flat=True)
