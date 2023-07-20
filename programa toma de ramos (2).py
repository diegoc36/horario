# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 02:06:47 2023

@author: diego
"""

import dash
from dash import dcc, html, dash_table
from librerias import obtener_opciones_curso,horario_func


def generate_curso_content(i):
    curso_content = html.Div([
        html.H2(f'Curso {i+1}'),
        html.Label('Nombre del Curso:'),
        dcc.Dropdown(
            id={'type': 'curso-dropdown', 'index': i},
            options=obtener_opciones_curso(),
            placeholder='Selecciona un curso',
            value=None,  # Valor inicial del dropdown
            persistence=True,  # Mantener el valor seleccionado después de actualizaciones
            persistence_type='memory'  # Tipo de persistencia en memoria
        ),

        html.Div(
            id={'type': 'horario-container', 'index': i},
            children=[],
        )
    ])
    return curso_content
    
def horario_dash(n_clicks, df_combined, hora_tras, tit_curso):
    

    colores_curso = [
'#FF5733',  # Rojo
'#33FF57',  # Verde claro
'#5733FF',  # Azul
'#FF33B7',  # Rosa
'#33B7FF',  # Azul claro
'#7F3300',  # Marrón oscuro
'#FFA500',  # Naranja
'#A52A2A',  # Marrón
'#00CED1',  # Turquesa
'#8A2BE2'   # Azul violeta
]
    columnas= df_combined.columns
    horario_div = html.Div([
        html.H3('Horario de Clases'),
        dash_table.DataTable(
            id={'type': 'horario-graph', 'index': n_clicks or 0},
            columns=[{'name': col, 'id': col} for col in columnas],
            data=df_combined.to_dict('records'),
            style_data_conditional=[

                {
                'if': {
                    'filter_query': '{{{0}}} = "{1}"'.format(col,curso[0]),
                    'column_id': col
                    },
                'backgroundColor': colores_curso[i % len(colores_curso)],
                'color': 'white'
            } for i, curso in enumerate(tit_curso) for col in columnas 
        ]+[
            {
                'if': {
                    'column_id': 'Horas',
                },
                'backgroundColor': '#CCCCCC', 
                'color': 'bold'
            },
        ]+[

            {
            'if': {
                'filter_query': '{{{0}}} = "{1}"'.format(col,'TOPE'),
                'column_id': col
                },
            'backgroundColor': 'rgb(0, 0, 0)' ,
            'color': 'white'
        } for col in columnas if len(hora_tras)
    ],
        style_header={
            'backgroundColor': 'orange',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'center'
        },
        style_table={
            'margin': {'l': 10, 'r': 10, 't': 30, 'b': 2},
            'border': '1px solid black'
        },
    ),

])
    return horario_div


app = dash.Dash(__name__)
server = app.server
df_combined, tod_prueba, hora_tras, traslape, tit_curso = horario_func([])
n_clicks=0
app.layout = html.Div([
    html.H1('Horario de la universidad'),

    html.Label('Número de Cursos:'),
    dcc.Input(id='num-cursos', type='number', min=1, max=10, step=1, value=1),
    html.Button('Actualizar', id='actualizar-button'),
    
    html.Div(generate_curso_content(0),id='cursos-container'),
    
    dcc.Store(id='selected-cursos-store', data=[]),
    
    html.Div(horario_dash(n_clicks, df_combined, hora_tras, tit_curso),id='horario-container')
    
    ])



@app.callback(
    
    [
        dash.dependencies.Output('cursos-container', 'children'),
        dash.dependencies.Output('selected-cursos-store', 'data'),
        dash.dependencies.Output('horario-container', 'children')
    ],
    [
        dash.dependencies.Input('actualizar-button', 'n_clicks'),
        dash.dependencies.Input({'type': 'curso-dropdown', 'index': dash.dependencies.ALL}, 'value')
    ],
    [
        dash.dependencies.State('num-cursos', 'value')
    ]
)
def update_cursos(n_clicks, selected_values, num_cursos):
    cursos_inputs = []
    for i in range(num_cursos):
        cursos_inputs.append(generate_curso_content(i))

    selected_cursos = selected_values[:num_cursos] if selected_values else []
    
    df_combined, tod_prueba, hora_tras, traslape, tit_curso = horario_func(selected_cursos)
    
    horario_div=horario_dash(n_clicks, df_combined, hora_tras, tit_curso)
    
  
    lista_traslape = html.Div([
        html.H3('Tiene Tope', style={'font-size': '40px', 'color': 'red'}),
        html.Ul([
            html.Li(f'{i}', style={'font-size': '30px', 'color': 'red'}) for i in traslape
            ])
    ])if len(traslape) > 0 else html.Div()
    
    lista_pruebas_div = html.Div([
        html.H3('Lista de Pruebas'),
        html.Ul([
            html.Li(f'{titulo} - {tipo} - {inicio}') for titulo, tipo, inicio, *_ in tod_prueba.values.tolist()
            ])
    ])
    horario_inicio_style = {'display': 'none'} if n_clicks == 0 else {}
    return cursos_inputs, selected_cursos, [horario_div,lista_traslape,lista_pruebas_div,horario_inicio_style]


app.run_server(debug=True, port=8888)


