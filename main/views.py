# main/views.py
from django.shortcuts import render

def home(request):
    latest_news = [
        {'title': 'خبر اول', 'image_url': 'https://via.placeholder.com/200'},
        {'title': 'خبر دوم', 'image_url': 'https://via.placeholder.com/200'},
    ]
    return render(request, 'home.html', {'latest_news': latest_news})
