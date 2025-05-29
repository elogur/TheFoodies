import streamlit as st

st.set_page_config(page_title="Recipe page")

if "recipe_detail" not in st.session_state:
    st.error("Aucune recette sélectionnée.")
    st.stop()

recipe = st.session_state["recipe_detail"]
#print(f"Recipe details: {recipe}")

st.title(f"📄 {recipe['name']}")
st.write(f"⭐ Rating : {recipe['rating']} / 5")

if "cooking_time" in recipe:
    st.write(f"⏱️ Cooking time: {recipe['cooking_time']} minutes")

st.subheader("🧂 Ingredients")
for ing in recipe["ingredients"]:
    st.markdown(f"- {ing}")

st.subheader("📖 Instructions")

st.subheader("💬 Reviews")