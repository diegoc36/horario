# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 21:29:19 2023

@author: diego
"""
import dash
from dash import dash_table, html, dcc
from datetime import datetime, timedelta
import pandas as pd

def clase_prueba(csv, NRC):
    clases = csv.loc[(csv['NRC'] == NRC) & ((csv['TIPO'] == 'CLAS') | (csv['TIPO'] == 'AYUD') | (csv['TIPO'] == 'CLSS') | (csv['TIPO'] == 'LABT')), ('TIPO', 'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES')]

    pruebas = csv.loc[ (csv['NRC'] == NRC) & ((csv['TIPO'] != 'CLAS') & (csv['TIPO'] != 'AYUD') & (csv['TIPO'] != 'CLSS')), ('TITULO', 'TIPO', 'INICIO', 'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES')]

    return clases, pruebas

def hora(horario):
    inicio = datetime.strptime('8:30', '%H:%M')  
    fin = datetime.strptime('19:20', '%H:%M')  

    horas = []
    actual = inicio
    while actual <= fin:
        horas.append(actual.time())
        if actual.minute == 30:
            actual += timedelta(minutes=60)  

    rango_horas = pd.Index(horas)

    dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
    df_horario = pd.DataFrame(index=rango_horas, columns=dias_semana)

    df_horario = df_horario.reindex(columns=rango_horas)

    df_combined = df_horario.copy()
    df_combined = df_combined.drop(df_combined.columns, axis=1)
    for dia in dias_semana:
        df_combined[dia] = None

    for dia, horas_clase in horario.items():
        for i, hora_clase in enumerate(horas_clase):
            hora = str(hora_clase[0])
            if hora != 'nan':
                duracion = datetime.strptime(hora.split('-')[1].replace(" ", ""), '%H:%M') - datetime.strptime(hora.split('-')[0].replace(" ", ""), '%H:%M')
                intervalos = int(duracion.total_seconds() / 600)  # Cálculo de los intervalos de 10 minutos
                hora_inicio = datetime.strptime(hora.split('-')[0].replace(" ", ""), '%H:%M')
                for intervalo in range(intervalos):
                    hora_actual = hora_inicio + timedelta(minutes=10 * intervalo)
                    df_combined.at[hora_actual.time(), dia] = hora_clase[1]

    df_combined = df_combined.reset_index()
    df_combined = df_combined.drop(range(11, df_combined.shape[0])).set_index('index')
    return df_combined

def obtener_opciones_curso(csv):
    cursos = csv[['NRC','TITULO','PROFESOR']].drop_duplicates(subset='NRC').values
    opciones = [{'label': '{} {} {}'.format(curso[0],curso[1],curso[2]), 'value': curso[0]} for curso in cursos]
    return opciones


def sumar_minutos(minutos_a_sumar):
    hora='00:00'
    hora_objeto = datetime.strptime(hora, '%H:%M')
    delta = timedelta(minutes=minutos_a_sumar)
    hora_sumada = hora_objeto + delta
    hora_resultante = hora_sumada.strftime('%H:%M')

    return hora_resultante


def tiene_traslapes(horario):
    # Diccionario para almacenar las horas de inicio y fin de cada día
    horas_por_dia = {}
    traslape=[]
    hora_tras=[]
    # Función para convertir una cadena de tiempo en minutos desde la medianoche
    def a_minutos(tiempo_str):
        horas, minutos = map(int, tiempo_str.split(':'))
        return horas * 60 + minutos

    # Bucle para recorrer cada día del horario
    for dia, horarios_del_dia in horario.items():
        # Lista para almacenar los horarios en minutos para este día
        horarios_minutos = []
        for hora, asignatura in horarios_del_dia:
            # Solo procesamos horarios válidos (ignoramos los valores 'nan')
            if hora and isinstance(hora, str):
                inicio, fin = hora.split('-')
                horarios_minutos.append((a_minutos(inicio.replace(" ", "")), a_minutos(fin.replace(" ", ""))))
            else:
                horarios_minutos.append((0, 0))
        
        # Comprobamos si hay traslapes en los horarios de este día
        for i in range(len(horarios_minutos)):
            for j in range(i + 1, len(horarios_minutos)):
                inicio_i, fin_i = horarios_minutos[i]
                inicio_j, fin_j = horarios_minutos[j]
                if (inicio_i < fin_j and inicio_j < fin_i):
                    minimo=sumar_minutos(max(inicio_i,inicio_j))
                    maximo=sumar_minutos(min(fin_i,fin_j))
                    traslape.append(f" El {dia} entre {horarios_del_dia[i][1]} y {horarios_del_dia[j][1]} entre {minimo} y {maximo}!")
                    hora_tras.append([dia,minimo, maximo])
                    

        # Almacenamos las horas de inicio y fin de este día
        horas_por_dia[dia] = horarios_minutos

    return hora_tras,traslape
def horario_func(csv,selected_cursos):
        horario = {
            'LUNES': [],
            'MARTES': [],
            'MIERCOLES': [],
            'JUEVES': [],
            'VIERNES': []
        }
        tod_prueba = pd.DataFrame(columns=['TITULO', 'TIPO', 'INICIO', 'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES'])
        tit_curso=[]
        for curso in selected_cursos:
            if curso==None:
                continue
            nrc = curso
            titulo = csv.loc[csv['NRC'] == nrc, 'TITULO'].drop_duplicates().values
            tit_curso.append(titulo)
            clases, pruebas = clase_prueba(csv,nrc)
            tod_prueba = pd.concat([tod_prueba, pruebas])
            for i, dia in enumerate(['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']):
                for a in clases.values.tolist():
                    if a[0] == 'AYUD':
                        horario[dia].append([a[i + 1], f'{titulo[0]}({a[0]})'])
                    elif a[0] == 'LABT':
                        horario[dia].append([a[i + 1], f'{titulo[0]}({a[0]})'])
                    else:
                        horario[dia].append([a[i + 1], titulo[0]])
        
        
        hora_tras , traslape = tiene_traslapes(horario)
        if len(hora_tras)>0:
            for i in hora_tras:
                horario[i[0]].append(['{} - {}'.format(i[1],i[2]),'TOPE'])
                
        df_combined = hora(horario)
        df_combined = df_combined.rename_axis('Horas').reset_index().fillna('')
        
        tod_prueba = tod_prueba.fillna('')
        
        return df_combined, tod_prueba, hora_tras , traslape, tit_curso
    
csv = pd.read_excel('HORARIO ING 202410.xlsx', skiprows=10, header=1)

def generate_curso_content(i):
    curso_content = html.Div([
        html.H2(f'Curso {i+1}'),
        html.Label('Nombre del Curso:'),
        dcc.Dropdown(
            id={'type': 'curso-dropdown', 'index': i},
            options=obtener_opciones_curso(csv),
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
                'backgroundColor': colores_curso[i],
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
server=app.server
_clicks=0
app.layout = html.Div([
    html.H1('Horario de la universidad'),

    html.Label('Número de Cursos:'),
    dcc.Input(id='num-cursos', type='number', min=1, max=10, step=1, value=1),
    html.Button('Actualizar', id='actualizar-button'),
    
    html.Div(id='cursos-container'),
    
    dcc.Store(id='selected-cursos-store', data=[]),
    
    html.Div(id='horario-container')
    
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
    
    df_combined, tod_prueba, hora_tras, traslape, tit_curso = horario_func(csv,selected_cursos)
    
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


if __name__ == '__main__':
    app.run_server(debug=True, port=5)
