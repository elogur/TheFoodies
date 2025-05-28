# recommender.py
RECIPES = [
    {"name": "Pâtes à la carbonara", "rating": 4.5, "ingredients": {"pâtes", "œuf", "lardons", "crème"}},
    {"name": "Gratin dauphinois", "rating": 4.7, "ingredients": {"pommes de terre", "crème", "fromage"}},
    {"name": "Omelette", "rating": 4.1, "ingredients": {"œuf", "fromage", "oignon"}},
    {"name": "Salade niçoise", "rating": 4.3, "ingredients": {"thon", "œuf", "haricots verts", "olives"}},
]

def recommander(recipe_name):
    user_input = next((r for r in RECIPES if r["name"].lower() == recipe_name.lower()), None)
    if not user_input:
        return []

    recommandations = []
    for r in RECIPES:
        if r["name"].lower() == recipe_name.lower():
            continue
        commons = len(user_input["ingredients"] & r["ingredients"])
        recommandations.append({
            "name": r["name"],
            "rating": r["rating"],
            "common_ingredients": commons
        })
    return sorted(recommandations, key=lambda x: (-x["common_ingredients"], -x["rating"]))[:10]

def get_recipe(name):
    return next((r for r in RECIPES if r["name"] == name), None)

def get_all_recipes():
    return RECIPES
