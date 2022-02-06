import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Messwert Visualisierung")


# Upload excel sheet
uploaded_file = st.file_uploader("Bitte eine Messwert-Datei hochladen")

if uploaded_file is None:
    st.info('Bitte eine Messwert-Datei hochladen.')
    st.stop()

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

x_distance = parameters.loc[0]['Wert']
y_distance = parameters.loc[1]['Wert']

measurements_df = pd.read_excel(
    uploaded_file,
    sheet_name='Messwerte'
)

# Create measurement grid
n_y, n_x = measurement_schema.shape

x = np.linspace(0, n_x * x_distance, n_x)
y = np.linspace(0, n_y * y_distance, n_y)

X, Y = np.meshgrid(x, y)

# Construct Z
Z = np.zeros_like(measurement_schema)

for index, df_row in measurements_df[1:].iterrows():

    key = df_row['Messort']

    # Get position of key in measurement schema
    key_search_result = np.where(measurement_schema==key)
    row_indices = key_search_result[0]
    column_indices = key_search_result[1]

    row_index = row_indices[0]
    column_index = column_indices[0]

    Z[row_index,column_index] = df_row['Flussdichte [µT] (3D-Wert)']

with st.expander('Parameter'):
    style_options = ['Verläufe','Kacheln']
    style = st.radio('Stil', style_options, index=0)

    colormap_options = ['viridis','RdGy']
    colormap_style = st.radio('Farbpalette', colormap_options, index=0)

fig = plt.figure(figsize=(10,5),facecolor='white')
if style == style_options[0]:
    plt.contourf(X, Y, Z[::-1,:], 200, cmap=colormap_style)#, vmin=40, vmax=50)
if style == style_options[1]:
    plt.imshow(Z.astype(float),cmap=colormap_style)
plt.axis('off')
plt.colorbar()
st.pyplot(fig)