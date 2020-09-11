from django.shortcuts import render


def index(request):
    return render(request, "game_index.html")
