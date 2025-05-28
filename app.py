import streamlit as st
from recommender import recommander, get_all_recipes

st.set_page_config(page_title="Recipe Recommender", layout="wide")

# --------- STYLE ----------
st.markdown("""
<style>
body {
    background-color: #faebd7;
}
.block {
    background-color: #fff8f0;
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 15px;
}
.search-btn {
    background-color: #cc5500;
    color: white;
    border: none;
    padding: 0.5em 1.2em;
    border-radius: 10px;
    font-weight: bold;
}
.details-btn {
    background-color: #cc5500;
    color: white;
    border: none;
    padding: 0.3em 0.9em;
    border-radius: 10px;
    font-size: 0.9em;
}
</style>
""", unsafe_allow_html=True)

# --------- HEADER ----------
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("## Recipe Recommender")

    if st.session_state.get("go_home"):
        del st.session_state["go_home"]
        st.experimental_set_query_params() 
    
    if "search_input" not in st.session_state:
        st.session_state["search_input"] = ""

    input_recipe = st.text_input(
        "Enter a recipe", 
        value=st.session_state["search_input"], 
        key="input_recipe",  
        label_visibility="collapsed"
    )
    
    search_clicked = st.button("🔍 Search", use_container_width=False)
    
    if search_clicked or input_recipe != st.session_state["search_input"]:
        st.session_state["search_input"] = input_recipe

with col2:
    st.markdown("### Statistics")
    base_recipe = st.session_state["search_input"] if st.session_state["search_input"] else "Pizza"
    recettes = get_all_recipes()
    total = len(recettes)
    avg_common = 4 
    st.write(f"**Base recipe:** {base_recipe}")
    st.write(f"**Recipes analyzed:** {total}")
    st.write(f"**Avg ingredients in common:** {avg_common}")

st.markdown("---")

# --------- RECOMMANDATIONS ----------
if st.session_state["search_input"]:
    st.markdown("### 🔝 Top 10 Recommendations")
    results = recommander(st.session_state["search_input"])
    
    for r in results:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{r['name']}**")
                st.markdown(f"{r['common_ingredients']} ingredients in common")
                if st.button("Details", key=f"btn_{r['name']}"):
                    st.session_state["recipe_detail"] = r["name"]
                    st.switch_page("pages/recipe.py")

            with col2:
                st.markdown(f"⭐ **{r['rating']}**")
            st.markdown("---")
else:
    st.info("Enter a recipe to get recommendations.")
