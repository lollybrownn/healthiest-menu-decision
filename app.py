import streamlit as st
import numpy as np 
import pandas as pd
import matplotlib as plt
from PIL import Image

icon = Image.open("meki_d_teach.png")

st.set_page_config(
    page_title="MEK D TEACH", 
    page_icon=icon,
    layout="wide", 
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown("Hello")
