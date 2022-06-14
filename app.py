import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from ressources.text_to_gcode import *
letters = readLetters("./ressources/ascii_gcode/")

st.set_page_config(
    page_title="Simple G-Code creator for text writing",
    page_icon=":hammer_and_pick:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://lmi.cnrs.fr/author/colin-bousige/',
        'Report a bug': "https://lmi.cnrs.fr/author/colin-bousige/",
        'About': """
            ### Simple G-Code creator for text writing
            Version date 2022-06-14.

            This app GUI was made by [Colin Bousige](mailto:colin.bousige@cnrs.fr). 
            The text to GCODE code comes from: https://github.com/Stypox/text-to-gcode
            Contact me for support or to signal a bug.
            """
    }
)

def plot_text(x, y, plotarea, figx=6, figy=3):
    """
    Plots the text with color ranging from green to red for the printing order
    """
    cmap = cm.RdYlGn_r
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(0.0, 1.0)
    z = np.asarray(np.linspace(0.0, 1.0, len(x)))
    lc = LineCollection(segments, array=z, cmap=cmap,
                        norm=norm, linewidth=1.5, alpha=.8)
    f = Figure(figsize=(figx, figy), dpi=150)
    f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax1 = f.add_subplot(1, 1, 1)
    ax1.add_collection(lc)
    ax1.axis('off')
    ax1.set_xlim(min(x)-5, max(x)+5)
    ax1.set_ylim(min(y), max(y))
    ax1.set_aspect('equal', 'datalim')
    plotarea.pyplot(f)

data = st.sidebar.text_area("Enter your text here:", "Sample text", height=200)
line_length = st.sidebar.slider("Line Length", value=100, min_value=0, max_value=1000)
height = st.sidebar.slider("Line Height", value=10, min_value=0, max_value=1000)
padding = st.sidebar.slider("Padding", value=3, min_value=-100, max_value=100)
gcode = textToGcode(letters, data, line_length, height, padding)
left, right = st.sidebar.columns(2)
figx = left.number_input("Figure size (x)", value=6)
figy = right.number_input("Figure size (y)", value=3)


gs = gcode.split("\n")
g,x,y = [],[],[]
for i in range(len(gs)):
    if len(gs[i].split(" "))==3:
        gg, xx, yy = gs[i].split(" ")
        x.append(float(xx.replace("X", "")))
        y.append(float(yy.replace("Y", "")))

plot_text(x, y, st, figx, figy)

st.sidebar.download_button("Download GCODE",
                           data = gcode,
                           file_name='GCODE.nc',
                           mime='text/csv')
