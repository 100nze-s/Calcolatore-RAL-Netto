import streamlit as st
from src.calculator import load_rules, calculate_net_salary

st.set_page_config(page_title="Calcolatore Netto RAL", layout="centered")

st.title("🧮 Calcolatore Netto Annuale")
st.caption("Simulatore base per dipendenti a tempo indeterminato (Milano)")

rules = load_rules()
ral = st.number_input("Retribuzione Lorda Annuale (€)", min_value=10000, max_value=150000, value=30000, step=1000)

res = calculate_net_salary(ral, rules)

col1, col2 = st.columns(2)
col1.metric("Netto Mensile (13 mensilità)", f"€ {res['net_monthly_13']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("Netto Annuale", f"€ {res['net_annual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()
st.subheader("Dettaglio Trattenute")
st.write(f"- **Contributi INPS (9.19%):** € {res['inps']:,.2f}")
st.write(f"- **Imponibile Fiscale:** € {res['taxable']:,.2f}")
st.write(f"- **IRPEF Lorda:** € {res['irpef_gross']:,.2f}")
