import streamlit as st

st.set_page_config(page_title="Recipe page")

if "recipe_detail" not in st.session_state:
    st.error("Aucune recette sélectionnée.")
    st.stop()

recipe = st.session_state["recipe_detail"]
#print(f"Recipe details: {recipe}")

st.title(f"📄 {recipe['name']}")
st.write(f"⭐ Rating : {recipe['rating']:.2f} / 5")

st.write(f"⏱️ Cooking time: {recipe['minutes']} minutes")

st.subheader("🧂 Ingredients")
for ing in recipe["ingredients"]:
    st.markdown(f"- {ing}")

st.subheader("📖 Instructions")
for i, step in enumerate(recipe["instructions"], 1):
    st.markdown(f"**Step {i}:** {step}")

st.subheader("💬 Review")
st.markdown(recipe["description"])