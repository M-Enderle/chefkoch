""" This module contains classes that retrieve recipes from the Chefkoch website. """

from typing import List, Optional

import bs4
import requests

from chefkoch.recipe import Recipe

RANDOM_RECIPE_URL = "https://www.chefkoch.de/rezepte/zufallsrezept/"
DAILY_COOKING_TIP_URL = "https://www.chefkoch.de/rezepte/was-koche-ich-heute/"
DAILY_BAKING_TIP_URL = "https://www.chefkoch.de/rezepte/was-backe-ich-heute/"


class RandomRetriever:
    """
    A class that retrieves random recipes from a source.
    """

    def __init__(self):
        """
        Initializes a RandomRetriever with a requests session for connection reuse.
        """
        self.session = requests.Session()

    def get_recipes(self, n: int = 1) -> Recipe:
        """
        Retrieves a specified number of random recipes.

        Args:
            n (int): The number of recipes to retrieve. Defaults to 1.

        Returns:
            Recipe: The retrieved recipe(s).
        """
        return [self.get_recipe() for _ in range(n)]

    def get_recipe(self) -> Recipe:
        """
        Retrieves a single random recipe.

        Returns:
            Recipe: The retrieved recipe.
        """
        while True:
            try:
                return Recipe(url=self.session.get(RANDOM_RECIPE_URL).url)
            except ValueError:
                continue

    def close(self):
        """
        Closes the session and all adapters.
        """
        self.session.close()


