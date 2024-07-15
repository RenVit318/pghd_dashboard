import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta

import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from datetime import date

from rdflib import Namespace
from rdflib.namespace import XSD, RDFS
from rdflib.plugins.sparql import prepareQuery


def process_simple_query(graph, query_string):
    ti = Namespace("https://github.com/RenVit318/financial_dashboard/blob/main/code/vocab/transaction_info.ttl#")
    query = prepareQuery(query_string, initNs={"ti": ti, "xsd": XSD})
    res = graph.query(query)

    return res

    
def plot_bp(g, plot_attrs):
    query_str = f"""
        PREFIX pghdc: <https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/>
        PREFIX bp_aux: <https://github.com/RenVit318/pghd/tree/main/src/vocab/auxillary_info/>
        PREFIX smash: <http://aimlab.cs.uoregon.edu/smash/ontologies/biomarker.owl#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?pulse ?sys_bp ?dia_bp ?date ?loc ?person ?pos
        WHERE {{
            ?y pghdc:patient ?x ;
               pghdc:collected_PGHD ?z . 
            ?x pghdc:patientID '{plot_attrs['patient']}'^^xsd:int .
            ?z smash:hasSystolicBloodPressureValue ?sys_bp ;
               smash:hasDiastolicBloodPressureValue ?dia_bp ;
               smash:hasPulseRate ?pulse ;
               bp_aux:CollectionLocation ?loc_uri ;
               bp_aux:CollectionPerson ?person_uri ;
               bp_aux:CollectionPosition ?pos_uri ;
               dc:date ?date .

            ?loc_uri    rdfs:label ?loc .
            ?person_uri rdfs:label ?person .
            ?pos_uri    rdfs:label ?pos .
        }}
    """

    pghdc = Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/")
    smash = Namespace("http://aimlab.cs.uoregon.edu/smash/ontologies/biomarker.owl#")
    dc    = Namespace("http://purl.org/dc/elements/1.1/")
    bp_aux= Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/auxillary_info/")
    query = prepareQuery(query_str, initNs={"pghdc": pghdc, "bp_aux": bp_aux, "smash": smash, "dc": dc, "xsd": XSD, "rdfs": RDFS})
    res = g.query(query)

    N = len(res)
    data = pd.DataFrame({
        'date'  : np.zeros(N, dtype=object),
        'pulse' : np.zeros(N, dtype=float),
        'sys_bp': np.zeros(N, dtype=float),
        'dia_bp': np.zeros(N, dtype=float),
        'loc'   : np.zeros(N, dtype=str),
        'person': np.zeros(N, dtype=str),
        'pos'   : np.zeros(N, dtype=str),
    })

    for i, row in enumerate(res):
        data.loc[i, 'date']   = date.fromisoformat(row.date)
        data.loc[i, 'pulse']  = float(row.pulse)
        data.loc[i, 'sys_bp'] = float(row.sys_bp)
        data.loc[i, 'dia_bp'] = float(row.dia_bp)
        data.loc[i, 'loc']    = row.loc
        data.loc[i, 'person'] = row.person
        data.loc[i, 'pos']    = row.pos

    data = data.sort_values(by='date')

    #unique_dates, idxs = np.unique(data['date'], return_index=True)
    #min_date = np.min(unique_dates)
    #max_date = np.max(unique_dates)
    #delta = timedelta(days=1)
    #start_state = (np.max((min_date, max_date - 2 * delta)), max_date)

    #daterange = st.slider(label='Select date range', min_value=min_date, max_value=max_date,
    #                      value=start_state)

    # Plotting
    ydata = []
    if plot_attrs['pulse']:
        ydata.append('pulse')
    if plot_attrs['sys_bp']:
        ydata.append('sys_bp')
    if plot_attrs['dia_bp']:
        ydata.append('dia_bp')

    if len(ydata) > 0:
        fig = px.line(data, x='date', y=ydata, custom_data=['loc', 'person', 'pos'], 
                      title=f"IVR Blood Pressure Monitor Data", 
                      markers=True)

        fig.update_traces(
            hovertemplate="<br>".join([
                "Date: %{x}",
                "Val:  %{y}",
                "Location: %{customdata[0]}",
                "Person:   %{customdata[1]}",
                "Position: %{customdata[2]}",
            ])
        )

        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Pule / Blood Pressure")

        st.plotly_chart(fig)



    # Show the data in a table
    #show_data = st.checkbox("Click here to view the data")
    #if show_data: 
    #    #df = pd.DataFrame(data)
    #    st.dataframe(data, 
    #                 use_container_width=True, hide_index=True,
    #                 column_config={
    #                    "date": "Date",
    #                    "pulse": "Pulse Rate",
    #                    "sys_bp": "Systolic BP",
    #                    "dia_bp": "Diastolic BP",
    #                    "loc": "Location",
    #                    "person": "Person",
    #                    "pos": "Position"
    #                 })


