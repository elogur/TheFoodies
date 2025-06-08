import streamlit as st
from recommender.graph_manager import recipe_recommender, graph_manager


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

    norm_method = st.selectbox(
        "🔢 Similarity Calculation Method:",
        options=[
            "0 - Most Shared Ingredients",
            "1 - Highest Percentage of Shared Ingredients ",
            "2 - Percentage of Shared Ingredients  + Recipe Rating"
        ],
        index=1
    )

    norm_type = int(norm_method.split(" - ")[0])

    explanation_map = {
        0: "👉 **Method 0**: The more ingredients two recipes share, the more similar they are considered.",
        1: "👉 **Method 1**: The number of shared ingredients is divided by the total number of ingredients in the compared recipe. This avoids favoring recipes just because they have many ingredients.",
        2: "👉 **Method 2**: Like Method 1, but also incorporates the average recipe rating (weighted). Ideal for finding alternatives that are both similar **and** well-rated."
    }
    st.markdown(explanation_map[norm_type])

    search_clicked = st.button("🔍 Search", use_container_width=False)
    
    if search_clicked or input_recipe != st.session_state["search_input"]:
        st.session_state["search_input"] = input_recipe

#with col2:
    #st.markdown("### Statistics")

st.markdown("---")

# --------- RECOMMANDATIONS ----------
if st.session_state["search_input"]:
    st.markdown("### 🔝 Top 10 Recommendations")

    recipe_id, suggestions = graph_manager.find_recipe_by_name(st.session_state["search_input"])
    if recipe_id is not None:
        results = recipe_recommender.graph_manager.recommend_similar_recipes(recipe_id, top_k=10, normalization_type=norm_type)
    else:
        st.warning(f"Recipe not found. Try : {', '.join(suggestions)}")
        results = []
    
    for r in results:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{r['name']}**")
                st.markdown(f"{len(r['shared_ingredients'])} common ingredients")
                
                if st.button("Details", key=f"btn_{r['name']}"):
                    st.session_state["recipe_detail"] = r
                    st.switch_page("pages/recipe.py")

            with col2:
                st.markdown(f"⭐ **{r['rating']:.1f}**" if r["rating"] else "⭐ **N/A**")
            st.markdown("---")

else:
    st.info("Enter a recipe to get recommendations.")
