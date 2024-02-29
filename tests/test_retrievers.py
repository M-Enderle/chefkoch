from chefkoch import DailyRecipeRetriever, RandomRetriever, SearchRetriever


def test_random_retriever_get_recipes_single():
    retriever = RandomRetriever()
    recipes = retriever.get_recipes(2)
    assert len(recipes) == 2
    assert recipes[0].url.startswith("https://www.chefkoch.de/rezepte/")


def test_random_retriever_get_recipe():
    retriever = RandomRetriever()
    recipe = retriever.get_recipe()
    assert recipe.url.startswith("https://www.chefkoch.de/rezepte/")


def test_search_retriever_get_recipe_valid_kuchen():
    retriever = SearchRetriever()
    recipes = retriever.get_recipes("Kuchen")
    assert len(recipes) > 0
    for recipe in recipes:
        assert recipe.url.startswith("https://www.chefkoch.de/rezepte/")


def test_search_retriever_get_recipe_valid_salat():
    retriever = SearchRetriever()
    recipes = retriever.get_recipes("Salat")
    assert len(recipes) > 0
    for recipe in recipes:
        assert recipe.url.startswith("https://www.chefkoch.de/rezepte/")


def test_search_retriever_get_with_filter():
    retriever = SearchRetriever(health=["vegan"])
    recipes = retriever.get_recipes("Kuchen")
    assert len(recipes) > 0
    for recipe in recipes:
        assert recipe.url.startswith("https://www.chefkoch.de/rezepte/")


def test_daily_recipe_retriever_get_recipes_cooking():
    retriever = DailyRecipeRetriever()
    recipes = retriever.get_recipes("kochen")
    assert len(recipes) > 0
    for recipe in recipes:
        assert recipe.url.startswith("https://www.chefkoch.de/rezepte/")


def test_daily_recipe_retriever_get_recipes_baking():
    retriever = DailyRecipeRetriever()
    recipes = retriever.get_recipes("backen")
    assert len(recipes) > 0
    for recipe in recipes:
        assert recipe.url.startswith("https://www.chefkoch.de/rezepte/")
