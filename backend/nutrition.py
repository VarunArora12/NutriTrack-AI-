import re


# Nutrition values are approximate per 100g unless noted by serving_grams.
FOOD_DATABASE = [
    {"name": "Roti", "aliases": ["chapati", "phulka"], "serving_grams": 40, "calories": 264, "protein": 8.7, "carbs": 55, "fat": 1.2},
    {"name": "Paratha", "aliases": ["plain paratha"], "serving_grams": 80, "calories": 326, "protein": 6.4, "carbs": 45, "fat": 13},
    {"name": "Idli", "aliases": ["idly"], "serving_grams": 40, "calories": 145, "protein": 4.5, "carbs": 30, "fat": 0.7},
    {"name": "Dosa", "aliases": ["plain dosa"], "serving_grams": 100, "calories": 168, "protein": 3.9, "carbs": 29, "fat": 3.7},
    {"name": "Poha", "aliases": ["kanda poha"], "serving_grams": 150, "calories": 130, "protein": 2.6, "carbs": 25, "fat": 2.5},
    {"name": "Upma", "aliases": ["rava upma"], "serving_grams": 150, "calories": 120, "protein": 3.2, "carbs": 21, "fat": 3},
    {"name": "Cooked Rice", "aliases": ["rice", "white rice", "chawal"], "serving_grams": 150, "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    {"name": "Brown Rice", "aliases": ["brown chawal"], "serving_grams": 150, "calories": 112, "protein": 2.6, "carbs": 23, "fat": 0.9},
    {"name": "Dal Tadka", "aliases": ["dal", "daal", "yellow dal"], "serving_grams": 180, "calories": 116, "protein": 6.8, "carbs": 18, "fat": 2.6},
    {"name": "Rajma", "aliases": ["kidney bean curry"], "serving_grams": 180, "calories": 124, "protein": 6.2, "carbs": 19, "fat": 3.2},
    {"name": "Chole", "aliases": ["chana masala", "chickpea curry"], "serving_grams": 180, "calories": 164, "protein": 7.1, "carbs": 22, "fat": 5.4},
    {"name": "Paneer", "aliases": ["cottage cheese"], "serving_grams": 100, "calories": 265, "protein": 18.3, "carbs": 1.2, "fat": 20.8},
    {"name": "Paneer Butter Masala", "aliases": ["paneer curry"], "serving_grams": 180, "calories": 220, "protein": 8.5, "carbs": 8, "fat": 17},
    {"name": "Palak Paneer", "aliases": ["saag paneer"], "serving_grams": 180, "calories": 170, "protein": 8.8, "carbs": 7, "fat": 12},
    {"name": "Chicken Curry", "aliases": ["chicken masala"], "serving_grams": 180, "calories": 190, "protein": 18, "carbs": 5, "fat": 11},
    {"name": "Chicken Breast", "aliases": ["grilled chicken"], "serving_grams": 100, "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    {"name": "Egg", "aliases": ["boiled egg", "anda"], "serving_grams": 50, "calories": 156, "protein": 12.6, "carbs": 1.1, "fat": 10.6},
    {"name": "Curd", "aliases": ["dahi", "yogurt"], "serving_grams": 100, "calories": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3},
    {"name": "Greek Yogurt", "aliases": ["hung curd"], "serving_grams": 100, "calories": 59, "protein": 10, "carbs": 3.6, "fat": 0.4},
    {"name": "Milk", "aliases": ["doodh"], "serving_grams": 240, "calories": 60, "protein": 3.2, "carbs": 5, "fat": 3.3},
    {"name": "Sambar", "aliases": ["sambhar"], "serving_grams": 180, "calories": 75, "protein": 3.7, "carbs": 11, "fat": 2},
    {"name": "Vegetable Biryani", "aliases": ["veg biryani"], "serving_grams": 250, "calories": 155, "protein": 3.6, "carbs": 24, "fat": 5.2},
    {"name": "Chicken Biryani", "aliases": ["biryani"], "serving_grams": 300, "calories": 170, "protein": 9.5, "carbs": 21, "fat": 6},
    {"name": "Aloo Sabzi", "aliases": ["potato curry", "aloo curry"], "serving_grams": 150, "calories": 120, "protein": 2.1, "carbs": 18, "fat": 4.8},
    {"name": "Mixed Vegetable Sabzi", "aliases": ["vegetable curry", "sabzi"], "serving_grams": 150, "calories": 90, "protein": 2.5, "carbs": 12, "fat": 3.8},
    {"name": "Sprouts", "aliases": ["moong sprouts"], "serving_grams": 100, "calories": 30, "protein": 3, "carbs": 6, "fat": 0.2},
    {"name": "Banana", "aliases": ["kela"], "serving_grams": 120, "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
    {"name": "Apple", "aliases": ["seb"], "serving_grams": 150, "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
    {"name": "Peanuts", "aliases": ["groundnuts", "moongfali"], "serving_grams": 30, "calories": 567, "protein": 25.8, "carbs": 16, "fat": 49},
    {"name": "Whey Protein", "aliases": ["protein powder", "whey"], "serving_grams": 30, "calories": 400, "protein": 80, "carbs": 8, "fat": 6},
]


def sample_foods():
    return FOOD_DATABASE[:5]


def search_foods(query=""):
    query = (query or "").strip().lower()
    if not query:
        return [food_response(food) for food in FOOD_DATABASE]

    matches = []
    for food in FOOD_DATABASE:
        names = _food_terms(food)
        if any(query in name.lower() for name in names):
            matches.append(food_response(food))

    return matches


def estimate_meal(description):
    description = (description or "").strip()
    if not description:
        return None

    text = description.lower()
    matched_items = []

    for food in FOOD_DATABASE:
        alias = _find_alias(text, food)
        if alias:
            grams = _find_quantity_grams(text, alias, food["serving_grams"])
            matched_items.append(_estimate_food(food, grams))

    if not matched_items:
        return {
            "description": description,
            "confidence": "low",
            "items": [],
            "totals": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
            "message": "No matching food found. Try names like roti, dal, paneer, idli, rice, or chole.",
        }

    totals = {
        "calories": round(sum(item["calories"] for item in matched_items)),
        "protein": round(sum(item["protein"] for item in matched_items), 1),
        "carbs": round(sum(item["carbs"] for item in matched_items), 1),
        "fat": round(sum(item["fat"] for item in matched_items), 1),
    }

    return {
        "description": description,
        "confidence": "medium" if len(matched_items) == 1 else "good",
        "items": matched_items,
        "totals": totals,
        "message": "Estimated from NutriTrack AI's built-in food database.",
    }


def food_response(food):
    return {
        "name": food["name"],
        "aliases": food["aliases"],
        "serving_grams": food["serving_grams"],
        "per_100g": {
            "calories": food["calories"],
            "protein": food["protein"],
            "carbs": food["carbs"],
            "fat": food["fat"],
        },
    }


def _find_alias(text, food):
    names = sorted(_food_terms(food), key=len, reverse=True)
    for name in names:
        if re.search(rf"\b{re.escape(name.lower())}\b", text):
            return name.lower()
    return None


def _find_quantity_grams(text, alias, default_serving_grams):
    escaped_alias = re.escape(alias)
    unit_patterns = [
        rf"(\d+(?:\.\d+)?)\s*(kg|kilogram|kilograms|g|gram|grams|l|liter|liters|litre|litres|ml|milliliter|milliliters|millilitre|millilitres)\s+(?:of\s+)?{escaped_alias}\b",
        rf"\b{escaped_alias}\b\s*(?:-|:)?\s*(\d+(?:\.\d+)?)\s*(kg|kilogram|kilograms|g|gram|grams|l|liter|liters|litre|litres|ml|milliliter|milliliters|millilitre|millilitres)\b",
    ]
    for pattern in unit_patterns:
        match = re.search(pattern, text)
        if match:
            return _unit_to_grams(float(match.group(1)), match.group(2))

    count_patterns = [
        rf"(\d+(?:\.\d+)?)\s+(?:piece[s]?|pc[s]?|serving[s]?|plate[s]?)?\s*{escaped_alias}\b",
        rf"\b{escaped_alias}\b\s*x\s*(\d+(?:\.\d+)?)",
    ]
    for pattern in count_patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1)) * default_serving_grams

    cup_match = re.search(rf"(\d+(?:\.\d+)?)\s+cup[s]?\s+(?:of\s+)?{escaped_alias}", text)
    if cup_match:
        return float(cup_match.group(1)) * 180

    bowl_match = re.search(rf"(\d+(?:\.\d+)?)\s+bowl[s]?\s+(?:of\s+)?{escaped_alias}", text)
    if bowl_match:
        return float(bowl_match.group(1)) * 180

    return default_serving_grams


def _food_terms(food):
    terms = set()
    for term in [food["name"], *food["aliases"]]:
        normalized = term.lower().strip()
        terms.add(normalized)
        terms.add(_pluralize(normalized))
    return terms


def _pluralize(term):
    words = term.split()
    last_word = words[-1]
    if last_word.endswith("y") and len(last_word) > 1 and last_word[-2] not in "aeiou":
        words[-1] = f"{last_word[:-1]}ies"
    elif last_word.endswith(("s", "x", "ch", "sh")):
        words[-1] = f"{last_word}es"
    else:
        words[-1] = f"{last_word}s"
    return " ".join(words)


def _unit_to_grams(amount, unit):
    unit = unit.lower()
    if unit in {"kg", "kilogram", "kilograms"}:
        return amount * 1000
    if unit in {"l", "liter", "liters", "litre", "litres"}:
        return amount * 1000
    if unit in {"ml", "milliliter", "milliliters", "millilitre", "millilitres"}:
        return amount
    return amount


def _estimate_food(food, grams):
    multiplier = grams / 100
    return {
        "name": food["name"],
        "grams": round(grams, 1),
        "calories": round(food["calories"] * multiplier),
        "protein": round(food["protein"] * multiplier, 1),
        "carbs": round(food["carbs"] * multiplier, 1),
        "fat": round(food["fat"] * multiplier, 1),
    }
