import datetime
import isodate

from chefkoch import Recipe

# Example URL with the new page structure
NEW_STRUCTURE_URL = "https://www.chefkoch.de/rezepte/761171178862026/Erdnuss-Hackbaellchen-in-Currysauce.html"


def test_from_url():
    """Tests recipe initialization from a URL."""
    recipe = Recipe(url=NEW_STRUCTURE_URL)
    assert recipe is not None
    assert recipe.id == "761171178862026"


def test_from_id():
    """Tests recipe initialization from an ID."""
    recipe = Recipe(id="761171178862026")
    assert recipe is not None
    assert recipe.url == "https://www.chefkoch.de/rezepte/761171178862026"


def test_new_structure_attributes():
    """Tests if attributes are correctly scraped from the new page structure."""
    recipe = Recipe(url=NEW_STRUCTURE_URL)

    assert recipe.title == "Erdnuss-Hackbällchen in Currysauce"
    assert isinstance(recipe.title, str)

    assert "Zwiebel(n)" in recipe.ingredients
    assert isinstance(recipe.ingredients, list)

    assert recipe.instructions
    assert isinstance(recipe.instructions, list)
    assert isinstance(recipe.instructions[0], str)

    assert recipe.image_url.startswith("https://img.chefkoch-cdn.de/")
    assert isinstance(recipe.image_url, str)

    assert isinstance(recipe.image_urls, list)
    assert recipe.image_urls[0].startswith("https://img.chefkoch-cdn.de/")

    assert isinstance(recipe.image_base64, bytes)

    assert recipe.date_published == datetime.datetime(2007, 10, 16)
    assert isinstance(recipe.date_published, datetime.datetime)

    assert recipe.prep_time == isodate.parse_duration("PT20M")
    assert isinstance(recipe.prep_time, isodate.duration.Duration)

    assert recipe.cook_time == isodate.parse_duration("PT25M")
    assert isinstance(recipe.cook_time, isodate.duration.Duration)

    assert recipe.total_time == isodate.parse_duration("PT45M")
    assert isinstance(recipe.total_time, isodate.duration.Duration)

    assert recipe.difficulty == "simpel"
    assert isinstance(recipe.difficulty, str)

    assert recipe.author == "saeva"
    assert isinstance(recipe.author, str)

    assert "Hauptspeise" in recipe.category
    assert isinstance(recipe.category, str)

    assert recipe.calories == "834 kcal"

    assert recipe.rating > 0
    assert isinstance(recipe.rating, float)

    assert recipe.number_ratings > 0
    assert isinstance(recipe.number_ratings, int)
