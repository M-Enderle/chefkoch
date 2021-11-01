# chefkoch_api
[![Downloads](https://pepy.tech/badge/chefkoch_api)](https://pepy.tech/project/chefkoch_api)

Python library to retrieve data from chefkoch.de

## Installation
Use the package manager [pip](https://pypi.org/) to install [chefkoch_api](https://pypi.org/project/chefkoch_api/)
```
pip install chefkoch_api
```

## Examples:

#### Retrieving daily recommendations
```python
from chefkoch_api import chefkoch

recipes = chefkoch.get_daily_recommendations(category="backe")

for recipe in recipes:
    print("\n" + str(recipe))
```

#### Retrieving a random recipe
```python
from chefkoch_api import chefkoch

recipe = chefkoch.get_random_recipe()
print(recipe.modify_portions(portions=6))

for step in recipe.steps:
    print("Next -> " + step)
```

#### Searching for a specific recipe with filter
```python
from chefkoch_api import chefkoch

print(chefkoch.get_specifications())
recipes = chefkoch.search(search_term="Lasagne",
                          filters={"page": 2, "sort": "rating", "duration": 30,
                                            "difficulty": {"easy": True, "medium": True, "hard": False}},
                          specifications=["vegetarisch", "gemuese"])
print(recipes)
```

## Recipe interactions

|name               |type      |description                                                                         |
|-------------------|----------|------------------------------------------------------------------------------------|
|get_next_step      |method    |returns the next step of the recipe. Throws EndOfRecipeError when the end is reached|
|modify_portions    |method    |modifies the portions and returns the new dict for ingredients                      |
|info_dict          |attribute |contains all information retrived directly from javascript from the chefkoch page   |
|ingredients        |attribute |dictionary with ingredients as key and the amount as values. Everything is a string |
|steps              |attribute |list with all steps. Simply the instruction text split by '.'                       |
|image              |attribute |hyper-link to the main image                                                        |
|...                |attributes|more attributes available that are self-explainatory                                |

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
