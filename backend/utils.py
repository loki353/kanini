def recommend_department(bp, hr):
    if bp > 160:
        return "Cardiology"
    elif hr > 120:
        return "Emergency"
    else:
        return "General Medicine"

