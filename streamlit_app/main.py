import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils import calculate_additional_columns
from utils import construct_Z, process_excel, metric_options_list
import matplotlib.patches as patches


# Template download
with open("Messpunktschema Vorlage.xlsx", "rb") as file:
     btn = st.sidebar.download_button(
             label="Tabellen Vorlage herunterladen",
             data=file,
             file_name="Messpunktschema Vorlage.xlsx"
             )


st.title("Messwert Visualisierung")

# Upload excel sheet
uploaded_file = st.file_uploader("Messwert-Datei hochladen.")

if uploaded_file is None:
    st.info('Bitte eine Messwert-Datei hochladen. Eine Vorlage kann aus der Sidebar links heruntergeladen werden.')
    st.stop()

measurements_df, measurement_schema, parameters = process_excel(uploaded_file)

x_distance = parameters.loc[0]['Wert']
y_distance = parameters.loc[1]['Wert']

# Create measurement grid
n_y, n_x = measurement_schema.shape

x = np.linspace(0, n_x * x_distance, n_x)
y = np.linspace(0, n_y * y_distance, n_y)

X, Y = np.meshgrid(x, y)

measurements_df = calculate_additional_columns(measurements_df)

with st.expander('Messdaten'):
    st.dataframe(measurements_df)

# Plotting Parameters
with st.expander('Einstellungen'):
    col1, col2 = st.columns(2)

    with col1:    

        metric = st.radio('Visualisierte Größe', options=metric_options_list, index=0)
    
    with col2:
        style_options = ['Verläufe','Kacheln']
        style = st.radio('Stil', style_options, index=0)

        colormap_options = ['viridis','RdGy']
        colormap_style = st.radio('Farbpalette', colormap_options, index=0)

        show_max_difference = st.checkbox('Zeige maximalen Abstand zwischen zwei Werten')
        if show_max_difference:
            rectangle_color = st.color_picker('Rechteckfarbe', value='#E03A1D')

# Construct Z
Z = construct_Z(measurements_df, measurement_schema, metric)



# Plotting
fig = plt.figure(figsize=(10,5),facecolor='white',dpi=300)
ax = fig.gca()
if style == style_options[0]:
    #plt.contourf(X, Y, Z[::-1,:], 200, cmap=colormap_style)#, vmin=40, vmax=50)
    plt.imshow(Z.astype(float),cmap=colormap_style, interpolation='spline36')
if style == style_options[1]:
    plt.imshow(Z.astype(float),cmap=colormap_style)
# Add the patch to the Axes
# Show maximum
if show_max_difference:
    Z_gradient = np.gradient(Z)
    
    x_diff = np.abs(np.diff(Z, axis=1)) # horizontal
    y_diff = np.abs(np.diff(Z, axis=0)) # vertikal

    max_x_diff = np.max(x_diff)
    max_y_diff = np.max(y_diff)

    max_x_diff_index = np.unravel_index(x_diff.argmax(),x_diff.shape)
    max_y_diff_index = np.unravel_index(y_diff.argmax(),y_diff.shape)

    x_is_larger_than_y = max_x_diff > max_y_diff
    max_diff = max_x_diff if x_is_larger_than_y else max_y_diff
    max_diff_index = max_x_diff_index if x_is_larger_than_y else max_y_diff_index

    rect_y, rect_x = max_diff_index

    if x_is_larger_than_y:
        rect = patches.Rectangle((rect_x-0.5, rect_y-0.5), 2, 1, linewidth=2, edgecolor=rectangle_color, facecolor='none')
    else:
        rect = patches.Rectangle((rect_x-0.5, rect_y-0.5), 1, 2, linewidth=2, edgecolor=rectangle_color, facecolor='none')

    
    ax.add_patch(rect)

plt.setp(ax.get_xticklabels(), visible=False)
plt.setp(ax.get_yticklabels(), visible=False)
ax.tick_params(axis='both', which='both', length=0)
#plt.ylabel('Kopfende')
plt.colorbar()
plt.tight_layout()
st.pyplot(fig)

if show_max_difference:
    st.metric('Maximale Differenz', value=np.round(max_diff,2))