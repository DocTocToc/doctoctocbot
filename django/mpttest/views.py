from django.shortcuts import render
from .models import Treedj

def show_genres(request):
    return render(request, "mpttest/status.html", {'treedj': Treedj.objects.all()})
