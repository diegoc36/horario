# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 09:37:19 2023

@author: diego
"""

from datetime import datetime, timedelta
import pandas as pd

def clase_prueba( NRC):
    clases = csv.loc[(csv['NRC'] == NRC) & ((csv['TIPO'] == 'CLAS') | (csv['TIPO'] == 'AYUD') | (csv['TIPO'] == 'CLSS')), ('TIPO', 'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES')]

    pruebas = csv.loc[ (csv['NRC'] == NRC) & ((csv['TIPO'] != 'CLAS') & (csv['TIPO'] != 'AYUD') & (csv['TIPO'] != 'CLSS')), ('TITULO', 'TIPO', 'INICIO', 'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES')]

    return clases, pruebas

def hora(horario):
    inicio = datetime.strptime('8:30', '%H:%M')  # Hora inicial
    fin = datetime.strptime('19:20', '%H:%M')  # Hora final

    horas = []
    actual = inicio
    while actual <= fin:
        horas.append(actual.time())
        if actual.minute == 30:
            actual += timedelta(minutes=60)  # Incremento de 50 minutos

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
                duracion = datetime.strptime(hora.split(' - ')[1], '%H:%M') - datetime.strptime(hora.split(' - ')[0], '%H:%M')
                intervalos = int(duracion.total_seconds() / 600)  # Cálculo de los intervalos de 10 minutos
                hora_inicio = datetime.strptime(hora.split(' - ')[0], '%H:%M')
                for intervalo in range(intervalos):
                    hora_actual = hora_inicio + timedelta(minutes=10 * intervalo)
                    df_combined.at[hora_actual.time(), dia] = hora_clase[1]

    df_combined = df_combined.reset_index()
    df_combined = df_combined.drop(range(11, df_combined.shape[0])).set_index('index')
    return df_combined

def obtener_opciones_curso():
    cursos = csv[['NRC','TITULO','PROFESOR','PLAN DE ESTUDIOS']].drop_duplicates(subset='NRC').values
    opciones = [{'label': '{} {} {} {} '.format(curso[0],curso[1],curso[2],curso[3]), 'value': curso[0]} for curso in cursos]
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
                inicio, fin = hora.split(' - ')
                horarios_minutos.append((a_minutos(inicio), a_minutos(fin)))
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
def horario_func(selected_cursos):
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
            clases, pruebas = clase_prueba(nrc)
            tod_prueba = pd.concat([tod_prueba, pruebas])
            for i, dia in enumerate(['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']):
                for a in clases.values.tolist():
                    if a[0] == 'AYUD':
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
    
csv = pd.read_excel('Horario ING_202320.xlsx', skiprows=10, header=1)