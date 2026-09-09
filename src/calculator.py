import json

def load_rules(path="tax_rules.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_employee_deduction(taxable: float) -> float:
    """Calcola la detrazione da lavoro dipendente (Art. 13 TUIR)"""
    if taxable <= 15000:
        return 1955.0
    elif taxable <= 28000:
        return 1910.0 + 1190.0 * ((28000.0 - taxable) / 13000.0)
    elif taxable <= 50000:
        return 1910.0 * ((50000.0 - taxable) / 22000.0)
    return 0.0

def calculate_cuneo_bonus(ral: float) -> float:
    """Stima l'impatto del taglio del cuneo fiscale / bonus dipendenti"""
    if 8500 < ral <= 20000:
        return ral * 0.07
    elif 20000 < ral <= 32000:
        return 1000.0
    elif 32000 < ral <= 40000:
        return 1000.0 * ((40000.0 - ral) / 8000.0)
    return 0.0

def calculate_net_salary(ral: float, rules: dict) -> dict:
    inps = ral * rules.get("inps_rate", 0.0919)
    taxable = ral - inps
    
    # IRPEF Lorda
    irpef_gross = 0
    rem_taxable = taxable
    prev_threshold = 0
    
    for bracket in rules.get("irpef_brackets", []):
        limit = bracket["threshold"]
        rate = bracket["rate"]
        
        if limit is not None:
            chunk = min(rem_taxable, limit - prev_threshold)
            if chunk > 0:
                irpef_gross += chunk * rate
                rem_taxable -= chunk
                prev_threshold = limit
        else:
            if rem_taxable > 0:
                irpef_gross += rem_taxable * rate

    # Calcolo agevolazioni e detrazioni
    deduction = calculate_employee_deduction(taxable)
    cuneo_bonus = calculate_cuneo_bonus(ral)
    
    # L'IRPEF Netta non può essere inferiore a zero
    irpef_net = max(0.0, irpef_gross - deduction)
    
    # Addizionali Locali (Stima Lombardia ~1.38% + Milano 0.8%)
    local_taxes = taxable * (0.0138 + 0.0080)
    
    net_annual = taxable - irpef_net - local_taxes + cuneo_bonus
    
    return {
        "ral": ral,
        "inps": round(inps, 2),
        "taxable": round(taxable, 2),
        "irpef_gross": round(irpef_gross, 2),
        "deduction": round(deduction, 2),
        "irpef_net": round(irpef_net, 2),
        "cuneo_bonus": round(cuneo_bonus, 2),
        "local_taxes": round(local_taxes, 2),
        "net_annual": round(net_annual, 2),
        "net_monthly_13": round(net_annual / 13, 2)
    }
