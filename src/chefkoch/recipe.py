""" This module provides a class to scrape recipes from chefkoch.de """

import datetime
import json
from functools import cached_property
from typing import List, Optional, Dict, Any, Union

import isodate
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.chefkoch.de/rezepte"


class Recipe:
    """
    Represents a recipe from Chefkoch website.
    This class scrapes recipe data from a given Chefkoch URL.
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

        if not url.startswith(BASE_URL.rsplit('/', 1)[0]):
            raise ValueError("Invalid url")

        if id is None:
            # Extract ID from URL, works for both old and new URL formats
            id = url.split("/")[4]

        self.url: str = url
        self.id: str = id

    @cached_property
    def __soup(self) -> BeautifulSoup:
        """
        Fetches and parses the HTML content of the recipe URL.
        Returns a BeautifulSoup object.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recipe page: {e}")
            return BeautifulSoup("", "html.parser")

    @cached_property
    def __info_dict(self) -> Dict[str, Any]:
        """
        Finds and parses the JSON-LD script tag containing recipe information.
        Returns the parsed dictionary.
        """
        try:
            scripts = self.__soup.findAll("script", type="application/ld+json")
            # The second JSON-LD script usually contains the recipe details.
            if len(scripts) > 1:
                info_dict_str = scripts[1].text
                return json.loads(info_dict_str)
        except (IndexError, json.JSONDecodeError) as e:
            print(f"Could not parse JSON-LD script: {e}")
        return {}

    @cached_property
    def title(self) -> Optional[str]:
        """Returns the title of the recipe."""
        return self.__info_dict.get("name")

    @cached_property
    def image_url(self) -> Optional[str]:
        """Returns the URL of the recipe's main image."""
        image_data = self.__info_dict.get("image")
        if not image_data:
            return None

        # Image data can be a dictionary or a list of dictionaries
        if isinstance(image_data, list) and image_data:
            return image_data[0].get("url")
        if isinstance(image_data, dict):
            return image_data.get("url")
        return None

    @cached_property
    def image_base64(self) -> Optional[bytes]:
        """Returns the content of the recipe's image as bytes."""
        if not self.image_url:
            return None
        try:
            response = requests.get(self.image_url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recipe image: {e}")
            return None

    @cached_property
    def image_urls(self) -> List[str]:
        """Returns the URLs of all images associated with the recipe from JSON-LD."""
        image_data = self.__info_dict.get("image")
        urls = []
        if not image_data:
            return urls

        image_list = image_data if isinstance(image_data, list) else [image_data]
        for img in image_list:
            if isinstance(img, dict) and img.get("url"):
                urls.append(img["url"])
        return urls


    @cached_property
    def date_published(self) -> Optional[datetime.datetime]:
        """Returns the publication date of the recipe."""
        date_string = self.__info_dict.get("datePublished")
        if date_string:
            return datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return None

    def _parse_duration(self, key: str) -> Optional[isodate.Duration]:
        """Helper to parse ISO 8601 duration strings from the info dict."""
        time_str = self.__info_dict.get(key)
        if time_str:
            try:
                return isodate.parse_duration(time_str)
            except isodate.ISO8601Error:
                return None
        return None

    @cached_property
    def prep_time(self) -> Optional[isodate.Duration]:
        """Returns the preparation time of the recipe."""
        return self._parse_duration("prepTime")

    @cached_property
    def cook_time(self) -> Optional[isodate.Duration]:
        """Returns the cooking time of the recipe."""
        return self._parse_duration("cookTime")

    @cached_property
    def total_time(self) -> Optional[isodate.Duration]:
        """Returns the total time required for the recipe."""
        return self._parse_duration("totalTime")

    @cached_property
    def difficulty(self) -> Optional[str]:
        """Returns the difficulty level of the recipe."""
        difficulty_div = self.__soup.find("div", {"class": "recipe-difficulty"})
        if difficulty_div:
            text_span = difficulty_div.find("span", {"class": "recipe-meta-text"})
            if text_span:
                return text_span.text.strip()
        return None

    @cached_property
    def ingredients(self) -> List[str]:
        """Returns the list of ingredients for the recipe."""
        return self.__info_dict.get("recipeIngredient", [])

    @cached_property
    def instructions(self) -> List[str]:
        """Returns the list of instructions to prepare the recipe."""
        instructions_data = self.__info_dict.get("recipeInstructions", [])
        parsed_instructions = []
        for step in instructions_data:
            if isinstance(step, dict) and step.get("@type") == "HowToStep":
                parsed_instructions.append(step.get("text", "").strip())
            elif isinstance(step, str): # Fallback for plain string instructions
                parsed_instructions.append(step.strip())
        return parsed_instructions

    @cached_property
    def publisher(self) -> Optional[str]:
        """Returns the name of the publisher of the recipe."""
        return self.__info_dict.get("publisher", {}).get("name")

    @cached_property
    def author(self) -> Optional[str]:
        """Returns the name of the author of the recipe."""
        author = self.__info_dict.get("author", {})
        if isinstance(author, dict):
            return author.get("name")
        if isinstance(author, list) and author:
            return author[0].get("name")
        return None

    @cached_property
    def calories(self) -> Optional[str]:
        """Returns the number of calories in the recipe."""
        return self.__info_dict.get("nutrition", {}).get("calories")

    @cached_property
    def keywords(self) -> List[str]:
        """Returns the keywords associated with the recipe."""
        keywords_data = self.__info_dict.get("keywords", "")
        if isinstance(keywords_data, str):
            return [kw.strip() for kw in keywords_data.split(',')]
        if isinstance(keywords_data, list):
            return keywords_data
        return []

    @cached_property
    def aggregate_rating(self) -> Dict[str, Any]:
        """Helper to get the aggregateRating dictionary."""
        return self.__info_dict.get("aggregateRating", {})

    @cached_property
    def number_reviews(self) -> int:
        """Returns the number of reviews for the recipe."""
        return self.aggregate_rating.get("reviewCount", 0)

    @cached_property
    def number_ratings(self) -> int:
        """Returns the number of ratings for the recipe."""
        return self.aggregate_rating.get("ratingCount", 0)

    @cached_property
    def rating(self) -> float:
        """Returns the average rating of the recipe."""
        return float(self.aggregate_rating.get("ratingValue", 0.0))

    @cached_property
    def category(self) -> Optional[str]:
        """Returns the category of the recipe."""
        return self.__info_dict.get("recipeCategory")
