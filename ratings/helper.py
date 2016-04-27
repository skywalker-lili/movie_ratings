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

# Give a value and its old range, linear mapping to a new range as an integer
def mapping(value, from_low, from_high, to_low, to_high):
    new_value = float(value-from_low)/(from_high-from_low) * (to_high-to_low) + to_low
    return int(new_value)

# Given a dictionary of word-weights, return top k words with
# adjusted weight for word cloud according to_low, to_high
def top_words(top_dic, k, to_low, to_high): 
    if k > len(top_dic): # k needs to be at most length of dic keys
        k = len(top_dic)
    
    temp = []
    temp_weights = []
    for word_weight in top_dic:
        temp.append((word_weight[0], float(word_weight[1])))
        temp_weights.append(float(word_weight[1]))
    temp.sort(key = lambda x: x[1], reverse = True) # descending sort by value
    from_low = min(temp_weights)
    from_high = max(temp_weights)+0.000000001
    
    temp_k = []
    for i in range(k): # get the top k value and adjust word size
        temp_k.append((temp[i][0], mapping(temp[i][1], from_low, from_high, to_low, to_high)))
    
    # Create a new dic
    frequency_list = []
    for word_weight in temp_k:
        temp = [word_weight[0], word_weight[1]]
        frequency_list.append(temp)
    
    return frequency_list
    
def find_similar_3(query, k=30):
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
        result[count][4] = top_words(movie['top_words'], k, 15, 50) # re-arrane the top words
        count += 1
    return result, result[0][4], result[1][4], result[2][4]