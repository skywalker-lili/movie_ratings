from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Movie
from django.template import loader
from .helper import find_similar_n

# Create your views here.
from django.http import HttpResponse


# Create your views here.
def index(request):
    movie_list = []
    freq_list = []
    search = "No query input yet"
    if request.GET.get('search'):
        search = request.GET.get('search')
        movie_list,freq_list = find_similar_n(search, n = 5, k = 30) # messaged sorted by distance compared to search_query
    return render_to_response('movie_ratings/index.html', \
                             {'movie_list': movie_list,\
                             'input_query':search,\
                             'freq_list':freq_list})
