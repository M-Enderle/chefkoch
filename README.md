# python-chefkoch

[![Downloads](https://static.pepy.tech/badge/python-chefkoch)](https://pepy.tech/project/python-chefkoch)
[![PyPI version](https://badge.fury.io/py/python-chefkoch.svg)](https://badge.fury.io/py/python-chefkoch)

A simple Python retrieval tool for recipes from chefkoch.de

## 🐍 Installation

```bash
$ pip install python-chefkoch
```

## 🚀 Quickstart

```python
from chefkoch import Recipe

recipe = Recipe('https://www.chefkoch.de/rezepte/745721177147257/Lasagne.html')
print(recipe.title)
```

## 🍽️ Recipe attributes

| Attribute          | Type                   | Description                                      |
|--------------------|------------------------|--------------------------------------------------|
| title              | str                    | The title of the recipe.                         |
| image_url          | str                    | The URL of the recipe's image.                    |
| image_base64       | bytes                  | The base64-encoded content of the recipe's image. |
| image_urls         | List[str]              | The URLs of all images associated with the recipe. |
| date_published     | datetime.datetime      | The date when the recipe was published.           |
| prep_time          | isodate.Duration       | The preparation time of the recipe.               |
| cookTime           | isodate.Duration       | The cooking time of the recipe.                   |
| totalTime          | isodate.Duration       | The total time required to prepare the recipe.    |
| difficulty         | str                    | The difficulty level of the recipe.               |
| ingredients        | List[str]              | The list of ingredients required for the recipe.  |
| instructions       | List[str]              | The list of instructions to prepare the recipe.   |
| publisher          | str                    | The name of the publisher of the recipe.          |
| calories           | str                    | The number of calories in the recipe.             |
| keywords           | str                    | The keywords associated with the recipe.          |
| number_reviews     | int                    | The number of reviews for the recipe.             |
| number_ratings     | int                    | The number of ratings for the recipe.             |
| rating             | float                  | The average rating of the recipe.                 |
| category           | str                    | The category of the recipe.                       |

## 🕵️ Retrivers

### RandomRetriever

Retrieves a random recipe from chefkoch.de.

```python
from chefkoch import RandomRetriever

retriever = RandomRetriever()
recipe = retriever.get_recipe()
```

### DailyRecommendationRetriever

Retrieves the daily recommendation from chefkoch.de.

```python
from chefkoch import DailyRecommendationRetriever

retriever = DailyRecommendationRetriever()
recipes = retriever.get_recipes()
```

### SearchRetriever

Allows the use of a search query to retrieve recipes from chefkoch.de.

```python
from chefkoch import SearchRetriever

print(SearchRetriever.HEALTH)
retriever = SearchRetriever(health=["Vegan"])
recipes = retriever.get_recipes()
```

## 💁 Contributing

As an open-source initiative in a rapidly evolving domain, I welcome contributions, be it through the addition of new features or the improvement of existing ones. If you have any suggestions, bug reports, or annoyances, please report them to the issue tracker.

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.