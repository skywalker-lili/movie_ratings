from .models import Movie_File, Movie
import os
import Levenshtein
import json
from django.conf import settings

def read_file(n):
    relative_path = Movie_File.objects.get(id = n).address;
    path = "".join([settings.BASE_DIR, relative_path])
    with open(path) as data_file:
        data = json.load(data_file)
    return data

def _edit(query, movie_title):
    return Levenshtein.distance(query.lower(), movie_title.lower())

def find_movie(name, year, movies):
    for movie in movies:
        if movie["name"] == name and movie["year"] == year:
            return movie
    return "No movie found!"     
    
def find_similar_3(query):
    # we store all movie information in one file, so just need to read first file
    # first file will be automatically named with id = 1 by Django
    movies = read_file(1)
    
    temp_result = []
    for movie in movies:
        # store the id and each movie's distance to
        temp_result.append(((_edit(query, " ".join([movie["name"],movie["year"]]))),\
        movie["name"], movie["year"]))
    
    temp_result = sorted(temp_result, key=lambda x: x[0]) # sort by distance
    
    if len(temp_result)>3:
        temp_result = temp_result[:3] # only needs top 3 results
        
    result = [[None]*5, [None]*5, [None]*5] # result as a list of 3 tuples
    count = 0
    for item in temp_result:
        name = item[1]
        year = item[2]
        movie = find_movie(name, year, movies)
        result[count][0] = name + " (" + year + ")" # format like: "Wizard of Oz (2008)"
        result[count][1] = movie['rating_predict'] # get predicted ratings
        result[count][2] = movie['rating_actual'] # get real ratings
        result[count][3] = movie['comment'] # get the words for predicting ratings
        count += 1
    return result