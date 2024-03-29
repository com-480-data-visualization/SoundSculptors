# Project of Data Visualization (COM-480)

| Student's name | SCIPER |
| -------------- | ------ |
| Yasmine Chaker | 311675 |
| Alexander Mueller | 312276 |
| Tymur Tytarenko | 375184 |

[Milestone 1](#milestone-1) • [Milestone 2](#milestone-2) • [Milestone 3](#milestone-3)

## Milestone 1 (29th March, 5pm)

**10% of the final grade**

The goal of our project is to show music preferences around the world and to offer a personalized experience to each user based on their music taste. 

### Dataset

In our project, we are using two different datasets.
The **first** one is this fixed dataset from Kaggle: https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023
The **second** one is from [Spotify's API](https://developer.spotify.com/documentation/web-api). This gives access to things like artist popularity per country, song characteristics, and song popularity. 

### Problematic

In our visualization, we are trying to show global music preferences, emphasizing the diversity within and between countries, how countries' music preferences are related and change over time. Adding to this comprehensive visualization, there will also be a feature that personalizes the user experience by incorporating individuals' music preferences into the world map, providing insights into how their personal tastes fit within the broader context of worldwide music preferences.

The **motivation** is a desire to understand and illustrate the diversity of global music cultures, to uncover the threads that connect different peoples through music  by leveraging global listening patterns.

The **overview** of the visualization will be a process of interactive world map in modes and graphical figures with real time updating.

The **target audience** is planned to include people who are interested in music, cultural researchers, and educators who are exploring the global landscape of music in a detailed and interactive way. It's also aimed at casual users who wish to discover new music based on global trends or their personal tastes.

### Exploratory Data Analysis

We are exploring two different datasets. For the **first**, you can find the data exploration and some insights in [milestone1.ipynb](milestone1.ipynb). This is a dataset containing popular songs of 2023 accross different platforms, including Spotify, Deezer, and Apple Music. The **second** dataset we will look at is not fixed, and thus we are not reporting statistics about it. We are using data from the Spotify API. We will be using Spotipy in order to gain access to the data. Here, we list some API functions we believe to be relevant to our project. Additionally, we implemented a small flask server, which we use to test the outputs of the API. The provided [requirements.txt](requirements.txt) gives all the necessary installations to run it.   

Functions:
- `audio_features`: returns the audio features of a song (e.g. energy, danceability)
- `category_playlists`: returns playlists for spotify-created categories. Especially useful since one of these is categories top charts, with the most popular songs at the moment, with a region selector. 
- `current_user_top_tracks`: the most listened songs of the current user. We will be able to tell what the user likes based on their favorite songs.
- `country_codes`: all of the countries Spotify officially supports. This will be useful to make the right API calls. 

 In order to run the flask app:
 - create a spotify developer account and set the environment variables SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET to their respective values
 - run `pip install -r requirements.txt`
 - run `flask run`
 
### Related work

While coming up with the idea we have encountered some projects already related to the world music map, this is one of them:

 Spotify and open-source platform CARTO have created the [“Musical Map of the World”](https://community.spotify.com/t5/App-Features/Spotify-s-NEW-Musical-Map-of-the-World-2-0/td-p/1519929). This creative visualization with an interactive map is making use of Spotify´s data from cities all over the world to give them their special “musical character”.

The Musical Map of the World has music aggregation in world map, but we cannot see the preferences which change over time and we cannot visualize the user's own preferences.

You can find [here](https://towardsdatascience.com/country-wise-visual-analysis-of-music-taste-using-spotify-api-seaborn-in-python-77f5b749b421) another example of visualizations created using the fixed dataset that we chose.

Our approach is original because we want to look at how different countries listen to music, and we want to do it in an interactive way with live updates from the Spotify API instead of one fixed scrape. 

We take this [visualization](https://public.tableau.com/views/MakeoverMonday-Week44-BankHolidays/BankHolidays?%3AshowVizHome=no) as one source of inspiration for our website.

## Milestone 2 (26th April, 5pm)

**10% of the final grade**


## Milestone 3 (31st May, 5pm)

**80% of the final grade**


## Late policy

- < 24h: 80% of the grade for the milestone
- < 48h: 70% of the grade for the milestone

