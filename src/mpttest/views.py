from django.shortcuts import render
from .models import Treedj, Tweetdj

def show_genres(request):
    
    return render(request, "mpttest/status.html", {'treedj': Treedj.objects.all()})
