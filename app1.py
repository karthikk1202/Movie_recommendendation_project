import pandas as pd
import pickle
import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Function to fetch movie poster
def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=c6e4ad312dd028afda1488daed2f43d9&language=en-US'.format(
            movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        # Fetch poster from API
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Load movie data and similarity matrix
movies_list_dict = pickle.load(open('movie_list_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_list_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Dash app layout
app.layout = html.Div(
    style={'background-image': 'url("https://c1.wallpaperflare.com/preview/570/413/91/interior-theatre-theater-empty-theater.jpg")',
           'background-size': 'cover',
           'height': '100vh',
           'display': 'flex',
           'flex-direction': 'column',
           'align-items': 'center',  # Center content vertically
           'justify-content': 'center'},  # Center content horizontally
    children=[
        html.Div(
            style={'background-color': 'rgba(0, 0, 0, 0.5)',
                   'padding': '20px',
                   'border-radius': '10px',
                   'text-align': 'center'},  # Align text in the center
            children=[
                html.H1("Movie Recommender System",
                        style={'color': 'White',
                               'font-size': '3rem',
                               'text-shadow': '2px 2px 4px #FFFFFF'}),  # Red title with bigger font size and white shadow
                html.Div(style={'display': 'flex',
                                'justify-content': 'center'}),  # Center dropdown and button horizontally
                dcc.Dropdown(
                    id='movie-dropdown',
                    options=[{'label': movie, 'value': movie} for movie in movies['title']],
                    value=movies['title'].iloc[0],
                    style={'width': '300px',
                           'height': '30px',
                           'color': '',
                           'margin': '0 auto'}  # Align select box to the center horizontally
                ),
                html.Button('Recommend',
                            id='recommend-button',
                            style={'margin-left': '10px',
                                   'margin-top': '20px',
                                   'font-size': '1.2rem'}),  # Decrease font size
                html.Div(id='output-container-button',
                         style={'margin-top': '10px'},
                         children=[
                             html.Div(id='recommendations',
                                      style={'display': 'flex',
                                             'flex-wrap': 'wrap'})  # Wrap recommendations horizontally
                         ])
            ]
        )
    ]
)

# Callback to update recommendations
@app.callback(
    Output('recommendations', 'children'),
    [Input('recommend-button', 'n_clicks')],
    [Input('movie-dropdown', 'value')]
)
def update_output(n_clicks, selected_movie_name):
    if n_clicks is not None:
        names, posters = recommend(selected_movie_name)
        return [html.Div([
            html.Img(src=posters[i],
                     style={'width': '200px',
                            'height': '300px'}),
            html.P(names[i],
                   style={'color': 'white',
                          'text-shadow': '2px 2px 4px #FFFFFF'})  # Add white shadow to text
        ]) for i in range(len(names))]

if __name__ == '__main__':
    app.run_server(debug=True)