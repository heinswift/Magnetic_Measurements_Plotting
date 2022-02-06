import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("Here comes the title")
st.write("Here comes some text.")
st.button("Click Here!")

def f(x, y):
    return np.sin(x) ** 10 + np.cos(10 + y * x) * np.cos(x)

x = np.linspace(0, 5, 900)
y = np.linspace(0, 5, 900)

X, Y = np.meshgrid(x, y)
Z = f(X, Y)

n_color_steps = st.number_input("Anzahl Farbstufen", min_value=0, max_value=100,value=10,step=1)
n_color_steps = int(n_color_steps)
fig, ax  = plt.subplots()
plt.contourf(X, Y, Z, n_color_steps-1, cmap='RdGy')
plt.colorbar()

st.pyplot(fig)