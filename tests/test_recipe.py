import datetime
import isodate
import pytest
from chefkoch.recipe import Recipe

# URL for a recipe in the "old" chefkoch.de format
URL_OLD = "https://www.chefkoch.de/rezepte/745721177147257/Lasagne.html"
ID_OLD = "745721177147257"

# URL for a recipe in the "new" Next.js-based format
URL_NEW = "https://www.chefkoch.de/rezepte/4267801700467824/Frikadellen-aus-der-Heissluftfritteuse.html"
ID_NEW = "4267801700467824"

# URL for a Chefkoch Plus recipe (provided by user example HTML)
URL_PLUS = "https://www.chefkoch.de/rezepte/4168421666771617/Lammschulter-in-Wermutfond.html"
ID_PLUS = "4168421666771617"


@pytest.fixture(scope="module")
def recipe_old():
    """Fixture for a recipe in the old format."""
    return Recipe(url=URL_OLD)


@pytest.fixture(scope="module")
def recipe_new():
    """Fixture for a recipe in the new format."""
    return Recipe(url=URL_NEW)

@pytest.fixture(scope="module")
def recipe_plus():
    """Fixture for a Chefkoch Plus recipe."""
    return Recipe(url=URL_PLUS)


def get_total_seconds(duration):
    """Helper to get total seconds from isodate.Duration or timedelta."""
    if isinstance(duration, isodate.duration.Duration):
        return duration.td.total_seconds()
    if isinstance(duration, datetime.timedelta):
        return duration.total_seconds()
    return 0


def test_init_from_id():
    """Test if recipes can be initialized from their ID."""
    recipe_old_from_id = Recipe(id=ID_OLD)
    assert recipe_old_from_id.title == "Lasagne"

    recipe_new_from_id = Recipe(id=ID_NEW)
    assert recipe_new_from_id.title == "Frikadellen aus der Heißluftfritteuse"


def test_old_format_attributes(recipe_old: Recipe):
    """Test attributes of a recipe in the old page format."""
    assert recipe_old.title == "Lasagne"
    assert not recipe_old.is_plus_recipe

    assert isinstance(recipe_old.ingredients, list)
    assert len(recipe_old.ingredients) > 0
    assert any("hackfleisch" in ing.lower() for ing in recipe_old.ingredients)

    assert isinstance(recipe_old.instructions, str)
    assert len(recipe_old.instructions) > 0

    assert isinstance(recipe_old.image_url, str)
    assert recipe_old.image_url.startswith("https://")

    # Time properties can be None, isodate.Duration or timedelta, so check for all
    assert isinstance(recipe_old.prep_time, (isodate.duration.Duration, datetime.timedelta, type(None)))
    assert isinstance(recipe_old.cook_time, (isodate.duration.Duration, datetime.timedelta, type(None)))
    assert isinstance(recipe_old.rest_time, (isodate.duration.Duration, datetime.timedelta, type(None)))
    assert isinstance(recipe_old.total_time, (isodate.duration.Duration, datetime.timedelta, type(None)))

    # The sum of components should roughly match total if all are present
    if recipe_old.prep_time and recipe_old.cook_time and recipe_old.total_time:
        # Give some leeway for calculated totals vs scraped totals
        prep_seconds = get_total_seconds(recipe_old.prep_time)
        cook_seconds = get_total_seconds(recipe_old.cook_time)
        total_seconds = get_total_seconds(recipe_old.total_time)

        calculated_seconds = prep_seconds + cook_seconds
        assert abs(total_seconds - calculated_seconds) < 60

    assert isinstance(recipe_old.difficulty, str)
    assert recipe_old.difficulty in ["simpel", "normal", "pfiffig", "unknown"]

    assert isinstance(recipe_old.author, str) and recipe_old.author

    assert isinstance(recipe_old.servings, (int, type(None)))

    assert isinstance(recipe_old.calories, str)

    assert isinstance(recipe_old.rating, float)
    assert recipe_old.rating >= 0.0

    assert isinstance(recipe_old.number_ratings, int)
    assert recipe_old.number_ratings >= 0


def test_new_format_attributes(recipe_new: Recipe):
    """Test attributes of a recipe in the new page format."""
    assert recipe_new.title == "Frikadellen aus der Heißluftfritteuse"
    assert not recipe_new.is_plus_recipe

    assert isinstance(recipe_new.ingredients, list)
    assert len(recipe_new.ingredients) > 0
    assert any("zwiebel" in ing.lower() for ing in recipe_new.ingredients)

    assert isinstance(recipe_new.instructions, str)
    # Changed "braten" to "garen" as it's actually in the text
    assert "garen" in recipe_new.instructions.lower()

    assert isinstance(recipe_new.image_url, str)
    assert recipe_new.image_url.startswith("https://img.chefkoch-cdn.de/")

    # Check against timedelta as well for consistency
    assert isinstance(recipe_new.prep_time, (isodate.duration.Duration, datetime.timedelta))
    assert get_total_seconds(recipe_new.prep_time) == 15 * 60

    assert isinstance(recipe_new.cook_time, (isodate.duration.Duration, datetime.timedelta))

    assert isinstance(recipe_new.rest_time, (isodate.duration.Duration, datetime.timedelta, type(None)))

    assert isinstance(recipe_new.total_time, (isodate.duration.Duration, datetime.timedelta))
    # The sum of components should roughly match total if all are present
    if recipe_new.prep_time and recipe_new.cook_time and recipe_new.total_time:
        prep_seconds = get_total_seconds(recipe_new.prep_time)
        cook_seconds = get_total_seconds(recipe_new.cook_time)
        total_seconds = get_total_seconds(recipe_new.total_time)

        calculated_seconds = prep_seconds + cook_seconds
        assert abs(total_seconds - calculated_seconds) < 60

    assert recipe_new.difficulty == "simpel"

    assert recipe_new.author == "princess_bambi"

    assert isinstance(recipe_new.servings, int)
    assert recipe_new.servings > 0

    assert isinstance(recipe_new.calories, str)
    assert "kcal" in recipe_new.calories

    assert isinstance(recipe_new.rating, float)
    assert recipe_new.rating > 0.0

    assert isinstance(recipe_new.number_ratings, int)
    assert recipe_new.number_ratings > 0

def test_plus_recipe_is_blocked(recipe_plus: Recipe):
    """Test attributes for a blocked Chefkoch Plus recipe."""
    assert recipe_plus.is_plus_recipe == True
    assert recipe_plus.title == "Chefkoch Plus Recipe (Content Blocked)"
    assert recipe_plus.difficulty == "blocked"
    assert recipe_plus.ingredients == ["Content blocked (Chefkoch Plus)"]
    assert recipe_plus.instructions == "Content blocked (Chefkoch Plus)"
    assert recipe_plus.author == "Unbekannt (Chefkoch Plus)"
    assert recipe_plus.calories == "k.A. (Chefkoch Plus)"
    assert recipe_plus.rating == 0.0
    assert recipe_plus.number_ratings == 0
    assert recipe_plus.servings is None
    assert recipe_plus.prep_time is None
