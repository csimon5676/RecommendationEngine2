import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def format_year(x):
    if (x[x.rfind('(')+1] == '1') or (x[x.rfind('(')+1] == '2'):
        year = x[x.rfind('(')+1:x.rfind('(')+5]
        return int(year)


def format_title(x):
    if (isinstance(x, str)):
        if (x[x.rfind('(')+1] == '1') or (x[x.rfind('(')+1] == '2'):
            title = x[0:x.rfind('(')]
            return str(title)
        else:
            return (x)


def format_id(x):
    if x[0] == 't':
        return int(x[2:])
    else:
        return int(x)


df1 = pd.read_csv('movies.csv', on_bad_lines='skip').dropna(subset='imdbId')
df2 = pd.read_csv('movies_description.csv', on_bad_lines='skip').dropna(subset='imdb_id')
df_cluster = df1.copy()


df1['genres'] = df1['genres'].map(lambda x: x.split('|'))
df1['Year'] = df1['title'].map(format_year)
df1['Title_No_Year'] = df1['title'].map(format_title)
df1 = df1.dropna()
df2['imdb_id'] = df2['imdb_id'].map(format_id)
df2 = df2[df2['imdb_id'].isin(df1['imdbId'])]
df_cluster = df1.copy()

selection = 114709

cluster = [113041, 105629, 84809]

# list to store all the plots
plots = []
# get my selected movie
base_case = df2[df2['imdb_id']==selection]
# filter the plots to the ones in our cluster
compare_df = df2[df2['imdb_id'].isin(cluster)]
# add all the plots to a list
for i , row in base_case.iterrows():
  movie_plot = row['overview']
  plots.append(movie_plot)

for i, row in compare_df.iterrows():
  movie_plot = row['overview']
  plots.append(movie_plot)

plots = tuple(plots)

tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(plots)

results = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)

for y in results[0]:
  print("%.2f" % (y))