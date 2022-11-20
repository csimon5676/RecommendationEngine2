#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 10:38:18 2022

@author: charlessimon
"""
import pandas as pd
import numpy as np
from imdb import IMDb
from io import StringIO
from sklearn.cluster import KMeans 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import Levenshtein
from sklearn.metrics.pairwise import cosine_similarity


def format_year(x):
        if (x[x.rfind('(')+1] == '1') or (x[x.rfind('(')+1] == '2'):
            year = x[x.rfind('(')+1:x.rfind('(')+5]
            return int(year)
        else:
            return 0
def format_title(x):
    if (isinstance(x,str)):
        if (x[x.rfind('(')+1] == '1') or (x[x.rfind('(')+1] == '2'):
            title = x[0:x.rfind('(')]
            return str(title)
        else:
            return str(x)
    else:
        return str('title not available')
def format_id(x):
        if x[0]=='t':
            return int(x[2:])
        else:
            return int(x)
class Engine:
    def __init__(self):
        #self.ia = IMDb()
        self.K = 10
        self.cluster_param = 2 #0 genre 1 title 2 genre and title
        self.filter_title = False
        self.filter_year = False
        self.filter_plot = False
        self.title_weight=float(0.0)
        self.plot_weight=float(0.0)
        self.a_year_weight =float(0.0)
        self.df1 = pd.read_csv('movies.csv', on_bad_lines='skip').dropna(subset='imdbId')
        self.df2 = pd.read_csv('movies_description.csv', on_bad_lines='skip').dropna(subset='imdb_id')
       
        self.df1['genres'] = self.df1['genres'].map(lambda x: x.split('|'))
        self.df1['Year']= self.df1['title'].map(format_year)
        self.df1['Title_No_Year']= self.df1['title'].map(format_title)
        self.df2['imdb_id']= self.df2['imdb_id'].map(format_id)
        self.df2= self.df2[self.df2['imdb_id'].isin(self.df1['imdbId'])]
        self.df2['overview'] = self.df2['overview'].fillna('No plot available')
        self.df1= self.df1[self.df1['imdbId'].isin(self.df2['imdb_id'])]
        self.df2 = self.df2.drop_duplicates(subset = 'imdb_id')
        self.df_cluster =  self.df1.copy()
        self.selection =0
    def set_K(self, x):
        self.K = x
    def get_K(self):
        return self.K
    def set_cluster_param(self, x):
        self.cluster_param = x
    def get_cluster_param(self):
        if self.cluster_param == 0:
            return 'Genre'
        if self.cluster_param == 1:
            return 'Title'
        if self.cluster_param ==2:
            return 'Title and Genre'
    def set_filter_param(self,x,y,z):
        self.filter_title = x
        self.filter_year = y
        self.filter_plot = z
    def get_filter_param(self):
        filter_by = ''
        if self.filter_title == True:
            filter_by += 'Title '
        if self.filter_year == True:
            filter_by+= 'Year '
        if self.filter_plot == True:
            filter_by+='Plot'
        if (self.filter_plot == False) and (self.filter_year==False) and (self.filter_title==False):
            filter_by = 'Please select an option!'
        return filter_by
    def searchMovieByTitle(self, title):
        movies_df = self.df1[self.df1['title'].str.contains(title)]
        return movies_df.head(10)
    def selectMovie(self, movie_list, index):
        # Offset index to account for array starting at 0
          index -= 1


          # Verify index is not bullshit
          if 0 <= index < len(movie_list):

              # Add movie selection
              self.selection = movie_list['imdbId'].iloc[index]
    def apply_clustering(self):
         conditional = self.cluster_param
         working_df = self.df1
         selection = self.selection
         clusters = self.K
         if(conditional==0):
             split_df = pd.DataFrame(working_df['genres'].tolist())
             genres_object = split_df.stack()
             genres_df = pd.get_dummies(genres_object)
             genres_df = genres_df.groupby(level=0).sum()
             R = genres_df.values
         elif(conditional==1):
             documents = []
             #df_cluster = df_cluster.head(1000)
             working_df['Title_No_Year'].map(lambda x: documents.append(str(x)))
             vectorizer = TfidfVectorizer()
             R = vectorizer.fit_transform(documents)
         elif(conditional == 2):
             documents = []
             #df_cluster = df_cluster.head(1000)
             working_df['Title_No_Year'].map(lambda x: documents.append(str(x)))
             vectorizer = TfidfVectorizer()
             X = vectorizer.fit_transform(documents)
             km = KMeans(n_clusters=clusters, random_state=0)
             km.fit(X)
             labels = km.labels_
             
             #normalize
             labels = labels/max(labels)
             
             split_df = pd.DataFrame(working_df['genres'].tolist())
             genres_object = split_df.stack()
             genres_df = pd.get_dummies(genres_object)
             genres_df = genres_df.groupby(level=0).sum()
             genres_df['Titles']= labels
             
             R = genres_df.values
             
         kmeans = KMeans(n_clusters=clusters, random_state=0)
         kmeans.fit(R)
         labels = kmeans.labels_
         self.df_cluster['cluster'] = labels
         selection_cluster = self.df_cluster[self.df_cluster['imdbId']==self.selection].cluster
         self.df_cluster=self.df_cluster[self.df_cluster['cluster'].isin(selection_cluster)]
         print(clusters, conditional, selection)
    def calculate_lev(self):
        base_case = self.df_cluster[(self.df_cluster['imdbId']==self.selection)]
        comparison_type = "Title_No_Year"
        base_case =base_case[comparison_type].to_list()
        print('lev distance', Levenshtein.distance(base_case[0], 'Toy_Story'))
        #print(base_case[comparison_type].astype(str))
        self.df_cluster['levenshtein'] = self.df_cluster[comparison_type].map(lambda x: Levenshtein.distance(base_case[0], str(x)))
        self.df_cluster['levenshtein'] =  1.0-(self.df_cluster['levenshtein'].astype(float)/float(max( self.df_cluster['levenshtein'])))
   
    def euclidean_distance(self, base_case_year: int, comparator_year: int):
        return abs(base_case_year - comparator_year)
    
    def calculate_euclid(self):
        base_case = self.df_cluster[(self.df_cluster['imdbId']==self.selection)]
        comparison_type = "Year"
        #print(base_case[comparison_type])
        self.df_cluster['euclidean'] = self.df_cluster[comparison_type].map(lambda x: self.euclidean_distance(int(base_case[comparison_type]), x))
        #print(max(self.df_cluster['euclidean']))
        #smalllest year is 0 for no year
        without_zero_years = self.df_cluster[self.df_cluster[comparison_type]!=0]
        max_euclid= max(without_zero_years['euclidean'])
        self.df_cluster['euclidean'] = 1.0-(self.df_cluster['euclidean'].astype(float)/max_euclid)    
    def calculate_cosine(self):
        # list to store all the plots
         plots = []
         # get my selected movie
         base_case_df = self.df2[self.df2['imdb_id']==self.selection]
         # filter the plots to the ones in our cluster
         compare_df = self.df2[self.df2['imdb_id'].isin(self.df_cluster['imdbId'])]
         # add all the plots to a list
         for i , row in base_case_df.iterrows():
             movie_plot = row['overview']
             plots.append(movie_plot)

         for i, row in compare_df.iterrows():
             movie_plot = row['overview']
             plots.append(movie_plot)

         plots = tuple(plots)

         tfidf_vectorizer = TfidfVectorizer()
         tfidf_matrix = tfidf_vectorizer.fit_transform(plots)

         results = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
         results = np.transpose(results)
         self.df_cluster['cosine_similarity'] = results[1:,:]
    
    def filter_and_sort(self):
        self.df_cluster['score'] = 0
        if self.filter_title == True:
            self.calculate_lev()
            self.df_cluster['score'] += self.title_weight*self.df_cluster['levenshtein']
        if self.filter_plot == True:
            self.calculate_cosine()
            self.df_cluster['score'] += self.plot_weight*self.df_cluster['cosine_similarity']
        if self.filter_year == True:
            self.calculate_euclid()
            self.df_cluster['score'] +=self.a_year_weight* self.df_cluster['euclidean']
        recommendations_df = self.df_cluster = self.df_cluster.sort_values(by = 'score', ascending=False)
        return recommendations_df
        
        
    