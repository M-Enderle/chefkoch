""" This module provides a class to scrape recipes from chefkoch.de """

import datetime
import json
from functools import cached_property
from typing import List, Optional, Union, Dict, Any

import isodate
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.chefkoch.de/rezepte"


class Recipe:
    """
    Represents a recipe from the Chefkoch website.
    Supports both old and new page layouts.
    """

    def __init__(self, url: Optional[str] = None, id: Optional[str] = None):
        """
        Initializes a Recipe object.

        Args:
            url (str, optional): The URL of the recipe. Defaults to None.
            id (str, optional): The ID of the recipe. Defaults to None.

        Raises:
            ValueError: If neither url nor id is provided.
            ValueError: If the url is invalid.
        """
        if url is None and id is None:
            raise ValueError("Either url or id must be provided")

        if id is not None:
            url = f"{BASE_URL}/{id}"

        if not url.startswith(BASE_URL):
            raise ValueError("Invalid url")

        self.url: str = url

        if id is None:
            try:
                # Extracts the numeric ID from the URL path
                id_part = url.split("/")[4]
                self.id: str = id_part
            except IndexError:
                raise ValueError("Could not extract recipe ID from URL.")
        else:
            self.id = id


    @cached_property
    def __soup(self) -> BeautifulSoup:
        """
        Returns the BeautifulSoup object of the recipe's webpage.
        """
        response = requests.get(self.url)
        response.raise_for_status() # Raise an exception for bad status codes
        return BeautifulSoup(response.content, "html.parser")

    @cached_property
    def __is_new_format(self) -> bool:
        """Checks if the recipe page uses the new Next.js format."""
        return bool(self.__soup.find("script", id="__NEXT_DATA__"))

    @cached_property
    def __recipe_data(self) -> Dict[str, Any]:
        """
        Extracts recipe data from the page's JSON scripts.
        It supports both the new Next.js format (from __NEXT_DATA__)
        and the old format (from JSON-LD).
        """
        if self.__is_new_format:
            next_data_script = self.__soup.find("script", id="__NEXT_DATA__")
            if next_data_script and next_data_script.string:
                data = json.loads(next_data_script.string)
                page_props = data.get("props", {}).get("pageProps", {})
                recipe_data = page_props.get("recipe") or page_props.get("initialRecipe")
                if recipe_data:
                    return recipe_data

        # Fallback to old format: find the JSON-LD script with recipe info
        all_json_ld_scripts = self.__soup.find_all("script", type="application/ld+json")
        for script in all_json_ld_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    # Data can be a single object or in a @graph list
                    if isinstance(data, dict) and data.get("@type") == "Recipe":
                        return data
                    if isinstance(data, dict) and "@graph" in data:
                        for item in data.get("@graph", []):
                            if isinstance(item, dict) and item.get("@type") == "Recipe":
                                return item
            except (json.JSONDecodeError, AttributeError):
                continue

        raise ValueError("Could not find recipe JSON data on the page.")

    @cached_property
    def title(self) -> str:
        """Returns the title of the recipe."""
        # The 'title' key is used in the new format, 'name' in the old one.
        return self.__recipe_data.get("title") or self.__recipe_data.get("name") or "Titel nicht gefunden"

    @cached_property
    def image_url(self) -> str:
        """Returns the URL of the recipe's main image."""
        if self.__is_new_format:
            image_info = self.__recipe_data.get("image", {})
            if image_info and "url" in image_info:
                return image_info["url"]

        # Fallback for old format or if new format URL is missing
        image_data = self.__recipe_data.get("image")
        if isinstance(image_data, list) and image_data:
            return image_data[0]
        if isinstance(image_data, str):
            return image_data

        # Fallback to scraping the amp-img tag
        image_tag = self.__soup.find("amp-img")
        if image_tag and image_tag.find("img"):
            return image_tag.find("img")["src"]

        raise ValueError("Image not found")

    @cached_property
    def image_base64(self) -> bytes:
        """Returns the raw bytes of the recipe's main image."""
        response = requests.get(self.image_url)
        response.raise_for_status()
        return response.content

    @cached_property
    def image_urls(self) -> List[str]:
        """Returns the URLs of all images associated with the recipe."""
        response = requests.get(f"{BASE_URL}/bilderuebersicht/{self.id}")
        if not response.ok:
            return []
        image_soup = BeautifulSoup(response.content, "html.parser")
        image_div = image_soup.find("div", {"class": "recipe-images"})
        if image_div:
            return [img["src"] for img in image_div.find_all("amp-img")]
        return []

    @cached_property
    def date_published(self) -> datetime.datetime:
        """Returns the date when the recipe was published."""
        if self.__is_new_format:
            date_string = self.__recipe_data.get("createdAt") # e.g., "2022-11-23T09:27:04.288Z"
            if date_string:
                if date_string.endswith('Z'):
                    date_string = date_string[:-1] + '+00:00'
                return datetime.datetime.fromisoformat(date_string)
        else:
            date_string = self.__recipe_data.get("datePublished") # e.g., "2014-04-13"
            if date_string:
                return datetime.datetime.strptime(date_string, "%Y-%m-%d")

        raise ValueError("Publication date not found.")

    def _parse_duration(self, time_val: Optional[Union[str, int]]) -> Optional[isodate.Duration]:
        """Helper to parse duration from either ISO string (e.g., 'PT15M') or minutes (e.g., 15)."""
        if time_val is None:
            return None
        if isinstance(time_val, int):
            return isodate.parse_duration(f"PT{time_val}M")
        if isinstance(time_val, str) and time_val:
            return isodate.parse_duration(time_val)
        return None

    @cached_property
    def prep_time(self) -> Optional[isodate.Duration]:
        """Returns the preparation time of the recipe."""
        return self._parse_duration(self.__recipe_data.get("prepTime"))

    @cached_property
    def cook_time(self) -> Optional[isodate.Duration]:
        """Returns the cooking time of the recipe."""
        return self._parse_duration(self.__recipe_data.get("cookTime"))

    @cached_property
    def total_time(self) -> Optional[isodate.Duration]:
        """Returns the total time required to prepare the recipe."""
        return self._parse_duration(self.__recipe_data.get("totalTime"))

    @cached_property
    def difficulty(self) -> str:
        """Returns the difficulty level of the recipe."""
        if self.__is_new_format:
            diff_map = {"SIMPLE": "simpel", "NORMAL": "normal", "ADVANCED": "pfiffig"}
            difficulty_key = self.__recipe_data.get("difficulty")
            return diff_map.get(difficulty_key, "unklar")

        # Fallback for old format
        difficulty_tag = self.__soup.find("span", {"class": "recipe-difficulty"})
        if difficulty_tag and difficulty_tag.text:
            return difficulty_tag.text.strip().split()[-1]

        return "unklar"

    @cached_property
    def ingredients(self) -> List[str]:
        """Returns the list of ingredients required for the recipe."""
        if self.__is_new_format:
            ingredients_list = []
            for group in self.__recipe_data.get("ingredientGroups", []):
                for ingredient in group.get("ingredients", []):
                    parts = [
                        str(ingredient["amount"]) if ingredient.get("amount") is not None and ingredient.get("amount") > 0 else "",
                        ingredient.get("unit", ""),
                        ingredient.get("name", ""),
                    ]
                    ingredients_list.append(" ".join(filter(None, parts)).strip())
            return ingredients_list

        return self.__recipe_data.get("recipeIngredient", [])

    @cached_property
    def instructions(self) -> str:
        """Returns the preparation instructions as a single string."""
        if self.__is_new_format:
            return self.__recipe_data.get("instructions", "")

        # Old format instructions can be a list of steps or a plain string
        instruction_data = self.__recipe_data.get("recipeInstructions", [])
        if isinstance(instruction_data, list):
            texts = [step.get("text", "") for step in instruction_data if isinstance(step, dict)]
            return "\n".join(texts)
        elif isinstance(instruction_data, str):
            return instruction_data

        return ""

    @cached_property
    def author(self) -> str:
        """Returns the name of the author of the recipe."""
        if self.__is_new_format:
            return self.__recipe_data.get("author", {}).get("username", "Unbekannt")

        author_data = self.__recipe_data.get("author", {})
        if isinstance(author_data, list) and author_data:
            return author_data[0].get("name", "Unbekannt")
        if isinstance(author_data, dict):
            return author_data.get("name", "Unbekannt")

        return "Unbekannt"

    @cached_property
    def publisher(self) -> str:
        """Returns the name of the publisher. For Chefkoch, this is usually the author."""
        if self.__is_new_format:
            return self.author

        return self.__recipe_data.get("publisher", {}).get("name", self.author)

    @cached_property
    def calories(self) -> str:
        """Returns the calories of the recipe as a string (e.g., '432 kcal')."""
        nutrition = self.__recipe_data.get("nutrition", {})
        if self.__is_new_format:
            return nutrition.get("nutrients", {}).get("calories", "k.A.")

        return nutrition.get("calories", "k.A.")

    @cached_property
    def keywords(self) -> List[str]:
        """Returns the keywords (tags) associated with the recipe."""
        if self.__is_new_format:
            return self.__recipe_data.get("tags", [])

        keywords_str = self.__recipe_data.get("keywords", "")
        return [k.strip() for k in keywords_str.split(",")] if keywords_str else []

    @cached_property
    def _aggregate_rating(self) -> Dict[str, Any]:
        """Helper to get rating block from either format."""
        if self.__is_new_format:
            return self.__recipe_data.get("rating", {})
        return self.__recipe_data.get("aggregateRating", {})

    @cached_property
    def number_reviews(self) -> int:
        """Returns the number of reviews for the recipe."""
        rating_data = self._aggregate_rating
        # New format uses 'count', old uses 'reviewCount'
        return int(rating_data.get("count", rating_data.get("reviewCount", 0)))

    @cached_property
    def number_ratings(self) -> int:
        """Returns the number of ratings for the recipe."""
        rating_data = self._aggregate_rating
        # New format uses 'numRatings', old uses 'ratingCount'
        return int(rating_data.get("numRatings", rating_data.get("ratingCount", 0)))

    @cached_property
    def rating(self) -> float:
        """Returns the average rating of the recipe."""
        rating_data = self._aggregate_rating
        # New format uses 'average', old uses 'ratingValue'
        return float(rating_data.get("average", rating_data.get("ratingValue", 0.0)))

    @cached_property
    def category(self) -> str:
        """Returns the category of the recipe."""
        if self.__is_new_format:
            # The new format uses tags; the first tag can be considered the main category.
            tags = self.keywords
            return tags[0] if tags else "Unkategorisiert"

        return self.__recipe_data.get("recipeCategory", "Unkategorisiert")