class SearchRetriever:
    """
    SearchRetriever is a class that retrieves recipes from the Chefkoch website based on search criteria.

    Attributes:
        PROPERTIES (List[str]): List of available recipe properties.
        HEALTH (List[str]): List of available health options.
        CATEGORIES (List[str]): List of available recipe categories.
        COUNTRIES (List[str]): List of available countries.
        MEAL_TYPE (List[str]): List of available meal types.
        PREP_TIMES (List[str]): List of available preparation times.
        RATINGS (List[str]): List of available ratings.
        SORT (List[str]): List of available sorting options.

    Args:
        properties (Optional[List[str]]): List of recipe properties to filter by.
        health (Optional[List[str]]): List of health options to filter by.
        categories (Optional[List[str]]): List of recipe categories to filter by.
        countries (Optional[List[str]]): List of countries to filter by.
        meal_type (Optional[List[str]]): List of meal types to filter by.
        prep_times (Optional[str]): Preparation time to filter by. Default is "Alle".
        ratings (Optional[str]): Rating to filter by. Default is "Alle".
        sort (Optional[str]): Sorting option. Default is "Empfehlung".

    Raises:
        ValueError: If any of the provided filter options are invalid.

    Methods:
        get_recipe(search_query: str, page: int = 1) -> Recipe:
            Retrieves recipes based on the search query and filter options.

    """

    PROPERTIES = ["Einfach", "Schnell", "Basisrezepte", "Preiswert"]
    HEALTH = [
        "Vegetarisch",
        "Vegan",
        "Kalorienarm",
        "Low Carb",
        "Ketogen",
        "Paleo",
        "Fettarm",
        "Trennkost",
        "Vollwert",
    ]
    CATEGORIES = [
        "Auflauf",
        "Pizza",
        "Reis- oder Nudelsalat",
        "Salat",
        "Salatdressing",
        "Tarte",
        "Fingerfood",
        "Dips",
        "Saucen",
        "Suppe",
        "Klöße",
        "Brot und Brötchen",
        "Brotspeise",
        "Aufstrich",
        "Süßspeise",
        "Eis",
        "Kuchen",
        "Kekse",
        "Torte",
        "Confiserie",
        "Getränke",
        "Shake",
        "Gewürzmischung",
        "Pasten",
        "Studentenküche",
    ]
    COUNTRIES = [
        "Deutschland",
        "Italien",
        "Spanien",
        "Portugal",
        "Frankreich",
        "England",
        "Osteuropa",
        "Skandinavien",
        "Griechenland",
        "Türkei",
        "Russland",
        "Naher Osten",
        "Asien",
        "Indien",
        "Japan",
        "Amerika",
        "Mexiko",
        "Karibik",
        "Lateinamerika",
        "Afrika",
        "Marokko",
        "Ägypten",
        "Australien",
    ]
    MEAL_TYPE = ["Hauptspeise", "Vorspeise", "Beilage", "Dessert", "Snack", "Frühstück"]
    PREP_TIMES = ["15", "30", "60", "120", "Alle"]
    RATINGS = ["Alle", "2", "3", "4", "Top"]
    SORT = ["Empfehlung", "Bewertung", "Neuheiten"]

    __properties = ["50", "49", "79", "48"]
    __health = ["32", "57", "55", "9948", "9947", "7710", "56", "112", "143"]
    __categories = [
        "30",
        "82",
        "94",
        "15",
        "3669",
        "122",
        "52",
        "35",
        "34",
        "40",
        "166",
        "108",
        "46",
        "51",
        "89",
        "127",
        "92",
        "147",
        "93",
        "157",
        "11",
        "113",
        "313",
        "243",
        "211",
    ]
    __countries = [
        "65",
        "28",
        "43",
        "149",
        "84",
        "117",
        "86",
        "133",
        "44",
        "103",
        "212",
        "163",
        "14",
        "13",
        "148",
        "38",
        "74",
        "95",
        "114",
        "101",
        "131",
        "168",
        "145",
    ]
    __meal_type = ["21", "19", "36", "90", "71", "53"]
    __prep_times = ["15", "30", "60", "120", ""]
    __ratings = ["1", "2", "3", "4", "4.5"]
    __sort = ["2", "3", "6"]

    def __init__(
        self,
        properties: Optional[List[str]] = [],
        health: Optional[List[str]] = [],
        categories: Optional[List[str]] = [],
        countries: Optional[List[str]] = [],
        meal_type: Optional[List[str]] = [],
        prep_times: Optional[str] = "Alle",
        ratings: Optional[str] = "Alle",
        sort: Optional[str] = "Empfehlung",
    ):
        """
        Initializes a SearchRetriever object with the provided filter options.

        Args:
            properties (Optional[List[str]]): List of recipe properties to filter by.
            health (Optional[List[str]]): List of health options to filter by.
            categories (Optional[List[str]]): List of recipe categories to filter by.
            countries (Optional[List[str]]): List of countries to filter by.
            meal_type (Optional[List[str]]): List of meal types to filter by.
            prep_times (Optional[str]): Preparation time to filter by. Default is "Alle".
            ratings (Optional[str]): Rating to filter by. Default is "Alle".
            sort (Optional[str]): Sorting option. Default is "Empfehlung".

        Raises:
            ValueError: If any of the provided filter options are invalid.
        """
        # Initialize requests session for connection reuse
        self.session = requests.Session()

        self._properties = [prop.capitalize() for prop in properties]
        self._health = [health.capitalize() for health in health]
        self._categories = [category.capitalize() for category in categories]
        self._countries = [country.capitalize() for country in countries]
        self._meal_type = [meal.capitalize() for meal in meal_type]
        self._prep_times = prep_times
        self._ratings = ratings
        self._sort = sort

        self.__validate()

    def __validate(self):
        """
        Validates the provided filter options.

        Raises:
            ValueError: If any of the provided filter options are invalid.
        """

        if self._properties and not all(
            prop in self.PROPERTIES for prop in self._properties
        ):
            raise ValueError("Invalid property")

        if self._health and not all(health in self.HEALTH for health in self._health):
            raise ValueError("Invalid health")

        if self._categories and not all(
            category in self.CATEGORIES for category in self._categories
        ):
            raise ValueError("Invalid category")

        if self._countries and not all(
            country in self.COUNTRIES for country in self._countries
        ):
            raise ValueError("Invalid country")

        if self._meal_type and not all(
            meal_type in self.MEAL_TYPE for meal_type in self._meal_type
        ):
            raise ValueError("Invalid meal type")

        if self._prep_times and not self._prep_times in self.PREP_TIMES:
            raise ValueError("Invalid prep time")

        if self._ratings and not self._ratings in self.RATINGS:
            raise ValueError("Invalid rating")

        if self._sort and not self._sort in self.SORT:
            raise ValueError("Invalid sort")

    def __convert_list_to_string(self, lst: List[str]) -> str:
        """
        Converts a list of strings to a single string.

        Args:
            lst (List[str]): List of strings.

        Returns:
            str: Converted string.
        """
        return (
            str(lst).replace("[", "").replace("]", "").replace(" ", "").replace("'", "")
        )

    def get_recipes(self, search_query: str, page: int = 1) -> Recipe:
        """
        Retrieves recipes based on the search query and filter options.

        Args:
            search_query (str): Search query for recipes.
            page (int): Page number of the search results. Default is 1.

        Returns:
            Recipe: List of Recipe objects.

        """
        prep_time = self.__prep_times[self.PREP_TIMES.index(self._prep_times)]
        rating = self.__ratings[self.RATINGS.index(self._ratings)]
        sort = self.__sort[self.SORT.index(self._sort)]

        properties = (
            [self.__properties[self.PROPERTIES.index(prop)] for prop in self._properties]
            if self._properties
            else []
        )
        health = (
            [self.__health[self.HEALTH.index(health)] for health in self._health]
            if self._health
            else []
        )
        categories = (
            [
                self.__categories[self.CATEGORIES.index(category)]
                for category in self._categories
            ]
            if self._categories
            else []
        )
        countries = (
            [
                self.__countries[self.COUNTRIES.index(country)]
                for country in self._countries
            ]
            if self._countries
            else []
        )
        meal_type = (
            [
                self.__meal_type[self.MEAL_TYPE.index(meal_type)]
                for meal_type in self._meal_type
            ]
            if self._meal_type
            else []
        )

        combined_string = "t" + self.__convert_list_to_string(
            properties + health + categories + countries + meal_type
        )

        url = f"https://www.chefkoch.de/rs/s{page-1}{combined_string}p{prep_time}r{rating}o{sort}/{search_query}/Rezepte.html"

        result = self.session.get(url).text
        soup = bs4.BeautifulSoup(result, "html.parser")

        recipe_cards = soup.find_all("div", {"class": "ds-recipe-card"})
        recipe_links = [card.find("a") for card in recipe_cards]
        recipes = [Recipe(url=link["href"], allow_premium=True) for link in recipe_links]
        return [recipe for recipe in recipes if not recipe.is_premium]

    def close(self):
        """
        Closes the session and all adapters.
        """
        self.session.close()


