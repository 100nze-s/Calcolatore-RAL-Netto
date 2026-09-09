import json

def load_rules(path="tax_rules.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_net_salary(ral: float, rules: dict) -> dict:
    inps = ral * rules["inps_rate"]
    taxable = ral - inps
    
    irpef_gross = 0
    rem_taxable = taxable
    prev_threshold = 0
    
    for bracket in rules["irpef_brackets"]:
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

    net_annual = taxable - irpef_gross
    return {
        "ral": ral,
        "inps": round(inps, 2),
        "taxable": round(taxable, 2),
        "irpef_gross": round(irpef_gross, 2),
        "net_annual": round(net_annual, 2),
        "net_monthly_13": round(net_annual / 13, 2)
    }
