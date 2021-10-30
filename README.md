# chefkoch-api
[![Downloads](https://pepy.tech/badge/chefkoch_api)](https://pepy.tech/project/chefkoch_api)

Python library to retrieve data from chefkoch.de

## Installation
```
pip install chefkoch_api
```

## Examples:

```python
from chefkoch_api import chefkoch

recipes = chefkoch.get_daily_recommendations(category="backe")

for recipe in recipes:
    print("\n" + str(recipe))
```

```python
from chefkoch_api import chefkoch

recipe = chefkoch.get_random_recipe()
print(recipe.modify_portions(portions=6))

for step in recipe.steps:
    print("Next -> " + step)
```

```python
from chefkoch_api import chefkoch

print(chefkoch.get_specifications())
recipes = chefkoch.get_specific(search_term="Lasagne",
                                filters={"page": 2, "sort": "rating", "duration": 30,
                                                    "difficulty": {"easy": True, "medium": True, "hard": False}},
                                specifications=["vegetarisch", "gemuese"])
print(recipes)
```
