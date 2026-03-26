import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────
# CONFIG & CONSTANTES
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Act Energy — Portfolio Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

EXCEL_FILE = "MyAct_Final.xlsx"

ACT_COLORS = {
    "primary": "#262E4B",
    "secondary": "#86B9B7",
    "accent": "#D3A021",
    "success": "#A4D65E",
    "danger": "#E74C3C",
    "text": "#262E4B",
    "text_light": "#64748B",
    "bg": "#F5F7FA",
    "card": "#FFFFFF",
    "border": "#E2E8F0",
}

ACT_SEQUENCE = [
    "#262E4B",
    "#86B9B7",
    "#D3A021",
    "#A4D65E",
    "#5B8DB8",
    "#E8A87C",
    "#7C9EB2",
    "#C4D4A2",
]

act_template = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color="#262E4B"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=ACT_SEQUENCE,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", gridwidth=1),
    )
)

LOT_LABELS = {
    "BT": "Basse Tension",
    "HT": "Haute Tension",
    "BP": "Basse Pression",
    "HP": "Haute Pression",
    "EP": "Éclairage Public",
}
RELEVE_LABELS = {
    "AMR": "AMR (15 min)",
    "MMR": "MMR (mensuel)",
    "YMR": "YMR (annuel)",
    "SMR": "SMR (semestriel)",
}

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #262E4B;
    color: white;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stMarkdown {
    color: white !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border-left: 4px solid #86B9B7;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 0.5rem;
}
.kpi-card h3 {
    color: #64748B;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0 0 0.3rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.kpi-card .value {
    color: #262E4B;
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
}
.kpi-card .sub {
    color: #64748B;
    font-size: 0.78rem;
    margin-top: 0.2rem;
}
.kpi-card.gold { border-left-color: #D3A021; }
.kpi-card.green { border-left-color: #A4D65E; }
.kpi-card.danger { border-left-color: #E74C3C; }
.kpi-card.blue { border-left-color: #5B8DB8; }

/* Hide Streamlit branding */
#MainMenu {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
footer {display: none !important;}

/* Desktop: sidebar always visible, no close button, no header */
@media (min-width: 768px) {
    [data-testid="stSidebar"] {
        min-width: 280px !important;
        width: 280px !important;
        transform: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
}

/* Mobile: header visible with sidebar hamburger button */
@media (max-width: 767px) {
    [data-testid="stHeader"] {
        background: #262E4B !important;
    }
    /* Hide only deploy button, keep hamburger */
    [data-testid="stToolbar"] button[kind="header"] {
        display: none !important;
    }
    [data-testid="stMainMenu"] {
        display: none !important;
    }
}

/* Page background */
.stApp {
    background-color: #F5F7FA;
}

/* Section titles */
.section-title {
    color: #262E4B;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 1.5rem 0 0.5rem 0;
    padding-bottom: 0.3rem;
    border-bottom: 2px solid #86B9B7;
    display: inline-block;
}

.page-subtitle {
    color: #64748B;
    font-size: 0.9rem;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
}

/* Logo text */
.logo-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    text-align: center;
    margin-bottom: 0;
    letter-spacing: 0.05em;
}
.logo-line {
    height: 3px;
    background: #A4D65E;
    width: 80px;
    margin: 0.3rem auto 1rem auto;
    border-radius: 2px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def kpi_card(title, value, sub="", variant=""):
    cls = f"kpi-card {variant}" if variant else "kpi-card"
    return f'<div class="{cls}"><h3>{title}</h3><p class="value">{value}</p><p class="sub">{sub}</p></div>'


def fmt_energy(kwh, force_unit=None):
    """Format kWh value to human-readable string with appropriate unit."""
    if pd.isna(kwh) or kwh == 0:
        return "0 kWh"
    if force_unit == "GWh" or (force_unit is None and abs(kwh) >= 1_000_000):
        return f"{kwh / 1_000_000:,.1f} GWh"
    if force_unit == "MWh" or (force_unit is None and abs(kwh) >= 1_000):
        return f"{kwh / 1_000:,.1f} MWh"
    return f"{kwh:,.0f} kWh"


def fmt_number(n):
    """Format integer with thousand separators."""
    if pd.isna(n):
        return "0"
    return f"{int(n):,}"


def section_title(text):
    st.markdown(f'<p class="section-title">{text}</p>', unsafe_allow_html=True)


def plotly_defaults(fig, height=400):
    fig.update_layout(
        template=act_template,
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), EXCEL_FILE)
    if not os.path.exists(path):
        return None
    df = pd.read_excel(path, dtype={"site_EAN": str})
    # Fix encoding issues (Excel contains mojibake)
    df["site_type_energie"] = df["site_type_energie"].apply(
        lambda x: "Electricité" if isinstance(x, str) and "lectricit" in x else x
    )
    df["groupe_type"] = df["groupe_type"].apply(
        lambda x: "Privé" if isinstance(x, str) and "Priv" in x else x
    )
    # Ensure EAN is string with leading zeros
    df["site_EAN"] = df["site_EAN"].astype(str).str.strip()
    # Fill NaN in text columns
    for col in [
        "site_nom",
        "societe_nom",
        "groupe_nom",
        "site_type_compteur",
        "site_type_releve",
        "site_lot",
    ]:
        df[col] = df[col].fillna("")
    # Fill NaN in numeric columns
    for col in [
        "site_consommation_annuelle",
        "site_injection_annuelle",
        "societe_consommation_totale_electricite",
        "societe_consommation_totale_gaz",
        "groupe_consommation_totale_electricite",
        "groupe_consommation_totale_gaz",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    # Ensure bool
    df["groupe_actif"] = df["groupe_actif"].astype(bool)
    return df


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), "Logo actenergy négatif.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown(
            '<p class="logo-text">ACT ENERGY</p><div class="logo-line"></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "Vue d'ensemble",
            "Analyse par Groupe",
            "Analyse par Société",
            "Analyse par Lot",
            "Injections & Renouvelable",
        ],
        label_visibility="collapsed",
    )

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df = load_data()

if df is None:
    st.error(
        f"Fichier '{EXCEL_FILE}' introuvable. Placez le fichier Excel dans le même répertoire que app.py."
    )
    st.stop()


# ═════════════════════════════════════════════
# PAGE 1 — VUE D'ENSEMBLE
# ═════════════════════════════════════════════
if page == "Vue d'ensemble":
    st.title("Vue d'ensemble du portefeuille")
    st.markdown(
        '<p class="page-subtitle">Synthèse globale de l\'ensemble des points de livraison gérés par Act Energy</p>',
        unsafe_allow_html=True,
    )

    # KPIs
    total_ean = len(df)
    mask_elec = df["site_type_energie"].str.contains("lectricit", case=False, na=False)
    mask_gaz = df["site_type_energie"].str.contains("gaz", case=False, na=False)
    total_elec_kwh = df.loc[mask_elec, "site_consommation_annuelle"].sum()
    total_gaz_kwh = df.loc[mask_gaz, "site_consommation_annuelle"].sum()
    nb_elec = int(mask_elec.sum())
    nb_gaz = int(mask_gaz.sum())
    nb_groupes_actifs = df[df["groupe_actif"]]["groupe_nom"].nunique()
    total_injection = df["site_injection_annuelle"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            kpi_card(
                "EAN actifs",
                fmt_number(total_ean),
                f"{df['societe_nom'].nunique()} sociétés",
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            kpi_card(
                "Consommation Électricité",
                fmt_energy(total_elec_kwh, "GWh"),
                f"{fmt_number(nb_elec)} compteurs",
                "gold",
            ),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            kpi_card(
                "Consommation Gaz",
                fmt_energy(total_gaz_kwh, "GWh"),
                f"{fmt_number(nb_gaz)} compteurs",
                "blue",
            ),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            kpi_card(
                "Groupes actifs",
                str(nb_groupes_actifs),
                f"sur {df['groupe_nom'].nunique()} groupes",
            ),
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            kpi_card(
                "Injection totale",
                fmt_energy(total_injection, "MWh"),
                f"{fmt_number((df['site_injection_annuelle'] > 0).sum())} sites producteurs",
                "green",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Row 1: Donut Elec/Gaz + Répartition par lot
    col_left, col_right = st.columns([1, 2])

    with col_left:
        section_title("Répartition Électricité vs Gaz")
        energy_split = (
            df.groupby("site_type_energie")["site_consommation_annuelle"]
            .sum()
            .reset_index()
        )
        energy_split.columns = ["Type", "kWh"]
        fig_donut = px.pie(
            energy_split,
            values="kWh",
            names="Type",
            hole=0.55,
            color_discrete_sequence=["#D3A021", "#86B9B7"],
        )
        fig_donut.update_traces(textinfo="percent+label", textfont_size=13)
        plotly_defaults(fig_donut, 350)
        fig_donut.update_layout(showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        section_title("Répartition par lot")
        lot_stats = (
            df.groupby("site_lot")
            .agg(
                nb_ean=("site_EAN", "count"),
                volume_kwh=("site_consommation_annuelle", "sum"),
            )
            .reset_index()
        )
        lot_stats["lot_label"] = (
            lot_stats["site_lot"].map(LOT_LABELS).fillna(lot_stats["site_lot"])
        )
        lot_stats = lot_stats.sort_values("volume_kwh", ascending=True)

        fig_lot = go.Figure()
        max_vol_gwh = lot_stats["volume_kwh"].max() / 1_000_000
        # For small bars: show GWh + EAN combined outside; for large bars: GWh inside + EAN annotation
        bar_texts = []
        bar_positions = []
        for v in lot_stats["volume_kwh"]:
            gwh = v / 1_000_000
            if gwh < max_vol_gwh * 0.15:
                bar_texts.append("")  # No text inside small bars
                bar_positions.append("outside")
            else:
                bar_texts.append(f"{gwh:,.1f} GWh")
                bar_positions.append("auto")
        fig_lot.add_trace(
            go.Bar(
                y=lot_stats["lot_label"],
                x=lot_stats["volume_kwh"] / 1_000_000,
                orientation="h",
                name="Volume (GWh)",
                marker_color="#262E4B",
                text=bar_texts,
                textposition=bar_positions,
            )
        )
        plotly_defaults(fig_lot, 350)
        fig_lot.update_layout(
            xaxis_title="Volume (GWh)",
            showlegend=False,
        )
        # Add EAN count annotations + GWh for small bars
        for _, row in lot_stats.iterrows():
            vol_gwh = row["volume_kwh"] / 1_000_000
            if vol_gwh < max_vol_gwh * 0.15:
                # Small bar: show "X.X GWh · 123 EAN" outside the bar
                label = f"  {vol_gwh:,.1f} GWh · {int(row['nb_ean'])} EAN"
            else:
                label = f"  {int(row['nb_ean'])} EAN"
            fig_lot.add_annotation(
                x=vol_gwh,
                y=row["lot_label"],
                text=label,
                showarrow=False,
                xanchor="left",
                font=dict(size=11, color="#64748B"),
            )
        st.plotly_chart(fig_lot, use_container_width=True)

    # Row 2: Public vs Privé + Top 10 groupes
    col_left2, col_right2 = st.columns([1, 2])

    with col_left2:
        section_title("Public vs Privé")
        type_split = (
            df.groupby("groupe_type")["site_consommation_annuelle"].sum().reset_index()
        )
        type_split.columns = ["Type", "kWh"]
        fig_type = px.pie(
            type_split,
            values="kWh",
            names="Type",
            hole=0.55,
            color_discrete_sequence=["#262E4B", "#A4D65E"],
        )
        fig_type.update_traces(textinfo="percent+label", textfont_size=13)
        plotly_defaults(fig_type, 350)
        fig_type.update_layout(showlegend=False)
        st.plotly_chart(fig_type, use_container_width=True)

    with col_right2:
        section_title("Top 10 groupes par consommation")
        grp = (
            df.groupby("groupe_nom")
            .agg(
                elec=("groupe_consommation_totale_electricite", "first"),
                gaz=("groupe_consommation_totale_gaz", "first"),
            )
            .reset_index()
        )
        grp["total"] = grp["elec"] + grp["gaz"]
        top10 = grp.nlargest(10, "total").sort_values("total", ascending=True)

        fig_top10 = go.Figure()
        fig_top10.add_trace(
            go.Bar(
                y=top10["groupe_nom"],
                x=top10["elec"] / 1e6,
                orientation="h",
                name="Électricité",
                marker_color="#D3A021",
            )
        )
        fig_top10.add_trace(
            go.Bar(
                y=top10["groupe_nom"],
                x=top10["gaz"] / 1e6,
                orientation="h",
                name="Gaz",
                marker_color="#86B9B7",
            )
        )
        plotly_defaults(fig_top10, 420)
        fig_top10.update_layout(barmode="stack", xaxis_title="Consommation (GWh)")
        st.plotly_chart(fig_top10, use_container_width=True)


# ═════════════════════════════════════════════
# PAGE 2 — ANALYSE PAR GROUPE
# ═════════════════════════════════════════════
elif page == "Analyse par Groupe":
    st.title("Analyse par Groupe")
    st.markdown(
        '<p class="page-subtitle">Détail d\'un ou plusieurs groupes clients et de leurs sociétés</p>',
        unsafe_allow_html=True,
    )

    groupes = sorted(df["groupe_nom"].unique())
    with st.sidebar:
        st.markdown("---")
        all_groupes = st.checkbox("Tous les groupes", value=False, key="all_grp")
        if all_groupes:
            selected_groupes = groupes
        else:
            selected_groupes = st.multiselect(
                "Sélectionner un ou plusieurs groupes",
                groupes,
                default=[],
                key="sel_grp",
            )
        if not selected_groupes:
            selected_groupes = groupes

    gdf = df[df["groupe_nom"].isin(selected_groupes)]

    # KPIs
    nb_societes = gdf["societe_nom"].nunique()
    nb_ean = len(gdf)
    conso_elec = gdf[gdf["site_type_energie"] == "Electricité"][
        "site_consommation_annuelle"
    ].sum()
    conso_gaz = gdf[gdf["site_type_energie"] == "Gaz"][
        "site_consommation_annuelle"
    ].sum()
    nb_injections = (gdf["site_injection_annuelle"] > 0).sum()
    nb_grp = len(selected_groupes)
    g_types = gdf["groupe_type"].unique()
    g_type_label = g_types[0] if len(g_types) == 1 else "Mixte"

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(kpi_card("Groupes", str(nb_grp)), unsafe_allow_html=True)
    with c2:
        st.markdown(
            kpi_card("Sociétés", str(nb_societes), f"{fmt_number(nb_ean)} EAN"),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            kpi_card("Conso Élec", fmt_energy(conso_elec), "", "gold"),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            kpi_card("Conso Gaz", fmt_energy(conso_gaz), "", "blue"),
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            kpi_card("Injections", str(nb_injections), "sites producteurs", "green"),
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(kpi_card("Type", g_type_label), unsafe_allow_html=True)

    st.markdown("")

    # Sociétés du groupe
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_title("Sociétés du groupe")
        soc_agg = (
            gdf.groupby("societe_nom")
            .agg(
                nb_ean=("site_EAN", "count"),
                conso_elec=("societe_consommation_totale_electricite", "first"),
                conso_gaz=("societe_consommation_totale_gaz", "first"),
            )
            .reset_index()
        )
        soc_agg["total"] = soc_agg["conso_elec"] + soc_agg["conso_gaz"]
        soc_agg = soc_agg.sort_values("total", ascending=False)

        st.dataframe(
            soc_agg.rename(
                columns={
                    "societe_nom": "Société",
                    "nb_ean": "Nb EAN",
                    "conso_elec": "Élec (kWh)",
                    "conso_gaz": "Gaz (kWh)",
                    "total": "Total (kWh)",
                }
            ),
            column_config={
                "Élec (kWh)": st.column_config.NumberColumn(format="%,.0f"),
                "Gaz (kWh)": st.column_config.NumberColumn(format="%,.0f"),
                "Total (kWh)": st.column_config.NumberColumn(format="%,.0f"),
            },
            use_container_width=True,
            hide_index=True,
        )

    with col_right:
        section_title("Répartition par lot")
        lot_grp = (
            gdf.groupby("site_lot")["site_consommation_annuelle"].sum().reset_index()
        )
        lot_grp.columns = ["Lot", "kWh"]
        lot_grp["label"] = lot_grp["Lot"].map(LOT_LABELS).fillna(lot_grp["Lot"])
        if len(lot_grp) > 0 and lot_grp["kWh"].sum() > 0:
            fig_lot_grp = px.pie(
                lot_grp,
                values="kWh",
                names="label",
                hole=0.5,
                color_discrete_sequence=ACT_SEQUENCE,
            )
            fig_lot_grp.update_traces(textinfo="percent+label", textfont_size=11)
            plotly_defaults(fig_lot_grp, 320)
            fig_lot_grp.update_layout(showlegend=False)
            st.plotly_chart(fig_lot_grp, use_container_width=True)
        else:
            st.info("Aucune consommation enregistrée pour ce groupe.")

    # Injection bar
    total_conso_grp = conso_elec + conso_gaz
    total_inj_grp = gdf["site_injection_annuelle"].sum()
    if total_inj_grp > 0:
        section_title("Consommation vs Injection")
        fig_inj = go.Figure()
        fig_inj.add_trace(
            go.Bar(
                x=["Consommation"],
                y=[total_conso_grp / 1e3],
                name="Consommation (MWh)",
                marker_color="#262E4B",
            )
        )
        fig_inj.add_trace(
            go.Bar(
                x=["Injection"],
                y=[total_inj_grp / 1e3],
                name="Injection (MWh)",
                marker_color="#A4D65E",
            )
        )
        plotly_defaults(fig_inj, 280)
        fig_inj.update_layout(yaxis_title="MWh", showlegend=True)
        st.plotly_chart(fig_inj, use_container_width=True)

    # EAN detail table
    section_title("Détail des EAN")
    display_cols = [
        "site_EAN",
        "site_nom",
        "site_consommation_annuelle",
        "site_type_energie",
        "site_lot",
        "site_type_releve",
        "site_type_compteur",
        "site_injection_annuelle",
    ]
    ean_df = gdf[display_cols].copy()
    ean_df.columns = [
        "EAN",
        "Nom du site",
        "Conso annuelle (kWh)",
        "Énergie",
        "Lot",
        "Relevé",
        "Compteur",
        "Injection (kWh)",
    ]
    st.dataframe(
        ean_df.sort_values("Conso annuelle (kWh)", ascending=False),
        column_config={
            "Conso annuelle (kWh)": st.column_config.NumberColumn(format="%,.0f"),
            "Injection (kWh)": st.column_config.NumberColumn(format="%,.0f"),
        },
        use_container_width=True,
        hide_index=True,
        height=400,
    )


# ═════════════════════════════════════════════
# PAGE 3 — ANALYSE PAR SOCIÉTÉ
# ═════════════════════════════════════════════
elif page == "Analyse par Société":
    st.title("Analyse par Société")
    st.markdown(
        '<p class="page-subtitle">Détail d\'une ou plusieurs sociétés et de leurs compteurs</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("---")
        groupes_for_filter = sorted(df["groupe_nom"].unique())
        filter_groupes = st.multiselect(
            "Filtrer par groupe", groupes_for_filter, key="soc_filter_grp"
        )

    if filter_groupes:
        societes_list = sorted(
            df[df["groupe_nom"].isin(filter_groupes)]["societe_nom"].unique()
        )
    else:
        societes_list = sorted(df["societe_nom"].unique())

    with st.sidebar:
        all_societes = st.checkbox("Toutes les sociétés", value=False, key="all_soc")
        if all_societes:
            selected_societes = societes_list
        else:
            selected_societes = st.multiselect(
                "Sélectionner une ou plusieurs sociétés",
                societes_list,
                default=[],
                key="sel_soc",
            )
        if not selected_societes:
            selected_societes = societes_list

    sdf = df[df["societe_nom"].isin(selected_societes)]

    # KPIs
    nb_ean_s = len(sdf)
    conso_elec_s = sdf[sdf["site_type_energie"] == "Electricité"][
        "site_consommation_annuelle"
    ].sum()
    conso_gaz_s = sdf[sdf["site_type_energie"] == "Gaz"][
        "site_consommation_annuelle"
    ].sum()
    nb_soc = len(selected_societes)
    nb_grp_parent = sdf["groupe_nom"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            kpi_card("Sociétés", str(nb_soc), f"{fmt_number(nb_ean_s)} EAN"),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            kpi_card("Conso Élec", fmt_energy(conso_elec_s), "", "gold"),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            kpi_card("Conso Gaz", fmt_energy(conso_gaz_s), "", "blue"),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            kpi_card("Groupes parents", str(nb_grp_parent)), unsafe_allow_html=True
        )

    st.markdown("")

    col_left, col_right = st.columns(2)

    with col_left:
        section_title("Répartition Électricité / Gaz")
        en_split = (
            sdf.groupby("site_type_energie")["site_consommation_annuelle"]
            .sum()
            .reset_index()
        )
        en_split.columns = ["Type", "kWh"]
        if en_split["kWh"].sum() > 0:
            fig_en = px.pie(
                en_split,
                values="kWh",
                names="Type",
                hole=0.55,
                color_discrete_sequence=["#D3A021", "#86B9B7"],
            )
            fig_en.update_traces(textinfo="percent+label", textfont_size=12)
            plotly_defaults(fig_en, 320)
            fig_en.update_layout(showlegend=False)
            st.plotly_chart(fig_en, use_container_width=True)
        else:
            st.info("Aucune consommation enregistrée.")

    with col_right:
        section_title("Répartition par type de relevé")
        releve_split = sdf.groupby("site_type_releve")["site_EAN"].count().reset_index()
        releve_split.columns = ["Relevé", "Nb EAN"]
        releve_split["label"] = (
            releve_split["Relevé"].map(RELEVE_LABELS).fillna(releve_split["Relevé"])
        )
        if len(releve_split) > 0:
            fig_rel = px.pie(
                releve_split,
                values="Nb EAN",
                names="label",
                hole=0.55,
                color_discrete_sequence=ACT_SEQUENCE,
            )
            fig_rel.update_traces(textinfo="percent+label", textfont_size=12)
            plotly_defaults(fig_rel, 320)
            fig_rel.update_layout(showlegend=False)
            st.plotly_chart(fig_rel, use_container_width=True)

    # EAN table
    section_title("Liste des sites / EAN")
    display_cols_s = [
        "site_EAN",
        "site_nom",
        "site_consommation_annuelle",
        "site_type_energie",
        "site_lot",
        "site_type_releve",
        "site_type_compteur",
        "site_injection_annuelle",
    ]
    ean_s = sdf[display_cols_s].copy()
    ean_s.columns = [
        "EAN",
        "Nom du site",
        "Conso annuelle (kWh)",
        "Énergie",
        "Lot",
        "Relevé",
        "Compteur",
        "Injection (kWh)",
    ]
    st.dataframe(
        ean_s.sort_values("Conso annuelle (kWh)", ascending=False),
        column_config={
            "Conso annuelle (kWh)": st.column_config.NumberColumn(format="%,.0f"),
            "Injection (kWh)": st.column_config.NumberColumn(format="%,.0f"),
        },
        use_container_width=True,
        hide_index=True,
        height=400,
    )


# ═════════════════════════════════════════════
# PAGE 4 — ANALYSE PAR LOT
# ═════════════════════════════════════════════
elif page == "Analyse par Lot":
    st.title("Analyse par Lot (Marchés)")
    st.markdown(
        '<p class="page-subtitle">Répartition des compteurs et volumes par segment de marché</p>',
        unsafe_allow_html=True,
    )

    all_lots = sorted(df["site_lot"].unique())
    with st.sidebar:
        st.markdown("---")
        all_lots_cb = st.checkbox("Tous les lots", value=True, key="all_lots")
        if all_lots_cb:
            selected_lots = all_lots
        else:
            selected_lots = st.multiselect(
                "Sélectionner un ou plusieurs lots",
                all_lots,
                default=all_lots,
                key="sel_lots",
            )
        if not selected_lots:
            selected_lots = all_lots

    ldf = df[df["site_lot"].isin(selected_lots)]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("EAN", fmt_number(len(ldf))), unsafe_allow_html=True)
    with c2:
        st.markdown(
            kpi_card(
                "Volume total",
                fmt_energy(ldf["site_consommation_annuelle"].sum()),
                "",
                "gold",
            ),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            kpi_card("Groupes", str(ldf["groupe_nom"].nunique())),
            unsafe_allow_html=True,
        )
    with c4:
        lots_label = (
            ", ".join(selected_lots)
            if len(selected_lots) <= 3
            else f"{len(selected_lots)} lots"
        )
        st.markdown(kpi_card("Lot(s)", lots_label, "", "blue"), unsafe_allow_html=True)

    st.markdown("")

    # Tableau récapitulatif par lot
    section_title("Récapitulatif par lot")
    lot_summary = (
        ldf.groupby("site_lot")
        .agg(
            nb_ean=("site_EAN", "count"),
            volume=("site_consommation_annuelle", "sum"),
            moyenne=("site_consommation_annuelle", "mean"),
            mediane=("site_consommation_annuelle", "median"),
            maximum=("site_consommation_annuelle", "max"),
        )
        .reset_index()
    )
    lot_summary["label"] = lot_summary["site_lot"].map(LOT_LABELS)
    lot_summary = lot_summary.sort_values("volume", ascending=False)
    st.dataframe(
        lot_summary[
            ["label", "nb_ean", "volume", "moyenne", "mediane", "maximum"]
        ].rename(
            columns={
                "label": "Lot",
                "nb_ean": "Nb EAN",
                "volume": "Volume (kWh)",
                "moyenne": "Moyenne (kWh)",
                "mediane": "Médiane (kWh)",
                "maximum": "Maximum (kWh)",
            }
        ),
        column_config={
            "Volume (kWh)": st.column_config.NumberColumn(format="%,.0f"),
            "Moyenne (kWh)": st.column_config.NumberColumn(format="%,.0f"),
            "Médiane (kWh)": st.column_config.NumberColumn(format="%,.0f"),
            "Maximum (kWh)": st.column_config.NumberColumn(format="%,.0f"),
        },
        use_container_width=True,
        hide_index=True,
    )

    col_left, col_right = st.columns(2)

    with col_left:
        section_title("Distribution des consommations")
        conso_nonzero = ldf[ldf["site_consommation_annuelle"] > 0].copy()
        if len(conso_nonzero) > 0:
            lots_uniques = sorted(conso_nonzero["site_lot"].unique())
            if len(lots_uniques) > 1:
                fig_box = px.box(
                    conso_nonzero,
                    x="site_lot",
                    y="site_consommation_annuelle",
                    color="site_lot",
                    color_discrete_map={
                        lot: ACT_SEQUENCE[i % len(ACT_SEQUENCE)]
                        for i, lot in enumerate(sorted(df["site_lot"].unique()))
                    },
                    labels={
                        "site_consommation_annuelle": "Consommation annuelle (kWh)",
                        "site_lot": "Lot",
                    },
                    points="outliers",
                )
            else:
                fig_box = px.box(
                    conso_nonzero,
                    y="site_consommation_annuelle",
                    color_discrete_sequence=["#262E4B"],
                    labels={
                        "site_consommation_annuelle": "Consommation annuelle (kWh)",
                    },
                    points="outliers",
                )
            plotly_defaults(fig_box, 380)
            fig_box.update_layout(
                yaxis_title="Consommation annuelle (kWh)",
                showlegend=False,
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("Aucune consommation > 0 dans cette sélection.")

    with col_right:
        section_title("Top 15 consommateurs")
        top15 = ldf.nlargest(15, "site_consommation_annuelle")[
            ["site_nom", "site_consommation_annuelle", "site_lot"]
        ].copy()
        top15 = top15.sort_values("site_consommation_annuelle", ascending=True)
        fig_top15 = px.bar(
            top15,
            y="site_nom",
            x="site_consommation_annuelle",
            orientation="h",
            color="site_lot",
            color_discrete_map={
                lot: ACT_SEQUENCE[i % len(ACT_SEQUENCE)]
                for i, lot in enumerate(sorted(df["site_lot"].unique()))
            },
            labels={
                "site_consommation_annuelle": "kWh",
                "site_nom": "",
                "site_lot": "Lot",
            },
        )
        plotly_defaults(fig_top15, 380)
        st.plotly_chart(fig_top15, use_container_width=True)


# ═════════════════════════════════════════════
# PAGE 5 — INJECTIONS & RENOUVELABLE
# ═════════════════════════════════════════════
elif page == "Injections & Renouvelable":
    st.title("Injections & Renouvelable")
    st.markdown(
        '<p class="page-subtitle">Production locale d\'énergie (panneaux solaires) et ratio injection/consommation</p>',
        unsafe_allow_html=True,
    )

    inj_df = df[df["site_injection_annuelle"] > 0]

    # KPIs
    nb_sites_inj = len(inj_df)
    vol_inj = inj_df["site_injection_annuelle"].sum()
    total_conso = df["site_consommation_annuelle"].sum()
    ratio_inj = (vol_inj / total_conso * 100) if total_conso > 0 else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            kpi_card(
                "Sites producteurs",
                fmt_number(nb_sites_inj),
                f"sur {fmt_number(len(df))} EAN totaux",
                "green",
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            kpi_card("Volume injecté", fmt_energy(vol_inj, "MWh"), "", "green"),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            kpi_card(
                "Ratio injection/conso",
                f"{ratio_inj:.1f}%",
                "de la consommation totale",
                "gold",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("")

    col_left, col_right = st.columns(2)

    with col_left:
        section_title("Injections par groupe")
        grp_inj = (
            inj_df.groupby("groupe_nom")["site_injection_annuelle"].sum().reset_index()
        )
        grp_inj.columns = ["Groupe", "Injection (kWh)"]
        grp_inj = grp_inj.sort_values("Injection (kWh)", ascending=False)
        if len(grp_inj) > 0:
            fig_tree = px.treemap(
                grp_inj.head(20),
                path=["Groupe"],
                values="Injection (kWh)",
                color_discrete_sequence=ACT_SEQUENCE,
            )
            plotly_defaults(fig_tree, 420)
            fig_tree.update_traces(textinfo="label+value")
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_right:
        section_title("Ratio injection/conso par société")
        soc_conso = (
            df.groupby("societe_nom")
            .agg(
                conso=("site_consommation_annuelle", "sum"),
                injection=("site_injection_annuelle", "sum"),
            )
            .reset_index()
        )
        soc_conso = soc_conso[soc_conso["injection"] > 0].copy()
        soc_conso["ratio"] = (
            soc_conso["injection"] / soc_conso["conso"].replace(0, np.nan) * 100
        )
        soc_conso = soc_conso.dropna(subset=["ratio"])
        if len(soc_conso) > 0:
            fig_scatter = px.scatter(
                soc_conso,
                x="conso",
                y="injection",
                hover_name="societe_nom",
                size="injection",
                size_max=25,
                color_discrete_sequence=["#A4D65E"],
                labels={"conso": "Consommation (kWh)", "injection": "Injection (kWh)"},
            )
            plotly_defaults(fig_scatter, 420)
            st.plotly_chart(fig_scatter, use_container_width=True)

    # Table
    section_title("Sites producteurs")
    inj_display = inj_df[
        [
            "site_EAN",
            "site_nom",
            "societe_nom",
            "groupe_nom",
            "site_injection_annuelle",
            "site_consommation_annuelle",
            "site_lot",
        ]
    ].copy()
    inj_display.columns = [
        "EAN",
        "Site",
        "Société",
        "Groupe",
        "Injection (kWh)",
        "Conso (kWh)",
        "Lot",
    ]
    inj_display = inj_display.sort_values("Injection (kWh)", ascending=False)
    st.dataframe(
        inj_display,
        column_config={
            "Injection (kWh)": st.column_config.NumberColumn(format="%,.0f"),
            "Conso (kWh)": st.column_config.NumberColumn(format="%,.0f"),
        },
        use_container_width=True,
        hide_index=True,
        height=400,
    )
