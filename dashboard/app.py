import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import plotly.express as px
from pandas.core.common import flatten
import json
import requests

#url = 'http://127.0.0.1:5000/predict_api' # URL en local
url = 'https://apiflaskoc.herokuapp.com/predict_api'
Path = './output/'
df = pd.read_csv(Path+'df_csv_export.csv', sep=',')
df_knn = pd.read_csv(Path+'df_knn_export.csv', sep=',')
df_job = pd.read_csv(Path+'df_job.csv', sep=',')
data_test = pd.read_csv(Path+'data_test.csv', sep=',')

test_sk_id = data_test['SK_ID_CURR'].tolist()

available_indicators = list(df.columns)

valid_threshold = 0.085 # crédit accordé si score en dessous de ce seuil

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
	# Case pour rentrer l'ID + bouton pour rafraichir
    html.Div(["SK_ID_CURR: ", dcc.Input(id='my-input-ID',value=100001)],
    style={'width': '15%', 'display': 'inline-block'}),
    html.Div([html.Button(id='submit-button-state', n_clicks=0, children='Rafraichir')],
    style={'width': '15%', 'display': 'inline-block'}),
    html.Div(id='API_result',
    style={'width': '10%', 'display': 'inline-block','backgroundColor': '#E6E6FA','textAlign': 'center'},
    ),

    html.H5(
      children='Comparaison avec les plus proches voisins',
      style={
        'textAlign': 'center',
      }
    ), 
    # Table avec plus proche voisin
    html.Div(id='filtered_table'),

    html.Div([
    	html.Div([
    		# Graphique plus proche voisin
    		dcc.Graph(id='graph_knn'),
			  # Choix des indicateurs sur les axes.
    		html.Div([
    			html.Div([
    				dcc.Dropdown(
              		id='xaxis-column',
              		options=[{'label': i, 'value': i} for i in available_indicators],
              		value='Revenu'
            		)
    			], style={'width': '48%', 'display': 'inline-block'}),
    			html.Div([
    				dcc.Dropdown(
              		id='yaxis-column',
              		options=[{'label': i, 'value': i} for i in available_indicators],
              		value='Age'
            		)
    			], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    		]),
    	], style={'width': '48%', 'display': 'inline-block'}),

    	html.Div([
     		# Graphique comparatif job
    		dcc.Graph(id='graph_job'),
    		dcc.Dropdown(
          	id='feature_id',
          	options=[{'label': i, 'value': i} for i in available_indicators],
          	value='Revenu'
        	)
    	], style={'width': '48%', 'display': 'inline-block'}),
    ])
])

@app.callback(
	Output('graph_job','figure'),
	[Input('submit-button-state', 'n_clicks')],
	[State('my-input-ID', 'value'),
    State('feature_id', 'value')]
)

def update_fig2(n_clicks, selected_applicant, feature_id):
   print(selected_applicant)
   job = df_job[df_job['SK_ID_CURR'] == int(selected_applicant)]['OCCUPATION_TYPE'].tolist()
   jobstr = ''.join(job)
   job_list_id = df_job[df_job['OCCUPATION_TYPE'] == jobstr]['SK_ID_CURR'].tolist()
   feat_mean = df[df['SK_ID_CURR'].isin(job_list_id)][feature_id].mean()
   feat_id_value = df[df['SK_ID_CURR'] == int(selected_applicant)][feature_id].values[0]
   df_feat_mean = pd.DataFrame({'VS':['Customer', jobstr],
   								'Valeur feature':[feat_id_value,feat_mean]
   								})

   fig2 = px.bar(df_feat_mean, x='VS', y='Valeur feature')

   fig2.update_layout(
    title={
        'text': 'Comparaison avec catégorie professionnelle',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'bottom'},
    transition_duration=500)
   return fig2

@app.callback(
	Output(component_id='filtered_table', component_property='children'),
	Output('graph_knn','figure'),
  	Output('API_result','children'),
  	[Input('submit-button-state', 'n_clicks')],
  	[State('my-input-ID', 'value'),
  	State('xaxis-column', 'value'),
  	State('yaxis-column', 'value')]
)

def update_df_fig(n_clicks, selected_applicant, xaxis_column_name, yaxis_column_name):
   # On filtre nos donnée avec les plus proches voisins de notre client.
   list_app = [selected_applicant]
   knn_filter = df_knn[df_knn['SK_ID_CURR'] == int(selected_applicant) ]
   # liste des plus proches voisins
   list_app.extend(list(flatten(knn_filter.values.tolist()))[:10])
   #Filtre uniqument le client demandé et les données d'entrainement
   target_filter = (df['SK_ID_CURR'] == int(selected_applicant)) | (df['TARGET'] == 0) | (df['TARGET'] == 1)
   filtered_dfr = df[(df['SK_ID_CURR'].isin(list_app)) & (target_filter)]

   if int(selected_applicant) in test_sk_id:
      # Sélection des données du client demandé et mise en forme sous dict puis Appel API modèle entraîné :
      test_param = data_test[data_test['SK_ID_CURR'] == int(selected_applicant)]
      test_param.drop(['SK_ID_CURR'], axis=1, inplace=True)
      test_param_d = test_param.to_dict('records')[0]
      response = requests.post(url, json=test_param_d)
      API_score = response.json()
      print(API_score)  
      if API_score <= valid_threshold:
          API_status = "Crédit accordé"
      else:
          API_status = "Crédit refusé"
      ID_index = filtered_dfr[filtered_dfr['SK_ID_CURR'] == int(selected_applicant)].index.values
      filtered_dfr.loc[ID_index,'TARGET'] = API_score
   else:
      API_status = "Le client fait partie de la base de donnéé d'entrainement"

   fig = px.scatter(filtered_dfr, x=xaxis_column_name, y=yaxis_column_name,
                 size="Annuite", color="TARGET", hover_name="SK_ID_CURR",
                 size_max=40)
   fig.update_layout(
    title={
        'text': 'Comparaison avec les plus proches voisins',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'bottom'},
    transition_duration=500)

   return dash_table.DataTable(
    data=filtered_dfr.to_dict('records'),
    columns=[{'id': 'SK_ID_CURR', 'name': 'SK_ID_CURR', 'type': 'numeric','format': Format(precision=0,scheme=Scheme.fixed,
            decimal_delimiter='.')}]+[{'id': c, 'name': c, 'type': 'numeric','format': Format(precision=3,scheme=Scheme.fixed,
            decimal_delimiter='.')} for c in filtered_dfr.columns if c != 'SK_ID_CURR'],
    style_table={'overflowX': 'auto'},
    style_cell={
        'textAlign': 'center',
        'font_family': 'sans-serif',
        'font_size': 12,
    },
    style_header={
        'height' : 'auto'
    },
    style_data_conditional=[
        {
            'if': {
                'filter_query': '{{SK_ID_CURR}} = {} && {{TARGET}} > {}'.format(selected_applicant,valid_threshold)
            },
            'backgroundColor': '#DC143C',
            'color': 'white'
        },
        {
            'if': {
                'filter_query': '{{SK_ID_CURR}} = {} && {{TARGET}} <= {}'.format(selected_applicant,valid_threshold)
            },
            'backgroundColor': '#2E8B57',
            'color': 'white'
        }
    ]

  ), fig, API_status

if __name__ == '__main__':
    app.run_server(debug=True)
