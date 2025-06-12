import pandas as pd
import ast
import networkx as nx
import os

from collections import defaultdict, Counter
from itertools import combinations
from difflib import get_close_matches

class GraphManager():

    def __init__(self, nrows=200, data_path='archive/', debug=False, min_shared_ingredients=3, randomized_recipes=True):
        self.nrows: int = nrows  # nr of recipes used
        self.data_path: str = data_path
        self.graph: nx.Graph = None
        self.id_to_name: dict[int, str] = {}
        self.name_to_id: dict[str, int] = {}
        self.ingredient_to_recipes: dict[str, set] = None  # {ingredient: {recipe_id1, recipe_id2, ...}}
        self.recipe_ingredients: dict[int, list[str]] = {}
        self.recipe_minutes: dict[int, int] = {}
        self.recipe_instructions: dict[int, list[str]] = {}
        self.recipe_descriptions: dict[int, str] = {}
        self.id_to_rating: dict[int, float] = {}
        self.id_to_rating_count: dict[int, int] = {}  # Not currently used but can be used in the future for a better weighting of ratings
        self.recipe_ids_in_graph: set[int] = set()  # Track which recipes are actually in the graph
        self.debug: bool = debug

        df = self.load_data(randomized_recipes=randomized_recipes)
        self.build_graph(df, min_shared_ingredients=min_shared_ingredients)
        self.load_ratings()  # Load ratings after graph is built

    def load_data(self, randomized_recipes=True):
        """Load and process recipe data using RAW_recipes.csv"""
        if self.debug:
            print("Loading recipe data...")

        # Load recipe data from RAW_recipes.csv with ingredients column
        
        if randomized_recipes is False:
            # This is a version choosing the first nrow rows, the file is in alphabetically order
            df = pd.read_csv(
                os.path.join(self.data_path, "RAW_recipes.csv"), 
                usecols=['id', 'name', 'ingredients', 'minutes', 'steps', 'description'],
                nrows=self.nrows
            )
        else:        
            # a version with random columns, should be used in production to prevent wrong alphabetically balance while limiting the recipes
            df = pd.read_csv(
                os.path.join(self.data_path, "RAW_recipes.csv"), 
                usecols=['id', 'name', 'ingredients', 'minutes', 'steps', 'description']
            )  # read all not only nrows

            df = df.sample(n=self.nrows, random_state=42)  # random state so it is shuffled but always the same way

        # Remove entries without name
        df = df.dropna(subset=['name'])

        # Parse ingredients
        df['ingredients_list'] = df['ingredients'].apply(self._parse_ingredients)

        # Remove recipes with no valid ingredients after parsing
        df = df[df['ingredients_list'].apply(len) > 0]
        self.recipe_ids_in_graph = set(df['id'].tolist())

        # Deprecated: Filter out top 0.5% most common ingredients
        # df = self._filter_top_ingredients(df)

        # Parse steps
        df['steps_list'] = df['steps'].apply(self._parse_steps)
        self.recipe_instructions = dict(zip(df['id'], df['steps_list']))

        # Store minutes
        self.recipe_minutes = dict(zip(df['id'], df['minutes'].fillna(0).astype(int)))

        # Store descriptions
        df['description'] = df['description'].fillna("No description available.")
        self.recipe_descriptions = dict(zip(df['id'], df['description']))

        # Create name dictionaries
        self.id_to_name = dict(zip(df["id"], df["name"]))
        self.name_to_id = {name.lower(): id for id, name in self.id_to_name.items()}

        if self.debug:
            print(f"Final recipes for graph: {len(df)}")
            print(f"Recipes with valid ingredients: {len(self.recipe_ids_in_graph)}")

        return df

    def _filter_top_ingredients(self, df):
        """Remove top 1% most common ingredients to reduce non meaningful neighbor connections """
        # Count ingredient frequencies
        ingredient_counts = Counter()
        for _, row in df.iterrows():
            for ingredient in row['ingredients_list']:
                ingredient_counts[ingredient] += 1
        
        # Get top 0.5% most common ingredients
        total_ingredients = len(ingredient_counts)
        top_1_percent = int(total_ingredients * 0.005)  # top 0.5% of ingredients
        most_common = ingredient_counts.most_common(top_1_percent)
        ingredients_to_remove = {ingredient for ingredient, _ in most_common}
        
        print(f"Removing {len(ingredients_to_remove)} common ingredients: {list(ingredients_to_remove)[:100]}")
        
        # Filter ingredients from recipes
        df['ingredients_list'] = df['ingredients_list'].apply(
            lambda ingredients: [ing for ing in ingredients if ing not in ingredients_to_remove]
        )
        
        # Remove recipes with no ingredients left
        df = df[df['ingredients_list'].apply(len) > 0]
        return df

    def _parse_ingredients(self, ingredients_str):
        """
        Parse ingredients string into a list of clean ingredient names
        ->  format like "['ingredient1', 'ingredient2']"
        """

        ingredients_list = ast.literal_eval(ingredients_str)

        # Clean and normalize ingredients
        cleaned_ingredients = []
        for ingredient in ingredients_list:
            if isinstance(ingredient, str):
                # Clean the ingredient: lowercase, strip whitespace
                clean_ingredient = ingredient.lower().strip()
                cleaned_ingredients.append(clean_ingredient)
        return cleaned_ingredients
    
    def _parse_steps(self, steps_str):
        try:
            steps = ast.literal_eval(steps_str)
            return [step.strip() for step in steps if isinstance(step, str)]
        except Exception:
            return []

    def load_ratings(self):
        """Load and calculate average ratings for each recipe"""
        if self.debug:
            print("Loading rating data...")

        # Load ratings data
        ratings_df = pd.read_csv(os.path.join(self.data_path, "RAW_interactions.csv"), 
                                usecols=["recipe_id", "rating"])

        # Filter to only include ratings for recipes in our graph
        ratings_df = ratings_df[ratings_df['recipe_id'].isin(self.recipe_ids_in_graph)]

        # Calculate average rating for each recipe
        avg_ratings = ratings_df.groupby('recipe_id')['rating'].agg(['mean', 'count']).reset_index()
        avg_ratings.columns = ['recipe_id', 'avg_rating', 'rating_count']

        # Create id to rating dictionaries for fast lookup
        self.id_to_rating = dict(zip(avg_ratings['recipe_id'], avg_ratings['avg_rating']))
        self.id_to_rating_count = dict(zip(avg_ratings['recipe_id'], avg_ratings['rating_count']))

        if self.debug:
            print(f"Loaded ratings for {len(self.id_to_rating)} recipes (out of {len(self.recipe_ids_in_graph)} in graph)")
            if len(self.id_to_rating) > 0:
                print(f"Average rating across recipes in graph: {avg_ratings['avg_rating'].mean():.2f}")

    def build_graph(self, df, min_shared_ingredients: int=3):
        """Build the recipe similarity graph"""
        if self.debug:
            print("Building ingredient-to-recipes mapping...")

        # Build ingredient-to-recipes mapping
        self.ingredient_to_recipes = defaultdict(set)

        for _, row in df.iterrows():
            recipe_id = row['id']
            ingredients = row['ingredients_list']

            # Store ingredients for this recipe
            self.recipe_ingredients[recipe_id] = ingredients

            # Build reverse mapping
            for ing in ingredients:
                self.ingredient_to_recipes[ing].add(recipe_id)

        if self.debug:
            print("Building similarity graph...")
            print(f"Total unique ingredients: {len(self.ingredient_to_recipes)}")

        # Create the graph
        self.graph = nx.Graph()
        self.graph.add_nodes_from(df['id'])

        # Add edges between recipes that share ingredients
        edge_weights = defaultdict(int)

        for recipes in self.ingredient_to_recipes.values():
            if len(recipes) > 1:  # Only if ingredient appears in multiple recipes
                for r1, r2 in combinations(sorted(recipes), 2):
                    edge_weights[(r1, r2)] += 1

        # Add edges with sufficient weight
        edges_added = 0
        for (r1, r2), weight in edge_weights.items():
            if weight >= min_shared_ingredients:
                self.graph.add_edge(r1, r2, weight=weight)
                edges_added += 1

        if self.debug:
            print(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            print(f"Minimum shared ingredients threshold: {min_shared_ingredients}")

    def get_recipe_ingredients(self, recipe_id: int):
        """Get the ingredients for a specific recipe"""
        return self.recipe_ingredients.get(recipe_id, [])

    def find_recipe_by_name(self, query, max_suggestions=5):
        """Find recipe ID by name with fuzzy matching"""
        query_lower = query.lower().strip()

        # Exact match
        if query_lower in self.name_to_id:
            return self.name_to_id[query_lower], query

        # Fuzzy match with difflib (Levenshtein distance)
        recipe_names = list(self.name_to_id.keys())
        matches = get_close_matches(query_lower, recipe_names, n=max_suggestions)

        if matches:
            return None, matches  # Return suggestions
        else:
            return None, []

    def get_avg_recipe_rating(self, recipe_id: int):
        return self.id_to_rating.get(recipe_id)

    def calculate_similarity_score(self, normalization_type: int, neighbor: int, recipe_id: int):
        """
        Get the similarity between a recipe id and its neighbor
        0: shared ingredients
        1: shared ingredients / all neighbors ingredients
        2: (shared ingredients / all neighbors ingredients) + (neighbors rating / 5)
        """

        weight = self.graph[recipe_id][neighbor]['weight']

        match normalization_type:
            case 0:  # weight -> nr of shared ingredients
                return weight

            case 1:  # normalized by total nr of ingredients
                neighbor_ingredients = len(self.get_recipe_ingredients(neighbor))
                return weight / neighbor_ingredients

            case 2:  # total nr of ingredients + normalization of rating
                neighbor_ingredients = len(self.get_recipe_ingredients(neighbor))
                similarity = weight / neighbor_ingredients
                rating = self.get_avg_recipe_rating(neighbor)
                return similarity + (rating / 5.0)  # /5 is normalization for rating

            case _:
                return weight

    def get_shared_ingredients(self, recipe_id1: int, recipe_id2: int):
        """Get the list of ingredients shared between two recipes"""
        ingredients_1 = set(self.get_recipe_ingredients(recipe_id1))
        ingredients_2 = set(self.get_recipe_ingredients(recipe_id2))
        return sorted(list(ingredients_1.intersection(ingredients_2)))
    
    def get_instructions(self, recipe_id: int):
        """Returns a list of instructions (steps) for a recipe."""
        return self.recipe_instructions.get(recipe_id, ["No instructions available."])

    def get_minutes(self, recipe_id: int):
        """Returns the estimated time in minutes for a recipe."""
        return self.recipe_minutes.get(recipe_id, 0)

    def get_description(self, recipe_id: int):
        """Returns the description of a recipe."""
        return self.recipe_descriptions.get(recipe_id, "No description available.")

    def recommend_similar_recipes(self, recipe_id: int, top_k: int =10, normalization_type: int=0):
        """
        Get top-k most similar recipes to the given recipe.
        Returned as a JSON array with the following structure:
            'id': neighbor,
            'name': recipe_name,
            'similarity_score': similarity,
            'ingredients': ingredients,
            'shared_ingredients': shared_ingredients,
            'rating': rating,
            'instructions': instructions,
            'minutes': minutes,
            'description': description
        """

        if not recipe_id in self.graph:
            return []

        # Get neighbors with their similarity scores
        neighbors = []
        for neighbor in self.graph.neighbors(recipe_id):
            recipe_name = self.id_to_name.get(neighbor, f"Recipe {neighbor}")
            similarity = self.calculate_similarity_score(normalization_type, neighbor, recipe_id)
            rating = self.get_avg_recipe_rating(neighbor)
            ingredients = self.get_recipe_ingredients(neighbor)
            shared_ingredients = self.get_shared_ingredients(recipe_id, neighbor)
            instructions = self.get_instructions(neighbor)
            minutes = self.get_minutes(neighbor)
            description = self.get_description(neighbor)

            neighbors.append({
                'id': neighbor,
                'name': recipe_name,
                'similarity_score': similarity,
                'ingredients': ingredients,
                'shared_ingredients': shared_ingredients,
                'rating': rating,
                'instructions': instructions,
                'minutes': minutes,
                'description': description
            })

        # Sort by similarity score and return top-k
        neighbors.sort(key=lambda x: x['similarity_score'], reverse=True)
        return neighbors[:top_k]


class RecipeRecommender():

    def __init__(self, graph_manager: GraphManager):
        self.graph_manager: GraphManager = graph_manager
        self.nr_of_recomms: int = 10
        self.norm_type: int = 1

    def set_config_values(self, nr_of_recomms=None, norm_type=None):
        """Set number of recommendations and the default normalization type"""
        self.nr_of_recomms = nr_of_recomms
        if not nr_of_recomms:  # both None and 0 would be bad
            self.nr_of_recomms = int(input("How many similar recipes do you want to get? People usually choose 10 😁"))

        self.norm_type = norm_type
        if norm_type == None:
            self.norm_type = int(input("How would you like me to evaluate similarity? 0: num of shared ingredients, 1: normalized num of ingredients, 2: top secret special algorithm for best rated similar recipes "))

    def command_line_interaction(self, query=None, cur_norm_type=None):
        """
        Start an interactive search for recipes neighbors.
        Can be started without interaction if a query is provided.
        norm_type the normalization type is optional.
        """

        # Find recipe
        if query is None:
            query = input("Which recipe do you want to replace today?")

        if cur_norm_type == None:  # if no custom norm type use set one
            cur_norm_type = self.norm_type

        result = self.graph_manager.find_recipe_by_name(query)

        if isinstance(result[0], int):  # exact match found = first result item is the recipe_id
            recipe_id, recipe_name = result
            print(f"🍽️ Found recipe: {self.graph_manager.id_to_name[recipe_id]}")

            # Show ingredients
            ingredients = self.graph_manager.get_recipe_ingredients(recipe_id)
            print(f"\nIngredients ({len(ingredients)}):")
            print(", ".join(sorted(ingredients)))

            # Get recommendations
            recommendations = self.graph_manager.recommend_similar_recipes(recipe_id, top_k=self.nr_of_recomms, normalization_type=cur_norm_type)

            if recommendations:
                print(f"\nTop {len(recommendations)} Similar Recipes:")
                print("-" * 80)

                for i, rec in enumerate(recommendations, 1):
                    print(f"{i:2d}. {rec['name']}")
                    print(f"    Number of shared ingredients: {len(rec['shared_ingredients'])}")
                    print(f"    Shared ingredients: {', '.join(rec['shared_ingredients'])}")
                    if rec['rating'] > 0:
                        print(f"    Rating: {rec['rating']:.1f}/5.0")
                    print(f"    Total ingredients: {len(rec['ingredients'])}")
                    print()
            else:
                print("❌ No similar recipes found in the graph.")

        elif result[1]:  # no exact match but suggestions found
            print(f"❓ Recipe '{query}' not found exactly. Did you mean:")
            for i, suggestion in enumerate(result[1], 1):
                print(f"{i}. {suggestion.title()}")
            print("\nTry searching with one of these suggestions.")

        else:
            print(f"❌ No recipes found matching '{query}'")

graph_manager = GraphManager(nrows=5000, debug=False)
recipe_recommender = RecipeRecommender(graph_manager)

