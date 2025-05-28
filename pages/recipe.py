import streamlit as st
from recommender import get_recipe

st.set_page_config(page_title="Recipe page")

if "recipe_detail" not in st.session_state:
    st.error("Aucune recette sélectionnée.")
    st.stop()

name = st.session_state["recipe_detail"]
recipe = get_recipe(name)

if not recipe:
    st.error("No recipe.")
    st.stop()

st.title(f"📄 {recipe['name']}")
st.write(f"⭐ Note : {recipe['rating']} / 5")

st.subheader("🧂 Ingredients")
for ing in recipe["ingredients"]:
    st.markdown(f"- {ing}")