class DailyRecipeRetriever:
    """
    A class that retrieves daily recipes from Chefkoch website.

    Attributes:
        None

    Methods:
        get_recipes(type: str) -> List[Recipe]: Retrieves daily recipes based on the specified type.

    """

    def __init__(self):
        """
        Initializes a DailyRecipeRetriever with a requests session for connection reuse.
        """
        self.session = requests.Session()

    def get_recipes(self, type: str) -> List[Recipe]:
        """
        Retrieves daily recipes based on the specified type.

        Args:
            type (str): The type of recipes to retrieve. Must be either 'kochen' or 'backen'.

        Returns:
            List[Recipe]: A list of Recipe objects representing the retrieved recipes.

        Raises:
            ValueError: If the specified type is invalid.

        """
        if type == "kochen":
            url = DAILY_COOKING_TIP_URL
        elif type == "backen":
            url = DAILY_BAKING_TIP_URL
        else:
            raise ValueError("Invalid type. Must be 'kochen' or 'backen'")

        response = self.session.get(url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        recipe_links = soup.find_all("a", {"class": "ds-recipe-card__link"})
        recipe_links = [
            link
            for link in recipe_links
            if link["href"].startswith("https://www.chefkoch.de/rezept")
        ]
        recipes = [Recipe(url=link["href"], allow_premium=True) for link in recipe_links]
        return [recipe for recipe in recipes if not recipe.is_premium]

    def close(self):
        """
        Closes the session and all adapters.
        """
        self.session.close()


if __name__ == "__main__":
    r = DailyRecipeRetriever()
    for _ in range(100):
        recipes = r.get_recipes("kochen")
        for recipe in recipes:
            assert not recipe.is_premium
    r.close()