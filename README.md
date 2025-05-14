# TheFoodies

**TheFoodies** is a project focused on graph-based data exploration and analysis of cooking recipes. It aims to represent and study the relationships between recipes, ingredients, and user interactions using graph structures.

## Objective

The goal of this project is to explore the underlying structure of culinary data using graph techniques, in order to better understand user preferences, similarities between recipes, and culinary trends.

## Requirements

To run the main notebook `main.ipynb`, you need to:

1. Download the dataset from Kaggle:  
   🔗 [Food.com Recipes and User Interactions Dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)

2. Extract the contents of the dataset into a folder named **`archive/`** at the root of the project.

## Project Structure

- `main.ipynb` – Main notebook for loading, processing, and visualizing recipe data using graphs.
- `archive/` – Directory containing the `.csv` files extracted from the Kaggle dataset.
- `requirements.txt` *(optional)* – List of required Python packages for running the notebook.

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
   # TheFoodies/
   # ├── archive/
   # │   ├── RAW_recipes.csv
   # │   └── interactions.csv
   # ├── main.ipynb
   # └── README.md

   # (Optional) Set up a virtual environment
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Launch Jupyter Notebook
   jupyter notebook

