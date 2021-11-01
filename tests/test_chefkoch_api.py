from chefkoch_api import chefkoch

print(chefkoch.get_specifications())
recipes = chefkoch.search(search_term="Lasagne",
                          filters={"page": 2, "sort": "rating", "duration": 30,
                                   "difficulty": {"easy": True, "medium": True, "hard": False}},
                          specifications=["vegetarisch", "gemuese"])
print(recipes)
