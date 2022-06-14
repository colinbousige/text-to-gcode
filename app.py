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

st.title("Simple G-Code creator for text writing")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 400px;
        margin-left: -400px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def plot_text(x, y, plotarea=st, figx=6, figy=3, 
              XMIN=0, XMAX=100, YMIN=0, YMAX=100, zoom=0):
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
    ax1.plot([XMIN, XMAX, XMAX, XMIN, XMIN],
             [YMIN, YMIN, YMAX, YMAX, YMIN], c='black', linewidth=3, zorder=1)
    ax1.axis('off')
    if zoom:
        ax1.set_xlim(min(x), max(x))
        ax1.set_ylim(min(y), max(y))
    else:
        ax1.set_xlim(XMIN, XMAX)
        ax1.set_ylim(YMIN, YMAX)
    ax1.set_aspect('equal', 'datalim')
    plotarea.pyplot(f)


def get_gcode(x, y, g, c):
    lines = [f"{gg}  X{xx:.5f}  Y{yy:.5f}  {cc}" for (gg, xx, yy, cc) in zip(
        g, x, y, c)]
    return("\n".join(lines))

bt, plotarea = st.columns([1, 4])

data = st.sidebar.text_area("Enter your text here:", "Sample text")
col1, col2 = st.sidebar.columns(2)
line_length = col1.number_input("Line Length:", value=100., min_value=0., max_value=1000.)
height = col2.number_input("Line Height:", value=10., min_value=0., max_value=1000.)
padding = col1.number_input("Padding:", value=3., key="pad")
baseline = col2.number_input("Baseline:", value=0., min_value=-10., max_value=10., key="base")
factor = col1.number_input("Font size factor:", value=4.0, min_value=0.0, key="factor")
N = col2.number_input("Number of layer per letter:", value=11, min_value=1, key="N")
shiftX = col1.number_input("Shift X:", value=0.0, key="shiftx")
shiftY = col2.number_input("Shift Y:", value=0.0, key="shifty")

st.sidebar.title("Definition of printing area:")
col1, col2 = st.sidebar.columns(2)
XMIN = col1.number_input("X min:", value=50., step=1., key="lines_XMIN")
XMAX = col2.number_input("X max:", value=350., step=1., key="lines_XMAX")
YMIN = col1.number_input("Y min:", value=50., step=1., key="lines_YMIN")
YMAX = col2.number_input("Y max:", value=350., step=1., key="lines_YMAX")

gcode = textToGcode(letters, data, line_length, height, padding, N, baseline)

figx = bt.number_input("Figure size (x)", value=6)
figy = bt.number_input("Figure size (y)", value=3)

gs = gcode.split("\n")[:-1]
g,x,y,c = [],[],[],[]
for i in range(len(gs)):
    if (len(gs[i].split(" "))==4):
        gg, xx, yy, cc = gs[i].split(" ")
        g.append(gg)
        x.append(float(xx.replace("X", "")))
        y.append(float(yy.replace("Y", "")))
        c.append(cc)

x = np.array(x)*factor
x = x+(XMIN+XMAX)/2 - (max(x)+min(x))/2 + shiftX
y = np.array(y)*factor
y = y+(YMIN+YMAX)/2 - (max(y)+min(y))/2 + shiftY
g = np.array(g)
c = np.array(c)

if 'zoom' not in st.session_state:
    st.session_state.zoom = 0
if bt.button("Zoom in/out", key="lines_zoom"):
    st.session_state.zoom = (st.session_state.zoom + 1) % 2

plot_text(x, y, plotarea, figx, figy, XMIN, XMAX,
          YMIN, YMAX, st.session_state.zoom)

bt.download_button("Download GCODE",
                           data = get_gcode(x, y, g, c),
                           file_name='GCODE.txt',
                           mime='text/csv')
