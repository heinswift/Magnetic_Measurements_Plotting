from  matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import streamlit as st

# Custom colormap
c = ["darkred","red","lightcoral","white", "palegreen","green","darkgreen"]
v = [0,.15,.4,.5,0.6,.9,1.]
l = list(zip(v,c))
cmap=LinearSegmentedColormap.from_list('rg',l, N=256)

metric_options_dict = {
        'Flussdichte 3D': 'Flussdichte [µT] (3D-Wert)',
        'Flussdichte X': 'Flussdichte [µT] (X-Wert)',
        'Flussdichte Y': 'Flussdichte [µT] (Y-Wert)',
        'Flussdichte Z': 'Flussdichte [µT] (Z-Wert)',
        '3D-Abweichung': '3D-Abweichung',
        'XYZ-Abweichung': 'XYZ-Abweichung',
        'Absolute Kompassnadelabweichung': 'Absolute Kompassnadelabweichung'
}

metric_options_list = [s for s in metric_options_dict]

def process_excel(uploaded_file):
    # Read measurement schema
    measurement_schema = pd.read_excel(
        uploaded_file,
        sheet_name='Messpunktschema',
        header=None
    )
    measurement_schema = np.array(measurement_schema)

    # Read parameters
    parameters = pd.read_excel(
        uploaded_file,
        sheet_name='Parameter'
    )

    measurements_df = pd.read_excel(
        uploaded_file,
        sheet_name='Messwerte'
    )

    return measurements_df, measurement_schema, parameters

def calculate_additional_columns(measurements_df):
    neutral_row = measurements_df.loc[0]
    neutral_3D = neutral_row['Flussdichte [µT] (3D-Wert)']
    neutral_X = neutral_row['Flussdichte [µT] (X-Wert)']
    neutral_Y = neutral_row['Flussdichte [µT] (Y-Wert)']
    neutral_Z = neutral_row['Flussdichte [µT] (Z-Wert)']
    neutral_vec = np.array([neutral_X, neutral_Y, neutral_Z])
    compass_neutral = neutral_row['Kompassnadelabweichung [°]']
    measurements_df['3D-Abweichung'] = measurements_df['Flussdichte [µT] (3D-Wert)'] - neutral_3D

    vec = np.array(measurements_df[[
        'Flussdichte [µT] (X-Wert)', 
        'Flussdichte [µT] (Y-Wert)', 
        'Flussdichte [µT] (Z-Wert)'
        ]])
    measurements_df['XYZ-Abweichung'] = np.linalg.norm(vec-neutral_vec, axis=1)

    compass_deviations = measurements_df['Kompassnadelabweichung [°]']
    compass_deviations = compass_deviations - compass_neutral
    measurements_df['Absolute Kompassnadelabweichung'] = np.min([np.abs(compass_deviations),np.abs(compass_deviations-360)], axis=0)

    return measurements_df

def construct_Z(measurements_df, measurement_schema, metric):


    Z = np.zeros_like(measurement_schema)

    for _, df_row in measurements_df[1:].iterrows():

        key = df_row['Messort']

        # Get position of key in measurement schema
        key_search_result = np.where(measurement_schema==key)
        row_indices = key_search_result[0]
        column_indices = key_search_result[1]

        row_index = row_indices[0]
        column_index = column_indices[0]

        z_value = df_row[metric_options_dict[metric]]

        Z[row_index,column_index] = z_value
    
    return Z