def rule_based_risk(bp, hr, temp):
    """
    Simple rule-based risk scoring
    """
    if bp > 180 or hr > 130 or temp > 39:
        return "High"
    elif bp > 140 or hr > 100 or temp > 38:
        return "Medium"
    else:
        return "Low"
