import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPK WP — Menu Sehat McDonald's India",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.main { background-color: #f7f8fa; }

/* Header */
.hero-header {
    background: linear-gradient(135deg, #da291c 0%, #ff6b35 60%, #ffc72c 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(218,41,28,0.25);
}
.hero-header h1 { font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.hero-header p  { font-size: 1rem; margin: 0.4rem 0 0; opacity: 0.9; }

/* Metric Cards */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-left: 4px solid #da291c;
    margin-bottom: 1rem;
}
.metric-card .label { font-size: 0.78rem; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value { font-size: 1.6rem; font-weight: 800; color: #1a1a2e; }

/* Step boxes */
.step-box {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.step-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #da291c;
    font-weight: 700;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

/* Winner card */
.winner-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 16px;
    padding: 2rem;
    color: white;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.winner-card .rank1 { font-size: 3rem; }
.winner-card h2 { font-size: 1.6rem; font-weight: 800; margin: 0.5rem 0 0.3rem; }
.winner-card .score-badge {
    display: inline-block;
    background: #ffc72c;
    color: #1a1a2e;
    font-weight: 800;
    font-size: 1.1rem;
    border-radius: 50px;
    padding: 0.3rem 1.2rem;
    margin: 0.5rem 0;
    font-family: 'Space Mono', monospace;
}

/* Sidebar */
section[data-testid="stSidebar"] { background: #1a1a2e !important; }
section[data-testid="stSidebar"] * { color: #e8e8f0 !important; }
section[data-testid="stSidebar"] .stSlider > div { color: white !important; }

/* Dataframe tweaks */
.dataframe-container { border-radius: 10px; overflow: hidden; }

/* Tab styling */
button[data-baseweb="tab"] { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("IndiaMcDs_Menu.csv")
    df.columns = df.columns.str.strip()
    # Kolom numerik
    num_cols = ['Energy (kCal)', 'Protein (g)', 'Total fat (g)', 'Sat Fat (g)',
                'Trans fat (g)', 'Cholesterols (mg)', 'Total carbohydrate (g)',
                'Total Sugars (g)', 'Added Sugars (g)', 'Sodium (mg)']
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df.dropna(subset=num_cols, inplace=True)
    return df

df_all = load_data()

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Konfigurasi WP")
    st.markdown("---")

    st.markdown("### 📂 Filter Kategori")
    categories = ["Semua"] + sorted(df_all["Menu Category"].unique().tolist())
    selected_cat = st.selectbox("Kategori Menu", categories)

    st.markdown("### 🔢 Jumlah Alternatif")
    top_n = st.slider("Tampilkan Top-N menu", min_value=5, max_value=30, value=10, step=1)

    st.markdown("---")
    st.markdown("### ⚖️ Bobot Kriteria")
    st.caption("Geser slider untuk mengatur bobot kepentingan (0.0 – 1.0)")

    w_energy   = st.slider("🔥 Kalori (Cost)", 0.0, 1.0, 0.25, 0.05)
    w_protein  = st.slider("💪 Protein (Benefit)", 0.0, 1.0, 0.30, 0.05)
    w_fat      = st.slider("🧈 Total Lemak (Cost)", 0.0, 1.0, 0.20, 0.05)
    w_sugar    = st.slider("🍬 Gula Tambahan (Cost)", 0.0, 1.0, 0.10, 0.05)
    w_sodium   = st.slider("🧂 Sodium (Cost)", 0.0, 1.0, 0.15, 0.05)

    total_w = w_energy + w_protein + w_fat + w_sugar + w_sodium
    if abs(total_w - 1.0) > 0.001:
        st.warning(f"⚠️ Total bobot = {total_w:.2f} (idealnya = 1.00)")
    else:
        st.success(f"✅ Total bobot = {total_w:.2f}")

    st.markdown("---")
    st.markdown("### ℹ️ Info")
    st.markdown("""
    **Dataset:** McDonald's India Menu  
    **Metode:** Weighted Product (WP)  
    **Kriteria:** 5 variabel nutrisi  
    """)

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🥗 SPK Pemilihan Menu Sehat</h1>
    <p>McDonald's India — Metode Weighted Product (WP) | Praktikum SCPK — UPN Veteran Yogyakarta</p>
</div>
""", unsafe_allow_html=True)

# ─── FILTER DATA ────────────────────────────────────────────────────────────────
if selected_cat == "Semua":
    df = df_all.copy()
else:
    df = df_all[df_all["Menu Category"] == selected_cat].copy()

# Kriteria yang digunakan
CRITERIA = {
    'Energy (kCal)'   : {'type': 'cost',    'w': w_energy,  'label': 'Kalori (kCal)'},
    'Protein (g)'     : {'type': 'benefit', 'w': w_protein, 'label': 'Protein (g)'},
    'Total fat (g)'   : {'type': 'cost',    'w': w_fat,     'label': 'Total Lemak (g)'},
    'Added Sugars (g)': {'type': 'cost',    'w': w_sugar,   'label': 'Gula Tambahan (g)'},
    'Sodium (mg)'     : {'type': 'cost',    'w': w_sodium,  'label': 'Sodium (mg)'},
}

crit_cols = list(CRITERIA.keys())

# ─── SUMMARY METRICS ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Total Menu</div>
        <div class="value">{len(df)}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Kategori</div>
        <div class="value">{selected_cat}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Kriteria</div>
        <div class="value">5 Variabel</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <div class="label">Top N Ditampilkan</div>
        <div class="value">{top_n}</div>
    </div>""", unsafe_allow_html=True)

# ─── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dataset", "🧮 Perhitungan WP", "🏆 Ranking", "📈 Visualisasi"])

# ════════════════════════════════════════════════════
# TAB 1 — DATASET
# ════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📋 Data Nutrisi Menu")
    st.caption(f"Menampilkan {len(df)} item menu dari kategori: **{selected_cat}**")

    show_cols = ['Menu Category', 'Menu Items'] + crit_cols
    st.dataframe(
        df[show_cols].reset_index(drop=True),
        use_container_width=True,
        height=420,
    )

    st.markdown("### 📌 Penjelasan Kriteria WP")
    crit_info = pd.DataFrame([
        {"Kriteria": v['label'], "Kolom": k, "Tipe": "✅ Benefit" if v['type']=='benefit' else "❌ Cost", "Bobot": v['w']}
        for k, v in CRITERIA.items()
    ])
    st.dataframe(crit_info, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# TAB 2 — PERHITUNGAN WP
# ════════════════════════════════════════════════════
with tab2:

    # Normalisasi bobot
    total_w = sum(v['w'] for v in CRITERIA.values())
    if total_w == 0:
        st.error("Total bobot tidak boleh 0. Atur slider di sidebar.")
        st.stop()

    weights_norm = {k: v['w']/total_w for k, v in CRITERIA.items()}

    st.markdown("""
    <div class="step-box">
        <div class="step-title">LANGKAH 1 — NORMALISASI BOBOT</div>
        Bobot ternormalisasi diperoleh dengan membagi tiap bobot dengan total bobot keseluruhan.
    </div>
    """, unsafe_allow_html=True)

    w_df = pd.DataFrame([
        {"Kriteria": CRITERIA[k]['label'], "Tipe": CRITERIA[k]['type'].capitalize(),
         "Bobot Input": CRITERIA[k]['w'], "Bobot Ternormalisasi (Wj)": round(weights_norm[k], 4)}
        for k in CRITERIA
    ])
    st.dataframe(w_df, use_container_width=True, hide_index=True)

    # ── Hitung Vektor S ──────────────────────────────────────
    st.markdown("""
    <div class="step-box">
        <div class="step-title">LANGKAH 2 — HITUNG VEKTOR S (NILAI PRODUK TERBOBOT)</div>
        Formula: <b>Si = Π (Xij ^ Wj)</b><br>
        Pangkat positif (+Wj) untuk kriteria Benefit, pangkat negatif (-Wj) untuk kriteria Cost.
    </div>
    """, unsafe_allow_html=True)

    df_wp = df[['Menu Category', 'Menu Items'] + crit_cols].copy().reset_index(drop=True)

    S_values = []
    for _, row in df_wp.iterrows():
        s = 1.0
        for col, meta in CRITERIA.items():
            val = row[col]
            if val <= 0:
                val = 1e-9  # avoid log(0)
            exp = weights_norm[col] if meta['type'] == 'benefit' else -weights_norm[col]
            s *= (val ** exp)
        S_values.append(s)

    df_wp['Vektor S'] = S_values

    st.dataframe(
        df_wp[['Menu Items'] + crit_cols + ['Vektor S']].round(5).head(20),
        use_container_width=True, height=350
    )

    # ── Hitung Vektor V ──────────────────────────────────────
    st.markdown("""
    <div class="step-box">
        <div class="step-title">LANGKAH 3 — HITUNG VEKTOR V (PREFERENSI AKHIR)</div>
        Formula: <b>Vi = Si / Σ Si</b><br>
        Vektor V adalah nilai preferensi ternormalisasi; semakin besar V, semakin sehat menu tersebut.
    </div>
    """, unsafe_allow_html=True)

    total_S = sum(S_values)
    df_wp['Vektor V'] = df_wp['Vektor S'] / total_S
    df_wp['Rank'] = df_wp['Vektor V'].rank(ascending=False).astype(int)
    df_wp_sorted = df_wp.sort_values('Rank')

    st.dataframe(
        df_wp_sorted[['Rank', 'Menu Items', 'Vektor S', 'Vektor V']].round(6).head(top_n),
        use_container_width=True, height=350
    )

# ════════════════════════════════════════════════════
# TAB 3 — RANKING
# ════════════════════════════════════════════════════
with tab3:
    top_df = df_wp_sorted.head(top_n).copy()
    best = top_df.iloc[0]

    # ── Winner card ──────────────────────────────────────────
    st.markdown(f"""
    <div class="winner-card">
        <div class="rank1">🥇</div>
        <h2>{best['Menu Items']}</h2>
        <div class="score-badge">V = {best['Vektor V']:.6f}</div>
        <p style="opacity:0.7; margin-top:0.5rem">Menu paling sehat berdasarkan metode Weighted Product</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Full ranking table ────────────────────────────────────
    st.markdown(f"### 🏆 Top {top_n} Menu Paling Sehat")
    rank_display = top_df[['Rank', 'Menu Items', 'Menu Category', 'Vektor V',
                            'Energy (kCal)', 'Protein (g)', 'Total fat (g)',
                            'Added Sugars (g)', 'Sodium (mg)']].copy()
    rank_display['Vektor V'] = rank_display['Vektor V'].map(lambda x: f"{x:.6f}")
    rank_display = rank_display.rename(columns={
        'Menu Items': 'Menu', 'Menu Category': 'Kategori',
        'Energy (kCal)': 'Kalori', 'Protein (g)': 'Protein',
        'Total fat (g)': 'Lemak', 'Added Sugars (g)': 'Gula Tambahan',
        'Sodium (mg)': 'Sodium'
    })
    st.dataframe(rank_display.reset_index(drop=True), use_container_width=True, height=420)

# ════════════════════════════════════════════════════
# TAB 4 — VISUALISASI
# ════════════════════════════════════════════════════
with tab4:
    top_vis = df_wp_sorted.head(top_n).copy()

    # Bar chart — Vektor V
    st.markdown("### 📊 Nilai Preferensi (Vektor V) — Top Menu")
    fig_bar = px.bar(
        top_vis,
        x='Vektor V', y='Menu Items',
        orientation='h',
        color='Vektor V',
        color_continuous_scale=['#ffc72c', '#ff6b35', '#da291c'],
        text=top_vis['Vektor V'].map(lambda x: f"{x:.5f}"),
        labels={'Menu Items': 'Menu', 'Vektor V': 'Nilai Preferensi (V)'},
    )
    fig_bar.update_layout(
        yaxis=dict(autorange='reversed'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_family='Plus Jakarta Sans',
        coloraxis_showscale=False,
        height=420,
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    col_l, col_r = st.columns(2)

    # Scatter — Kalori vs Protein
    with col_l:
        st.markdown("### 🔵 Kalori vs Protein")
        fig_sc = px.scatter(
            top_vis,
            x='Energy (kCal)', y='Protein (g)',
            size='Vektor V',
            color='Vektor V',
            color_continuous_scale=['#ffc72c', '#da291c'],
            hover_name='Menu Items',
            labels={'Energy (kCal)': 'Kalori (kCal)', 'Protein (g)': 'Protein (g)'},
            size_max=30,
        )
        fig_sc.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                             font_family='Plus Jakarta Sans', height=350,
                             coloraxis_showscale=False)
        st.plotly_chart(fig_sc, use_container_width=True)

    # Radar chart — top 5
    with col_r:
        st.markdown("### 🕸️ Profil Nutrisi Top 5")
        top5 = df_wp_sorted.head(5).copy()
        radar_cols = ['Energy (kCal)', 'Protein (g)', 'Total fat (g)', 'Added Sugars (g)', 'Sodium (mg)']
        radar_labels = ['Kalori', 'Protein', 'Lemak', 'Gula', 'Sodium']

        fig_radar = go.Figure()
        colors = ['#da291c', '#ff6b35', '#ffc72c', '#27ae60', '#2980b9']

        for i, (_, row) in enumerate(top5.iterrows()):
            vals = []
            for c in radar_cols:
                col_max = df_wp[c].max()
                col_min = df_wp[c].min()
                norm = (row[c] - col_min) / (col_max - col_min + 1e-9)
                # for cost, invert so lower=better shows high on radar
                if CRITERIA[c]['type'] == 'cost':
                    norm = 1 - norm
                vals.append(round(norm, 3))

            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=radar_labels + [radar_labels[0]],
                fill='toself',
                name=row['Menu Items'][:25],
                line_color=colors[i],
                opacity=0.6,
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            font_family='Plus Jakarta Sans',
            height=350,
            paper_bgcolor='white',
            legend=dict(font=dict(size=10)),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Pie — distribusi kategori top-N
    st.markdown(f"### 🥧 Distribusi Kategori — Top {top_n} Menu Sehat")
    cat_count = top_vis['Menu Category'].value_counts().reset_index()
    cat_count.columns = ['Kategori', 'Jumlah']
    fig_pie = px.pie(cat_count, values='Jumlah', names='Kategori',
                     color_discrete_sequence=['#da291c','#ff6b35','#ffc72c','#27ae60','#2980b9','#8e44ad','#e67e22'])
    fig_pie.update_layout(font_family='Plus Jakarta Sans', height=350, paper_bgcolor='white')
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.82rem; padding: 0.5rem 0 1rem;">
    🎓 Praktikum Sistem Cerdas & Pendukung Keputusan — UPN Veteran Yogyakarta &nbsp;|&nbsp;
    Metode: <b>Weighted Product (WP)</b> &nbsp;|&nbsp; Dataset: McDonald's India Menu
</div>
""", unsafe_allow_html=True)