def plot_fitbit_heartrate(g, plot_attrs):
    query_str = f"""
        PREFIX pghdc: <https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/>
        PREFIX fitbit: <https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?date ?heartrate
        WHERE {{
            ?y pghdc:patient ?x ;
               pghdc:collected_PGHD ?z . 
            ?x pghdc:patientID '{plot_attrs['patient']}'^^xsd:int .
            ?z fitbit:resting_heart_rate ?heartrate ;
               dc:date ?date .
        }}
    """

    pghdc = Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/")
    fitbit= Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/")
    dc    = Namespace("http://purl.org/dc/elements/1.1/")
    
    query = prepareQuery(query_str, initNs={"pghdc": pghdc, "fitbit": fitbit, "dc": dc, "xsd": XSD})
    res = g.query(query)

    N = len(res)
    data = pd.DataFrame({
        'date'  : np.zeros(N, dtype=object),
        'heartrate' : np.zeros(N, dtype=float)
    })

    for i, row in enumerate(res):
        data.loc[i, 'date']   = date.fromisoformat(row.date)
        try:
            data.loc[i, 'heartrate']  = float(row.heartrate) # Is set to None if no value present
        except:
            data.loc[i, 'heartrate'] = np.nan

    data = data.sort_values(by='date')

    # Plotting
    fig = px.line(data, x='date', y='heartrate', 
                    title="Fitbit - Heartrate", markers=True)
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Resting Heart Rate")

    st.plotly_chart(fig)


def plot_fitbit_steps(g, plot_attrs):
    query_str = f"""
        PREFIX pghdc: <https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/>
        PREFIX fitbit: <https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?date ?steps
        WHERE {{
            ?y pghdc:patient ?x ;
               pghdc:collected_PGHD ?z . 
            ?x pghdc:patientID '{plot_attrs['patient']}'^^xsd:int .
            ?z fitbit:steps ?steps;
               dc:date ?date .
        }}
    """

    pghdc = Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/")
    fitbit= Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/")
    dc    = Namespace("http://purl.org/dc/elements/1.1/")
    
    query = prepareQuery(query_str, initNs={"pghdc": pghdc, "fitbit": fitbit, "dc": dc, "xsd": XSD})
    res = g.query(query)

    N = len(res)
    data = pd.DataFrame({
        'date'  : np.zeros(N, dtype=object),
        'steps' : np.zeros(N, dtype=float)
    })

    for i, row in enumerate(res):
        data.loc[i, 'date']   = date.fromisoformat(row.date)
        data.loc[i, 'steps']  = float(row.steps)

    data = data.sort_values(by='date')

    # Plotting
    fig = px.line(data, x='date', y='steps', 
                    title="Fitbit - Steps", markers=True)
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Step Count")

    st.plotly_chart(fig)


