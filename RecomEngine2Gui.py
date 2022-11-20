#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 11:01:52 2022

@author: charlessimon
"""

from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
import urllib.request
import io 
from PIL import ImageTk, Image
import requests
from io import BytesIO
import RecomEngine2 as RE2

def displayMovies(results_df, limit_rows, title_display, rating_bool):
    # Pull out the movie ids
    display_window = Toplevel()
    display_window.title(title_display)
    display_window.geometry('700x250')

    movie_ids = results_df['imdbId'].to_list()
    
    row_num = 0
    index = 0

    # Get movies from original dataframe
    for i in movie_ids:

        # Get row
        movie_item = hal.df_cluster[(hal.df_cluster['imdbId'] == i)]

        # Get more movie data from imdb
        if(rating_bool):
            movie = hal.ia.get_movie(movie_item['imdbId'].to_list()[0])
            rating = movie.get('rating')
            link = movie.get('cover url')
            
        title = movie_item['title'].to_list()[0]
        print_selection=''
        index +=1
        if(rating_bool):
            print_selection +=str(index)+'. ' + str(title)+' rating: ' + str(rating)
        else:
            print_selection +=str(index)+'. ' + str(title)
        search_options = Label(display_window,text = print_selection).pack()
        

        # Count number of results
        if limit_rows:
            row_num += 1

        # End method if number of results has been reached
        if row_num == 10:
            return  
def selecitonWindow(results_df):
    selection_window = Toplevel()
    selection_window.title("Search Results")
    movie_ids = results_df['imdbId'].to_list()
    row_num = 0
    choice = IntVar()
    print_selections = ""
    search_options = Label(selection_window,text = "Selction Window").pack()
    # Get movies from original dataframe
    for i in movie_ids:

        # Get row
        movie_item = hal.df1.loc[(hal.df1['imdbId'] == i)]

        year = movie_item['Year'].to_list()[0]

        # Format for displaying
        
        
        index = 1 + row_num

        title = movie_item['title'].to_list()[0]

        print_selections += str(index) + ". " + str(title) +"\n"
        #print(print_selections)
        # Count number of results
        row_num += 1
        Radiobutton(selection_window, text=str(index) + ". " + str(title), variable=choice, value=int(index)).pack(anchor=W)
        # End method if number of results has been reached
        if row_num == 10:
            break
    def clicked(value):
        global button1_bool
        label = Label(selection_window, text=value)
        label.pack()
        hal.selectMovie(results_df, int(value))
        if hal.selection != 0:
            button1_bool=True
        else:
            button1_bool = False
        #print(button1_bool)
        print(hal.selection)
# =============================================================================
#             if(re.user_selection):
#                 button5['state']= NORMAL
#                 button4['state']=NORMAL
# =============================================================================
    myButton = Button(selection_window, text="Make Selection", command=lambda: clicked(choice.get()))
    myButton.pack()
        
def Button1():
    search_df= hal.searchMovieByTitle(search_title.get())
    if(search_df.empty):
        messagebox.showerror("Error", "Search returned no results")
    else:
        selecitonWindow(search_df)
# =============================================================================
#     if(re.user_selection):
#         button5['state']= NORMAL
#         button4['state']=NORMAL
# =============================================================================
    search_title.delete(0,END)
    

def Button2():
    try:
        user_input = int(K_entry.get())
        if(user_input < 2):
            raise EXCEPTION  
        
    except:
        messagebox.showerror("Error", "K must be int >=2!")
        return
  
    hal.set_K(user_input)
    k_label = Label(frame2, text ='K is '+ str(hal.get_K())).pack()
    
def Button3(value):
    global button4
    hal.set_cluster_param(value)
    cluster_label = Label(frame2 ,text = 'Cluster By: ' + str(hal.get_cluster_param()))
    cluster_label.pack()
    if button1_bool == True:
        button4['state']=NORMAL
def Button4():
    #cluster function 
    hal.apply_clustering()
    def Button5(value1, value2, value3):
        filter_choice1.set(False)
        filter_choice2.set(False)
        filter_choice3.set(False)
        r2.selection_clear()
        r3.selection_clear()
        print(value1, value2, value3)
        hal.set_filter_param(value1,value2, value3)
        filter_label = Label(filter_window, text = 'Filter using:' + str(hal.get_filter_param())).pack()
        if hal.get_filter_param() == 'Please select an option!':
            print('Filter not performed')
        else:
            #calculate metrics
            #filter function
            print('Filtering')
            
            try:
                if(weight_title.get()):
                    title_weight = float(weight_title.get())
                    print(title_weight)
                    hal.title_weight=title_weight
                if(weight_plot.get()):
                    plot_weight = float(weight_plot.get())
                    print(plot_weight)
                    hal.plot_weight = plot_weight
                if(weight_year.get()):
                    year_weight =float(weight_year.get())
                    print(year_weight)
                    hal.a_year_weight = year_weight
            except:
                messagebox.showerror("Weights must be numbers!")
            movie_recommendations = hal.filter_and_sort()
            displayMovies(movie_recommendations, True, 'Your Recommendations', False)
    filter_window = Toplevel()
    filter_window.title('Filter Parameters')
    filter_instructions = Label(filter_window, text='Select filtering parameter(s) and add weights for cluster').pack()
    filter_choice1 = BooleanVar()
    filter_choice2 = BooleanVar()
    filter_choice3 = BooleanVar()
    r1 = Radiobutton(filter_window, text='Title', variable=filter_choice1 , value=True)
    r1.pack(anchor=W)
    weight_title = Entry(filter_window,width=10)
    weight_title.pack()
    r2 = Radiobutton(filter_window, text='Year', variable=filter_choice2, value=1)
    r2.pack(anchor=W)
    weight_year = Entry(filter_window,width=10)
    weight_year.pack()
    r3 = Radiobutton(filter_window, text='Plot', variable=filter_choice3, value=2)
    r3.pack(anchor=W)
    weight_plot = Entry(filter_window,width=10)
    weight_plot.pack()
    button5 = Button(filter_window, text = 'Filter', command =lambda: Button5(filter_choice1.get(), filter_choice2.get(), filter_choice3.get()), padx=50, pady=20 ).pack()
    return    
    
root = Tk()  
root.title("Recomemndataion Engine")    
hal = RE2.Engine()
frame1 = LabelFrame(root, text='Search Options', padx=20, pady=20)
frame1.pack(padx=5, pady=5)
frame2 = LabelFrame(root, text = 'Set K and parameter\n choice for clustering ', padx=50, pady=50)
frame2.pack(padx=5, pady=5)

frame3 = LabelFrame(root, text = 'Filter Selection Cluster ', padx=50, pady=50)
frame3.pack(padx=10, pady=10)



search_title = Entry(frame1,width=20)
search_title.pack()

button1 = Button(frame1, text = 'Search Title', padx=20, pady=20, command = Button1)
button1.pack()


K_entry = Entry(frame2,width=20)
K_entry.pack()
button2 = Button(frame2, text ='Set K', padx=50, pady=20, command = Button2)
button2.pack()
#true genre false title
param_choice = IntVar()
Radiobutton(frame2, text='Genre', variable=param_choice, value=0).pack(anchor=W)
Radiobutton(frame2, text='Title', variable=param_choice, value=1).pack(anchor=W)
Radiobutton(frame2, text='Title and Genre', variable=param_choice, value=2).pack(anchor=W)

button3 = Button(frame2, text ='Clustering parameter', padx=50, pady=20, command = lambda: Button3(param_choice.get())).pack()
button4 = Button(frame2, text = 'Cluster', command =Button4, padx=50, pady=20, state=DISABLED)
button4.pack()
button4_exp = Label(frame2, text ='Cluster will become available after searching\n and selecting a movie and choosing parameters.').pack()



root.mainloop()

