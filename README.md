# TheFoodies

**TheFoodies** is a project focused on graph-based data exploration and analysis of cooking recipes. It represents and studies the relationships between recipes, ingredients, and user interactions using graph structures.

## 🎯 Objective

The goal of this project is to explore the underlying structure of culinary data using graph techniques, in order to better understand user preferences, similarities between recipes, and culinary trends.  
The app allows users to search for recipes, view detailed descriptions, ingredients, preparation steps, and discover similar recipes based on shared ingredients and ratings.

---

## 📦 Requirements

1. Download the dataset from Kaggle:  
   🔗 [Food.com Recipes and User Interactions Dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)

2. Extract the contents into a folder named **`archive/`** at the root of the project.

---

## Usage

1. Clone the repository, download the dataset, and set up your environment:
   ```bash
   # Clone the project
   git clone https://github.com/your-username/TheFoodies.git
   cd TheFoodies

   # Download the dataset manually from Kaggle:
   # https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
   # Then extract the contents into a folder named 'archive/' at the root of the project.

   # The folder structure should look like:
   #TheFoodies/
   #├── archive/ # Dataset CSV files
   #│ ├── RAW_recipes.csv
   #│ └── RAW_interactions.csv
   #├── evaluation/
   #│ ├── Recipe Recommender User Survey.csv
   #├── pages/
   #│ └── recipe.py # Recipe detail page
   #├── presentations/
   #│ ├── graph_3d_colored_edges.html
   #│ ├── main.ipynb # Jupyter notebook for exploration
   #│ ├── The Foodies progress presentation.pdf
   #│ ├── The Foodies proposal presentation.pdf
   #│ └── The Foodies final presentation.pdf
   #├── recommender/
   #│ ├── statistics.ipynb
   #│ └── graph_manager.py # Graph-based logic and similarity engine
   #├── app.py # Streamlit app main entry
   #└── README.md # Project documentation

   # (Optional) Set up a virtual environment
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate

   # Install dependencies

   # Launch Jupyter Notebook
   jupyter notebook

2. Run the Streamlit app
   ```bash
   streamlit run app.py

## Features 

Search for recipes by name (with fuzzy search).

View:

- ✅ Title & Ingredients

- ⏱️ Cooking time (minutes)

- 📋 Step-by-step instructions (steps)

- 📝 Description

Explore similar recipes using a graph-based similarity score.

Built-in normalization strategies to rank recommendations.

Debug mode for verbose loading and graph building logs.

## Technologies 

- Python 🐍

- Pandas & NetworkX 🧠

- Streamlit 🌐

- Jupyter Notebooks 📓

- Fuzzy matching (difflib)

