from django.contrib.flatpages import views
from django.urls import path

urlpatterns = [
    path("about-author/", views.flatpage, {"url": "/about-author/"}, name="about-author"),
    path("about-spec/", views.flatpage, {"url": "/about-spec/"}, name="about-spec"),
    path("about-us/", views.flatpage, {"url": "/about-us/"}, name="about"),
    path("terms/", views.flatpage, {"url": "/terms/"}, name="terms"),
]
