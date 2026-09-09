import streamlit as st
import plotly.graph_objects as go
from src.calculator import load_rules, calculate_net_salary

# Configurazione pagina a larghezza intera
st.set_page_config(page_title="Calcolatore Netto RAL Milano", layout="wide")

# CSS Personalizzato per mettere in risalto gli elementi e definire i colori
st.markdown("""
<style>
    /* Styling del box Input RAL */
    div[data-testid="stTextInput"] {
        background-color: #0f172a;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    div[data-testid="stTextInput"] input {
        font-size: 1.5rem !important;
        font-weight: bold !important;
        color: #38bdf8 !important;
        background-color: #1e293b !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    /* Box Risultati principali (Card) */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        margin-bottom: 16px;
    }
    .metric-card-blue {
        border: 2px solid #38bdf8;
    }
    .metric-card-green {
        border: 2px solid #22c55e;
    }
    .metric-title {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
    }

    /* Tag colore per il Dettaglio */
    .tag-negative {
        color: #f87171;
        background-color: rgba(248, 113, 113, 0.12);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-family: monospace;
    }
    .tag-positive {
        color: #4ade80;
        background-color: rgba(74, 222, 128, 0.12);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-family: monospace;
    }
    .tag-neutral {
        color: #38bdf8;
        background-color: rgba(56, 189, 248, 0.12);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧮 Calcolatore Netto Annuale")
st.caption("Simulatore per dipendenti a tempo indeterminato (Milano)")

def fmt(val: float) -> str:
    return f"€ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Input RAL in evidenza
raw_input = st.text_input("💰 Inserisci la Retribuzione Lorda Annuale (RAL in €)", value="32.500")

clean_input = raw_input.replace(".", "").replace(",", ".").replace("€", "").strip()

try:
    ral = float(clean_input)
    if ral <= 0:
        st.error("Inserisci un importo maggiore di zero.")
        st.stop()
except ValueError:
    st.error("Inserisci un numero valido (es. 32500 o 32.500).")
    st.stop()

rules = load_rules()
res = calculate_net_salary(ral, rules)

st.write("") 

# Card Risultati principali in evidenza
col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown(f"""
    <div class="metric-card metric-card-blue">
        <div class="metric-title">Netto Mensile (13 mensilità)</div>
        <div class="metric-value">{fmt(res['net_monthly_13'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card metric-card-green">
        <div class="metric-title">Netto Annuale</div>
        <div class="metric-value">{fmt(res['net_annual'])}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Layout affiancato: Dettaglio a sinistra, Grafico a destra
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader("📋 Dettaglio e Trattenute")
    st.caption("ℹ️ *Tutti gli importi riportati sotto sono calcolati su **base annua**.*")
    st.write("")
    
    st.markdown(f"""
    **Retribuzione Lorda (RAL):** <span class="tag-neutral">{fmt(res['ral'])} /anno</span>

    ---

    🔹 **Contributi Previdenziali**
    * **INPS (9,19%):** <span class="tag-negative">- {fmt(res['inps'])} /anno</span><br>
      *(trattenuta versata per la copertura pensionistica)*

    🔹 **Tasse sulla Busta Paga**
    * **Imponibile Fiscale:** <span class="tag-neutral">{fmt(res['taxable'])} /anno</span> *(RAL meno contributi INPS)*
    * **IRPEF Netta:** <span class="tag-negative">- {fmt(res['irpef_net'])} /anno</span><br>
      *(IRPEF Lorda di {fmt(res['irpef_gross'])} meno Detrazione Lavoro di {fmt(res['deduction'])})*
    * **Addizionali Locali (Milano/Lombardia):** <span class="tag-negative">- {fmt(res['local_taxes'])} /anno</span>

    🔹 **Bonus e Agevolazioni**
    * **Sgravio Cuneo Fiscale:** <span class="tag-positive">+ {fmt(res['cuneo_bonus'])} /anno</span><br>
      *(integrazione economica positiva applicata al netto)*
    """, unsafe_allow_html=True)

with col_right:
    st.subheader("📊 Composizione della RAL")
    
    labels = ['Netto in Tasca', 'IRPEF Netta', 'Contributi INPS', 'Addizionali Locali']
    
    net_pure = max(0.0, res['net_annual'] - res['cuneo_bonus'])
    values = [net_pure, res['irpef_net'], res['inps'], res['local_taxes']]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.45,
        textinfo='percent',
        hoverinfo='label+value',
        marker=dict(colors=['#2ecc71', '#e74c3c', '#f39c12', '#3498db'])
    )])
    
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    
    st.plotly_chart(fig, use_container_width=True)
