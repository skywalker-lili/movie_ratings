from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from .models import Movie
from django.template import loader
from .helper import find_similar_3

# Create your views here.
from django.http import HttpResponse


# Create your views here.
def index(request):
    movie_list = []
    freq_1 = []
    freq_2 = []
    freq_3 = []
    search = "No query input yet"
    if request.GET.get('search'):
        search = request.GET.get('search')
        movie_list,freq_1, freq_2, freq_3 = find_similar_3(search, 30) # messaged sorted by distance compared to search_query
    return render_to_response('movie_ratings/index.html', \
                             {'movie_list': movie_list,\
                             'input_query':search,\
                             'freq_1':freq_1,\
                             'freq_2':freq_2,\
                             'freq_3':freq_3,})

