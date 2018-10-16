from django.shortcuts import render
from .models import Treedj, Tweetdj

def show_conversations(request):
    return render(request, "conversation/status.html", {'treedj': Treedj.objects.all()})