from django.shortcuts import render

# Create your views here.

def main(request):
    return render(request, 'main.html', {'current_page': 'main'})

def about(request):
    return render(request, 'about.html', {'current_page': 'about'})

def service(request):
    return render(request, 'service.html', {'current_page': 'service'})

def contact(request):
    return render(request, 'contact.html', {'current_page': 'contact'})
