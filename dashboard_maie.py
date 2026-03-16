
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO

st.set_page_config(
    page_title="MAIE CU Pasto",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; color-scheme: dark !important; }
.main { background-color: #0f1117; }
.stApp { background-color: #0f1117 !important; }
[data-testid="stAppViewContainer"] { background-color: #0f1117 !important; }
[data-testid="stAppViewBlockContainer"] { background-color: #0f1117 !important; }
section[data-testid="stMain"] { background-color: #0f1117 !important; }

#

.kpi-card {
    background: linear-gradient(135deg, #1a1f2e 0%, #1e2640 100%);
    border: 1px solid #2a3050; border-radius: 16px;
    padding: 24px 28px; text-align: center;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px; border-radius: 16px 16px 0 0;
}
.kpi-card.total::before     { background: #4f8ef7; }
.kpi-card.atendidas::before { background: #2ecc9a; }
.kpi-card.pendientes::before{ background: #f7a34f; }
.kpi-label { font-size: 12px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: #6b7db3; margin-bottom: 10px; }
.kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 42px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.kpi-value.total { color: #4f8ef7; }
.kpi-value.atend { color: #2ecc9a; }
.kpi-value.pend  { color: #f7a34f; }
.kpi-sub  { font-size: 11px; color: #4a5578; margin-bottom: 2px; }
.kpi-pct  { font-size: 15px; font-weight: 700; margin-top: 8px; padding: 4px 12px; border-radius: 20px; display: inline-block; }
.kpi-pct.atend { background: #2ecc9a22; color: #2ecc9a; }
.kpi-pct.pend  { background: #f7a34f22; color: #f7a34f; }
.section-title { font-size: 13px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #4f8ef7; margin: 0 0 4px 0; padding-left: 10px; border-left: 3px solid #4f8ef7; }
.section-sub { font-size: 14px; color: #6b7db3; margin-bottom: 20px; padding-left: 13px; }
[data-testid="stSidebar"] { background: #0d1020 !important; border-right: 1px solid #1e2640; }
[data-testid="stSidebar"] * { color: #c4cce8 !important; }
.header-banner { background: linear-gradient(135deg, #0d1020 0%, #141929 50%, #0f1525 100%); border: 1px solid #2a3050; border-radius: 20px; padding: 28px 36px; margin-bottom: 32px; display: flex; align-items: center; gap: 20px; }
.header-title { font-size: 26px; font-weight: 700; color: #e8eeff; margin: 0; }
.header-sub { font-size: 14px; color: #4f8ef7; font-weight: 400; margin: 4px 0 0 0; letter-spacing: 1px; }
.motivo-card { background: linear-gradient(135deg, #1a1f2e 0%, #1e2640 100%); border: 1px solid #2a3050; border-radius: 14px; padding: 18px 20px; margin-bottom: 12px; }
.motivo-card-title { font-size: 12px; font-weight: 700; color: #c4cce8; margin-bottom: 12px; }
.motivo-stats { display: flex; justify-content: space-between; margin-bottom: 10px; }
.motivo-stat-atend { font-size: 11px; color: #2ecc9a; }
.motivo-stat-pend  { font-size: 11px; color: #f7a34f; }
.progress-track { background: #0d1020; border-radius: 8px; height: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)

GDRIVE_URL = "https://docs.google.com/spreadsheets/d/1djM3sjEUeNv9YSFWU2oy8ybuuW03FSELAgG1yDiXSOc/export?format=xlsx"

def buscar_col(cols, *palabras):
    for c in cols:
        cu = c.upper()
        if all(p.upper() in cu for p in palabras):
            return c
    return None

def nombre_corto(nombre_completo):
    partes = str(nombre_completo).strip().split()
    if len(partes) >= 2:
        return partes[0] + " " + partes[1]
    return str(nombre_completo)

def procesar_hoja(df):
    col_fecha = next((c for c in df.columns if "FECHA" in c.upper() and "SEGUIMIENTO" in c.upper() and "2" not in c), None)
    if col_fecha:
        df["ATENDIDO"] = df[col_fecha].notna()
    return df

def cargar_todas_las_hojas():
    try:
        response = requests.get(GDRIVE_URL)
        response.raise_for_status()
        contenido = BytesIO(response.content)
        xl = pd.ExcelFile(contenido)
        hojas = {}
        for hoja in xl.sheet_names:
            df_hoja = pd.read_excel(BytesIO(response.content), sheet_name=hoja)
            df_hoja = procesar_hoja(df_hoja)
            hojas[hoja] = df_hoja
        return hojas, True
    except Exception as e:
        return None, str(e)

with st.sidebar:
    st.markdown("### Datos")
    st.markdown("---")
    st.markdown("""
    <div style="background:#0d1a2e;border:1px solid #4f8ef744;border-radius:10px;padding:12px 14px;margin-bottom:16px;">
      <div style="font-size:10px;color:#4f8ef7;letter-spacing:2px;font-weight:700">FUENTE</div>
      <div style="font-size:11px;color:#6b7db3;margin-top:4px">Matriz Consejeria MAIE</div>
    </div>
    """, unsafe_allow_html=True)
    actualizar = st.button("Actualizar datos", use_container_width=True)
    st.markdown("---")

if "hojas" not in st.session_state or actualizar:
    with st.spinner("Cargando datos desde Matriz Consejeria MAIE..."):
        hojas, status = cargar_todas_las_hojas()
        if status is True:
            st.session_state["hojas"] = hojas
        else:
            st.error(f"No se pudo cargar el archivo: {status}")
            st.stop()

hojas   = st.session_state["hojas"]
nombres = sorted(list(hojas.keys()), reverse=True)

with st.sidebar:
    st.markdown("### Periodo Academico")
    sel_periodo = st.selectbox("Selecciona el periodo", nombres, index=0)
    st.markdown("---")

df = hojas[sel_periodo]

col_programa = buscar_col(df.columns, "PROGRAMA")
col_motivo   = buscar_col(df.columns, "MOTIVO", "REMIS")
col_docente  = buscar_col(df.columns, "DOCENTE", "CONSEJERO")
col_fecha    = next((c for c in df.columns if "FECHA" in c.upper() and "SEGUIMIENTO" in c.upper() and "2" not in c), None)
col_id       = buscar_col(df.columns, "ID")

with st.sidebar:
    st.markdown(f"""
    <div style="background:#0d2518;border:1px solid #2ecc9a44;border-radius:10px;padding:12px 14px;">
      <div style="font-size:10px;color:#2ecc9a;letter-spacing:2px;font-weight:700">PERIODO ACTIVO</div>
      <div style="font-size:16px;font-weight:700;color:#2ecc9a;margin-top:4px">{sel_periodo}</div>
      <div style="font-size:11px;color:#4a5578;margin-top:2px">{len(df)} registros</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Filtros")
    programas = ["Todos"] + sorted(df[col_programa].dropna().unique().tolist())
    sel_programa = st.selectbox("Programa", programas)
    docentes = ["Todos"] + sorted(df[col_docente].dropna().unique().tolist())
    sel_docente = st.selectbox("Docente Consejero", docentes)
    motivos = ["Todos"] + sorted(df[col_motivo].dropna().unique().tolist())
    sel_motivo = st.selectbox("Motivo", motivos)
    estado_opts = ["Todos", "Atendidos", "Pendientes"]
    sel_estado = st.radio("Estado", estado_opts)

dff = df.copy()
if sel_programa != "Todos": dff = dff[dff[col_programa] == sel_programa]
if sel_docente  != "Todos": dff = dff[dff[col_docente]  == sel_docente]
if sel_motivo   != "Todos": dff = dff[dff[col_motivo]   == sel_motivo]
if sel_estado == "Atendidos":    dff = dff[dff["ATENDIDO"] == True]
elif sel_estado == "Pendientes": dff = dff[dff["ATENDIDO"] == False]

total      = len(dff)
atendidas  = int(dff["ATENDIDO"].sum())
pendientes = total - atendidas
pct_atend  = round(atendidas  / total * 100, 1) if total > 0 else 0
pct_pend   = round(pendientes / total * 100, 1) if total > 0 else 0

st.markdown("""
<div class="header-banner">
  <div style="font-size:48px;">🎓</div>
  <div>
    <p class="header-title">Dashboard - Consejeria MAIE CU Pasto</p>
    <p class="header-sub">MAIE - Modelo de Atencion Integral al Estudiante</p>
  </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'''<div class="kpi-card total">
      <div class="kpi-label">Total Remisiones</div>
      <div class="kpi-value total">{total}</div>
      <div class="kpi-sub">registros en el periodo</div>
    </div>''', unsafe_allow_html=True)
with c2:
    st.markdown(f'''<div class="kpi-card atendidas">
      <div class="kpi-label">Atendidas</div>
      <div class="kpi-value atend">{atendidas}</div>
      <div class="kpi-sub">con fecha de seguimiento 1</div>
      <div class="kpi-pct atend">{pct_atend}% del total</div>
    </div>''', unsafe_allow_html=True)
with c3:
    st.markdown(f'''<div class="kpi-card pendientes">
      <div class="kpi-label">Pendientes</div>
      <div class="kpi-value pend">{pendientes}</div>
      <div class="kpi-sub">sin fecha de atencion</div>
      <div class="kpi-pct pend">{pct_pend}% del total</div>
    </div>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<p class="section-title">Cobertura por Programa</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Remisiones totales vs. atendidas por cada programa academico</p>', unsafe_allow_html=True)

prog_df = dff.groupby(col_programa).agg(Total=("ATENDIDO","count"), Atendidas=("ATENDIDO","sum")).reset_index()
prog_df["Pendientes"] = prog_df["Total"] - prog_df["Atendidas"]
prog_df["Pct"] = (prog_df["Atendidas"] / prog_df["Total"] * 100).round(1)
prog_df = prog_df.sort_values("Total", ascending=True)

fig_prog = go.Figure()
fig_prog.add_trace(go.Bar(
    y=prog_df[col_programa], x=prog_df["Atendidas"], name="Atendidas",
    orientation="h", marker_color="#2ecc9a",
    text=[f"{v} ({p}%)" for v, p in zip(prog_df["Atendidas"], prog_df["Pct"])],
    textposition="inside", insidetextanchor="middle", textfont=dict(color="white", size=12)
))
fig_prog.add_trace(go.Bar(
    y=prog_df[col_programa], x=prog_df["Pendientes"], name="Pendientes",
    orientation="h", marker_color="#f7a34f",
    text=prog_df["Pendientes"],
    textposition="inside", insidetextanchor="middle", textfont=dict(color="white", size=12)
))
fig_prog.update_layout(
    barmode="stack", height=480,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c4cce8"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="#1e2640", title="Cantidad de remisiones"),
    yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=20, t=10, b=10)
)
st.plotly_chart(fig_prog, use_container_width=True)

with st.expander("Ver tabla detallada por programa"):
    prog_show = prog_df[[col_programa,"Total","Atendidas","Pendientes","Pct"]].copy()
    prog_show.columns = ["Programa","Total","Atendidas","Pendientes","% Atencion"]
    st.dataframe(prog_show.sort_values("Total", ascending=False).reset_index(drop=True).style.background_gradient(subset=["% Atencion"], cmap="RdYlGn").format({"% Atencion":"{:.1f}%"}), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<p class="section-title">Gestion por Docente Consejero</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Remisiones atendidas y pendientes por consejero</p>', unsafe_allow_html=True)

doc_df = dff.groupby(col_docente).agg(Atendidas=("ATENDIDO","sum"), Total=("ATENDIDO","count")).reset_index()
doc_df["Pendientes"] = doc_df["Total"] - doc_df["Atendidas"]
doc_df["Etiqueta"] = doc_df[col_docente].apply(nombre_corto)
doc_df = doc_df.sort_values("Total", ascending=False)

col_doc, col_gauge = st.columns([3, 2])
with col_doc:
    fig_doc = go.Figure()
    fig_doc.add_trace(go.Bar(
        x=doc_df["Etiqueta"], y=doc_df["Atendidas"], name="Atendidas", marker_color="#2ecc9a",
        text=doc_df["Atendidas"], textposition="outside", textfont=dict(color="#2ecc9a", size=12),
        hovertemplate="<b>%{x}</b><br>Atendidas: %{y}<extra></extra>"
    ))
    fig_doc.add_trace(go.Bar(
        x=doc_df["Etiqueta"], y=doc_df["Pendientes"], name="Pendientes", marker_color="#f7a34f",
        text=doc_df["Pendientes"], textposition="outside", textfont=dict(color="#f7a34f", size=12),
        hovertemplate="<b>%{x}</b><br>Pendientes: %{y}<extra></extra>"
    ))
    fig_doc.update_layout(
        height=400, barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c4cce8", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(tickangle=-25, gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#1e2640", title="Cantidad de remisiones"),
        margin=dict(l=10, r=10, t=20, b=100)
    )
    st.plotly_chart(fig_doc, use_container_width=True)

with col_gauge:
    fig_g = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=pct_atend,
        title={"text": "Tasa Global de Atencion", "font": {"size": 14, "color": "#c4cce8"}},
        number={"suffix": "%", "font": {"size": 36, "color": "#a78bfa"}},
        delta={"reference": 80, "increasing": {"color": "#2ecc9a"}, "decreasing": {"color": "#f7a34f"}},
        gauge={"axis": {"range": [0,100]}, "bar": {"color": "#a78bfa"}, "bgcolor": "#1a1f2e", "bordercolor": "#2a3050",
               "steps": [{"range":[0,40],"color":"rgba(247,163,79,0.1)"},{"range":[40,70],"color":"rgba(79,142,247,0.1)"},{"range":[70,100],"color":"rgba(46,204,154,0.1)"}],
               "threshold": {"line": {"color": "#4f8ef7", "width": 3}, "thickness": 0.75, "value": 80}}
    ))
    fig_g.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20,r=20,t=40,b=10), font=dict(color="#c4cce8"))
    st.plotly_chart(fig_g, use_container_width=True)

with st.expander("Ver tabla detallada por docente"):
    doc_show = doc_df[["Etiqueta","Total","Atendidas","Pendientes"]].copy()
    doc_show.columns = ["Docente Consejero","Total","Atendidas","Pendientes"]
    st.dataframe(doc_show.reset_index(drop=True).style.background_gradient(subset=["Atendidas"], cmap="Greens"), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<p class="section-title">Motivos de Remision</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Estado de atencion detallado por cada motivo de remision</p>', unsafe_allow_html=True)

mot_df = dff.groupby(col_motivo).agg(Total=("ATENDIDO","count"), Atendidas=("ATENDIDO","sum")).reset_index()
mot_df["Pendientes"] = mot_df["Total"] - mot_df["Atendidas"]
mot_df["Pct"] = (mot_df["Atendidas"] / mot_df["Total"] * 100).round(1)
mot_df = mot_df.sort_values("Total", ascending=False)

colores = ["#4f8ef7","#2ecc9a","#a78bfa","#f7a34f","#f75f7a","#4fd0f7","#f7d34f"]
cols_mot = st.columns(3)
for i, (_, row) in enumerate(mot_df.iterrows()):
    color = colores[i % len(colores)]
    nombre = str(row[col_motivo])
    pct_a = row["Pct"]
    pct_p = round(100 - pct_a, 1)
    with cols_mot[i % 3]:
        st.markdown(f'''
        <div class="motivo-card" style="border-top:3px solid {color};">
          <div class="motivo-card-title">{nombre}</div>
          <div style="font-family:monospace;font-size:36px;font-weight:700;color:{color};margin-bottom:8px;">{int(row["Total"])}</div>
          <div class="motivo-stats">
            <span class="motivo-stat-atend">Atendidas: {int(row["Atendidas"])}</span>
            <span class="motivo-stat-pend">Pendientes: {int(row["Pendientes"])}</span>
          </div>
          <div class="progress-track">
            <div style="width:{pct_a}%;background:{color};border-radius:8px;height:8px;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:5px;">
            <span style="font-size:13px;color:{color};font-weight:700">{pct_a}% atendido</span>
            <span style="font-size:13px;color:#4a5578">{pct_p}% pendiente</span>
          </div>
        </div>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<p class="section-title">Consulta por Estudiante</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Ingresa el ID del estudiante para ver su seguimiento</p>', unsafe_allow_html=True)

if col_id is None:
    st.warning("No se encontro columna de ID en el archivo.")
else:
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        id_buscar = st.text_input("", placeholder="Escribe el ID del estudiante...", label_visibility="collapsed", key="id_input")
    with col_btn:
        buscar = st.button("Buscar", use_container_width=True)

    # Activar busqueda tambien con Enter
    if id_buscar and not buscar:
        buscar = True

    if buscar and id_buscar:
        try:
            id_num = int(id_buscar.strip())
            estudiante = df[df[col_id] == id_num]
        except ValueError:
            id_num = id_buscar.strip()
            estudiante = df[df[col_id].astype(str).str.strip() == id_num]

        if len(estudiante) == 0:
            st.markdown(f"""
            <div style="background:#1a1520;border:1px solid #f7a34f44;border-radius:14px;padding:24px 28px;margin-top:16px;text-align:center;">
              <div style="font-size:16px;font-weight:700;color:#f7a34f;">No se encontro ningun estudiante con ID {id_buscar}</div>
              <div style="font-size:13px;color:#4a5578;margin-top:6px;">Verifica que el ID sea correcto</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            col_seg1      = buscar_col(df.columns, "SEGUIMIENTO 1")
            col_fecha_rem = buscar_col(df.columns, "FECHA", "REMIS")

            for _, row in estudiante.iterrows():
                programa  = str(row.get(col_programa, "No disponible"))
                docente   = str(row.get(col_docente,  "No asignado"))
                motivo    = str(row.get(col_motivo,   "No disponible"))
                fecha_remision = row.get(col_fecha_rem, None) if col_fecha_rem else None
                fecha_atencion = row.get(col_fecha, None)
                fecha_rem_str = pd.to_datetime(fecha_remision).strftime("%d/%m/%Y") if pd.notna(fecha_remision) else "No registrada"
                fecha_ate_str = pd.to_datetime(fecha_atencion).strftime("%d/%m/%Y") if pd.notna(fecha_atencion) else None
                seguimiento = str(row.get(col_seg1, "")) if col_seg1 else ""
                if not seguimiento or seguimiento == "nan": seguimiento = None
                if fecha_ate_str:
                    estado_color, estado_texto, estado_bg, estado_border = "#2ecc9a", "Atendido", "#0d2518", "#2ecc9a44"
                else:
                    estado_color, estado_texto, estado_bg, estado_border = "#f7a34f", "Pendiente", "#1a1520", "#f7a34f44"

                st.markdown(f'''
                <div style="background:linear-gradient(135deg,#1a1f2e,#1e2640);border:1px solid #2a3050;border-radius:16px;padding:28px;margin-top:16px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px;">
                    <div>
                      <div style="font-size:11px;color:#6b7db3;letter-spacing:2px;font-weight:700;text-transform:uppercase">ID Estudiante</div>
                      <div style="font-family:monospace;font-size:26px;font-weight:700;color:#4f8ef7">{id_num}</div>
                    </div>
                    <div style="background:{estado_bg};border:1px solid {estado_border};border-radius:20px;padding:6px 18px;">
                      <span style="color:{estado_color};font-weight:700;font-size:13px;">{estado_texto}</span>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:20px;">
                    <div style="background:#0d1020;border-radius:10px;padding:14px;">
                      <div style="font-size:10px;color:#6b7db3;letter-spacing:1px;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Programa</div>
                      <div style="font-size:13px;color:#c4cce8;font-weight:600">{programa}</div>
                    </div>
                    <div style="background:#0d1020;border-radius:10px;padding:14px;">
                      <div style="font-size:10px;color:#6b7db3;letter-spacing:1px;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Docente Consejero</div>
                      <div style="font-size:13px;color:#c4cce8;font-weight:600">{docente}</div>
                    </div>
                    <div style="background:#0d1020;border-radius:10px;padding:14px;">
                      <div style="font-size:10px;color:#6b7db3;letter-spacing:1px;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Motivo de Remision</div>
                      <div style="font-size:13px;color:#c4cce8;font-weight:600">{motivo}</div>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
                    <div style="background:#0d1020;border-radius:10px;padding:14px;">
                      <div style="font-size:10px;color:#6b7db3;letter-spacing:1px;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Fecha de Remision</div>
                      <div style="font-size:15px;color:#4f8ef7;font-weight:700;font-family:monospace">{fecha_rem_str}</div>
                    </div>
                    <div style="background:#0d1020;border-radius:10px;padding:14px;">
                      <div style="font-size:10px;color:#6b7db3;letter-spacing:1px;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Fecha de Atencion</div>
                      <div style="font-size:15px;font-weight:700;font-family:monospace;color:{estado_color}">{fecha_ate_str if fecha_ate_str else "Sin fecha de atencion"}</div>
                    </div>
                  </div>
                  <div style="background:#0d1020;border-radius:10px;padding:16px;">
                    <div style="font-size:10px;color:#6b7db3;letter-spacing:1px;font-weight:700;text-transform:uppercase;margin-bottom:8px;">Seguimiento Realizado</div>
                    <div style="font-size:13px;color:{"#c4cce8" if seguimiento else "#f7a34f"};line-height:1.6;">{"Pendiente por realizar seguimiento" if not seguimiento else seguimiento}</div>
                  </div>
                </div>''', unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;padding:20px 0 10px;'>
  <div style='color:#4f8ef7;font-size:12px;font-weight:700;letter-spacing:1px;'>Desarrollado por José Julián Figueroa Arias</div>
  <div style='color:#6b7db3;font-size:11px;margin-top:4px;'>Profesional de Bienestar Institucional</div>
  <div style='color:#6b7db3;font-size:11px;margin-top:2px;'>Uniminuto - Centro Universitario Pasto</div>
  <div style='color:#2a3050;font-size:10px;margin-top:8px;'>MAIE - Dashboard de Seguimientos Estudiantiles</div>
</div>
""", unsafe_allow_html=True)
