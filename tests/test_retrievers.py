import pytest
from unittest.mock import patch, MagicMock
from chefkoch import DailyRecipeRetriever, RandomRetriever, SearchRetriever, Recipe


def test_random_retriever_get_recipes_single():
    retriever = RandomRetriever()
    recipes = retriever.get_recipes(2)
    assert len(recipes) == 2
    assert recipes[0].url.startswith("https://www.chefkoch.de/rezepte/")


def test_random_retriever_get_recipe():
    retriever = RandomRetriever()
    recipe = retriever.get_recipe()
    assert recipe.url.startswith("https://www.chefkoch.de/rezepte/")

def test_random_retriever_skips_plus_recipes():
    """
    Tests that RandomRetriever retries and successfully returns a non-Plus recipe.
    Mocks the Recipe initialization to simulate finding a Plus recipe on the first attempt.
    """
    # Create mock recipes
    mock_plus_recipe = MagicMock(spec=Recipe)
    mock_plus_recipe.is_plus_recipe = True
    mock_plus_recipe.url = "https://www.chefkoch.de/rezepte/4168421666771617/Lammschulter-in-Wermutfond.html"

    mock_valid_recipe = MagicMock(spec=Recipe)
    mock_valid_recipe.is_plus_recipe = False
    mock_valid_recipe.url = "https://www.chefkoch.de/rezepte/40231013521154/Bulettentopf-mit-Wirsing.html"

    # Configure mock `Recipe` class to return Plus, then Valid on consecutive calls
    with patch('chefkoch.retrievers.Recipe') as MockRecipe:
        MockRecipe.side_effect = [
            mock_plus_recipe,  # Attempt 1 returns Plus
            mock_valid_recipe  # Attempt 2 returns Valid (should succeed here)
        ]

        retriever = RandomRetriever()

        # We also mock the session.get to prevent actual HTTP calls during the test
        with patch.object(retriever.session, 'get') as mock_get:
            # The URL doesn't matter much here, as the Recipe mock controls the result
            mock_get.return_value = MagicMock(url="https://www.chefkoch.de/rezepte/simulated")

            recipe = retriever.get_recipe()

            # Assertions
            assert recipe.is_plus_recipe == False
            assert recipe.url == "https://www.chefkoch.de/rezepte/40231013521154/Bulettentopf-mit-Wirsing.html"

            # Check if two actual recipe object creations were attempted
            assert MockRecipe.call_count == 2

            # Check that the URL was fetched twice (once for the blocked, once for the valid)
            assert mock_get.call_count == 2

        retriever.close()

def test_random_retriever_max_retries_exceeded():
    """
    Tests that RandomRetriever raises an exception after exceeding max_retries (3 attempts).
    """
    # Create a mock for a Plus recipe
    mock_plus_recipe = MagicMock(spec=Recipe)
    mock_plus_recipe.is_plus_recipe = True

    # Configure mock `Recipe` class to always return Plus
    with patch('chefkoch.retrievers.Recipe') as MockRecipe:
        MockRecipe.return_value = mock_plus_recipe

        retriever = RandomRetriever()

        # We mock the session.get as well
        with patch.object(retriever.session, 'get') as mock_get:
            mock_get.return_value = MagicMock(url="https://www.chefkoch.de/rezepte/simulated")

            # Expect an exception to be raised because maximum retries (3) were exhausted
            with pytest.raises(Exception, match=r"Failed to retrieve a non-Plus random recipe after 3 attempts."):
                retriever.get_recipe()

            # Check that 3 calls were made to both Recipe constructor and session.get
            assert MockRecipe.call_count == 3
            assert mock_get.call_count == 3

        retriever.close()


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
