import streamlit as st
import plotly.graph_objects as go
from src.calculator import load_rules, calculate_net_salary

# Configurazione pagina a larghezza intera
st.set_page_config(page_title="Calcolatore Netto RAL Milano", layout="wide")

st.title("🧮 Calcolatore Netto Annuale")
st.caption("Simulatore per dipendenti a tempo indeterminato (Milano)")

# Helper per la formattazione dei numeri in euro
def fmt(val: float) -> str:
    return f"€ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Input libero come testo (accetta es. 30000, 30.000 o 30000,00)
raw_input = st.text_input("Inserisci la Retribuzione Lorda Annuale (€)", value="30.000")

# Normalizzazione dell'input dell'utente
clean_input = raw_input.replace(".", "").replace(",", ".").replace("€", "").strip()

try:
    ral = float(clean_input)
    if ral <= 0:
        st.error("Inserisci un importo maggiore di zero.")
        st.stop()
except ValueError:
    st.error("Inserisci un numero valido (es. 30000 o 30.000).")
    st.stop()

rules = load_rules()
res = calculate_net_salary(ral, rules)

# Indicatori Principali
col_m1, col_m2 = st.columns(2)
col_m1.metric("Netto Mensile (13 mensilità)", fmt(res['net_monthly_13']))
col_m2.metric("Netto Annuale", fmt(res['net_annual']))

st.divider()

# Layout affiancato: Dettaglio a sinistra, Grafico a destra
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader("📋 Dettaglio e Trattenute")
    
    st.markdown(f"""
    **Retribuzione Lorda (RAL):** `{fmt(res['ral'])}`

    ---

    🔹 **Contributi Previdenziali**
    * **INPS (9,19%):** `- {fmt(res['inps'])}` *(versati per la copertura pensionistica)*

    🔹 **Tasse sulla Busta Paga**
    * **Imponibile Fiscale:** `{fmt(res['taxable'])}` *(RAL meno contributi INPS)*
    * **IRPEF Netta:** `- {fmt(res['irpef_net'])}`
      *(Calcolata come IRPEF Lorda {fmt(res['irpef_gross'])} meno Detrazione da Lavoro {fmt(res['deduction'])})*
    * **Addizionali Locali (Milano/Lombardia):** `- {fmt(res['local_taxes'])}`

    🔹 **Bonus e Agevolazioni**
    * **Sgravio Cuneo Fiscale:** `+ {fmt(res['cuneo_bonus'])}` *(integrato direttamente nel netto)*
    """)

with col_right:
    st.subheader("Composizione RAL")
    
    # Quote per il Grafico a Donut
    labels = ['Netto in Tasca', 'IRPEF Netta', 'Contributi INPS', 'Addizionali Locali']
    
    # Calcolo della quota del netto escludendo il bonus per bilanciare il 100% della RAL visualizzata
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