def plot_fitbit_activity(g, plot_attrs):
    query_str = f"""
        PREFIX pghdc: <https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/>
        PREFIX fitbit: <https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?date ?sedentary ?light ?fairly ?very
        WHERE {{
            ?y pghdc:patient ?x ;
               pghdc:collected_PGHD ?z . 
            ?x pghdc:patientID '{plot_attrs['patient']}'^^xsd:int .
            ?z fitbit:lightly_active_minutes ?light ;
               fitbit:sedentary_minutes ?sedentary;
               fitbit:fairly_active_minutes ?fairly;
               fitbit:very_active_minutes ?very;
               dc:date ?date .
        }}
    """
    
    pghdc = Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/")
    fitbit= Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/")
    dc    = Namespace("http://purl.org/dc/elements/1.1/")
    
    query = prepareQuery(query_str, initNs={"pghdc": pghdc, "fitbit": fitbit, "dc": dc, "xsd": XSD})
    res = g.query(query)

    N = len(res)
    data = pd.DataFrame({
        'date'   : np.zeros(N, dtype=object),
        'sedentary' : np.zeros(N, dtype=float),
        'light'  : np.zeros(N, dtype=float),
        'fairly' : np.zeros(N, dtype=float),
        'very'   : np.zeros(N, dtype=float),
    })

    for i, row in enumerate(res):
        data.loc[i, 'date']   = date.fromisoformat(row.date)
        data.loc[i, 'sedentary']  = float(row.sedentary)
        data.loc[i, 'light']  = float(row.light)
        data.loc[i, 'fairly']  = float(row.fairly)
        data.loc[i, 'very']  = float(row.very)

    data = data.sort_values(by='date')

    # Plotting
    ydata = ['sedentary', 'light', 'fairly', 'very']
    fig = px.line(data, x='date', y=ydata, 
                  labels={'sedentary': 'Sedentary', 'light': 'Light', 'fairly':'Fairly', 'very':'Very'},
                  title="Fitbit - Activity", markers=True)
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Time spent (Minutes)")

    st.plotly_chart(fig)

def plot_fitbit_sleep(g, plot_attrs):
    query_str = f"""
        PREFIX pghdc: <https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/>
        PREFIX fitbit: <https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?date ?efficiency ?duration
        WHERE {{
            ?y pghdc:patient ?x ;
               pghdc:collected_PGHD ?z . 
            ?x pghdc:patientID '{plot_attrs['patient']}'^^xsd:int .
            ?z fitbit:sleep_efficiency ?efficiency ;
               fitbit:sleep_duration ?duration ;
               dc:date ?date .
        }}
    """

    pghdc = Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/pghd_connect/")
    fitbit= Namespace("https://github.com/RenVit318/pghd/tree/main/src/vocab/fitbit/")
    dc    = Namespace("http://purl.org/dc/elements/1.1/")
    
    query = prepareQuery(query_str, initNs={"pghdc": pghdc, "fitbit": fitbit, "dc": dc, "xsd": XSD})
    res = g.query(query)

    N = len(res)
    data = pd.DataFrame({
        'date'  : np.zeros(N, dtype=object),
        'efficiency' : np.zeros(N, dtype=float),
        'duration' : np.zeros(N, dtype=float) 
    })

    for i, row in enumerate(res):
        data.loc[i, 'date']   = date.fromisoformat(row.date)
        try:
            data.loc[i, 'efficiency']  = float(row.efficiency)
        except:
            data.loc[i, 'efficiency'] = np.nan
        try:
            data.loc[i, 'duration'] = float(row.duration)
        except:
            data.loc[i, 'duration'] = np.nan

    data = data.sort_values(by='date')

    # Plotting
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=data['date'], y=data['efficiency'], 
                             name='Sleep Efficiency'),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=data['date'], y=data['duration'], 
                             name='Sleep Duration'),
                  secondary_y=True)

    
    fig.update_layout(title_text="Fitbit - Sleep Data")
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Sleep Efficiency", secondary_y=False)
    fig.update_yaxes(title_text="Sleep Duration (ms)", secondary_y=True)
    #fig.update_yaxes(title_text="Resting Heart Rate")

    st.plotly_chart(fig)

