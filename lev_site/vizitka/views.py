from django.shortcuts import render

def home(request):
    context = {
        'title': 'Мой сайт-визитка',
        'content': 'Добро пожаловать!'
    }
    return render(request, 'vizitka/home.html', context)
