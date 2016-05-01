from .models import Movie_File, Movie
import os
import Levenshtein
import json
from django.conf import settings

def read_file(relative_path):
    # relative_path = Movie_File.objects.get(id = n).address;
    path = "".join([settings.BASE_DIR, relative_path])
    with open(path) as data_file:
        data = json.load(data_file)
    return data

# Calculate edit distance between query and movie_title    
def _edit(query, movie_title):
    return Levenshtein.distance(query.lower(), movie_title.lower())

# return the list of movies that has ALL match on the query
def _inverted_index(query, movies, inverted_index):
    
    intersect = []
    first_word = True
    for item in query.split():
        word = item.lower()
        if first_word:
            try:
                intersect = inverted_index[word]
            except KeyError:
                continue
        else:
            try:
                for id in intersect:
                    if id not in inverted_index[word]:
                        intersect.remove(id)
            except KeyError:
                continue
    
    # Get the movies whos id are in the intersect
    intersect_movies = []
    for id in intersect:
        intersect_movies.append(movies[id])
    
    return intersect_movies
    
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
    from_low = min(temp_weights + [0])
    from_high = max(temp_weights + [0])+0.0000001

    temp_k = []
    for i in range(k): # get the top k value and adjust word size
        temp_k.append((temp[i][0], mapping(temp[i][1], from_low, from_high, to_low, to_high)))
    
    # Create a new dic
    frequency_list = []
    for word_weight in temp_k:
        temp = [word_weight[0], word_weight[1]]
        frequency_list.append(temp)
    
    return frequency_list
    
def find_similar_n(query, n = 5, k=30):
    
    # Read movie information
    movies = read_file("/ratings/json/movies.160501.json")
    # Read the inverted index file
    inverted_index = read_file("/ratings/json/inverted_index.json")
    
    # Get candidate movies by inverted index
    candidate_movies = _inverted_index(query, movies, inverted_index)
    candidate_num = len(candidate_movies)
    
    # For movies in the candidate_movies, re-order by edit distance
    editDis_result = []
    for movie in candidate_movies:
        movie_year = " ".join([movie["name"],movie["year"]]).lower()
        editDis_result.append([(_edit(query, movie_year)), movie["name"], movie["year"]])
    
    editDis_result.sort(key=lambda x: x[0]) # sort by distance
    
    if len(editDis_result)> n:
        editDis_result = editDis_result[:n] # only needs top n results
    
    # if the candidates are too short, use edit distance to find rest movies
    if len(editDis_result) < n:
        shortage_num = n - len(editDis_result)
        additional_movies = []
        for movie in movies:
            movie_year = " ".join([movie["name"],movie["year"]]).lower()
            additional_movies.append([(_edit(query, movie_year)), movie["name"], movie["year"]])
        
        additional_movies.sort(key=lambda x: x[0]) # sort by distance
        
        # Append additional_movies if it's not in the editDis_result yet
        movie_already_in = set([])
        for movie in editDis_result:
            movie_already_in.add(movie[1])
        
        added_count = 0
        for movie in additional_movies:
            if added_count == shortage_num:
                break
            if movie[1] not in movie_already_in:
                editDis_result.append(movie)
                added_count += 1
        
    result = [[None]*6 for i in range(n)] # result as a list of n lists
    count = 0
    for item in editDis_result:
        name = item[1]
        year = item[2]
        movie = find_movie(name, year, movies)
        result[count][0] = name + " (" + year + ")" # format like: "Wizard of Oz (2008)"
        result[count][1] = movie['rating_predict'] # get predicted ratings
        result[count][2] = movie['rating_actual'] # get real ratings
        result[count][3] = movie['comment'] # get the words for predicting ratings
        result[count][4] = top_words(movie['top_words'], k, 15, 50) # re-arrane the top words
        result[count][5] = movie['preview']
        count += 1
    return result, [result[i][4] for i in range(n)]