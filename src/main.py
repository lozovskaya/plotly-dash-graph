import requests
import plotly.graph_objs as go
import pandas as pd
import dash
from dash import dcc, html

def get_repository_data():
    url = 'https://api.github.com/search/repositories?q=stars:>0'
    response = requests.get(url)
    data = response.json()
    return data['items']


app = dash.Dash(__name__)

all_languages = list(set([repo['language'] for repo in get_repository_data() if repo['language'] is not None]))
languages_options = [{'label': str(language), 'value': language} for language in all_languages]

app.layout = html.Div([
    html.H1("The amount of github stars & forks depending on the programming languages"),
    html.Label('Programming language:'),
    dcc.Dropdown(
        id='language-dropdown',
        options=languages_options,
        value=all_languages,
        multi=True
    ),
    dcc.Graph(
        id='star-fork-distribution'
    )
])

@app.callback(
    dash.dependencies.Output('star-fork-distribution', 'figure'),
    [dash.dependencies.Input('language-dropdown', 'value')]
)
def update_graph(selected_languages):
    repositories = get_repository_data()
    repo_df = pd.DataFrame({
        'Language': [repo['language'] for repo in repositories if repo['language'] in selected_languages and repo['language'] is not None],
        'Stars': [repo['stargazers_count'] for repo in repositories if repo['language'] in selected_languages and repo['language'] is not None],
        'Forks': [repo['forks_count'] for repo in repositories if repo['language'] in selected_languages and repo['language'] is not None]
    })
    grouped_df = repo_df.groupby('Language').sum().reset_index()

    return {
        'data': [
            go.Bar(
                x=grouped_df['Language'],
                y=grouped_df['Stars'],
                name='Stars'
            ),
            go.Bar(
                x=grouped_df['Language'],
                y=grouped_df['Forks'],
                name='Forks'
            )
        ],
        'layout': {
            'title': "The amount of github stars & forks depending on the programming languages",
            'barmode': 'group'
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)
