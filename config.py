# app/config.py
# A central place for application configuration

# Mapping of common terms to exact database category names
CATEGORY_MAPPING = {
    "pothole": "potholes",
    "garbage": "Garbage",
    "damaged electrical poles": "DamagedElectricalPoles",
    "streetlight": "streetlight",
    "roads": "roads",
    "waterlogging": "WaterLogging",
    "fallen trees": "FallenTrees",
    "other": "other"
}

# The list of allowed database category values for security checks
ALLOWED_CATEGORIES = list(CATEGORY_MAPPING.values())