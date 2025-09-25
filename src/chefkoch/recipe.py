# -*- coding: utf-8 -*-
""" This module provides a class to scrape recipes from chefkoch.de """

import datetime
import json
import re
from functools import cached_property
from typing import List, Optional, Union, Dict, Any

import isodate
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.chefkoch.de/rezepte"


class Recipe:
    """
    Represents a recipe from the Chefkoch website.
    Supports both old and new page layouts with robust fallbacks.
    """

    def __init__(self, url: Optional[str] = None, id: Optional[str] = None):
        """
        Initializes a Recipe object.

        Args:
            url (str, optional): The URL of the recipe. Defaults to None.
            id (str, optional): The ID of the recipe. Defaults to None.
        """
        if url is None and id is None:
            raise ValueError("Either url or id must be provided")

        if id is not None:
            url = f"{BASE_URL}/{id}"

        if not url.startswith(BASE_URL.split("/rezepte")[0]):
            raise ValueError(f"Invalid URL: {url}")

        # Clean URL from query parameters like '?zufall=on'
        self.url: str = url.split("?")[0]

        if id is None:
            try:
                # Extracts the numeric ID from the URL path
                self.id: str = self.url.split("/")[4]
            except IndexError:
                raise ValueError(f"Could not extract recipe ID from URL: {self.url}")
        else:
            self.id = id

    @cached_property
    def __soup(self) -> BeautifulSoup:
        """
        Returns the BeautifulSoup object of the recipe's webpage.
        Includes a User-Agent to mimic a real browser.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(self.url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    @cached_property
    def __is_new_format(self) -> bool:
        """Checks if the recipe page uses the new Next.js format."""
        return bool(self.__soup.find("script", id="__NEXT_DATA__"))

    @cached_property
    def __recipe_data(self) -> Dict[str, Any]:
        """
        Extracts recipe data from the page's JSON scripts (JSON-LD or __NEXT_DATA__).
        This is the primary method for data extraction.
        """
        # New format (preferred): __NEXT_DATA__
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
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Recipe":
                    return data
                if isinstance(data, dict) and "@graph" in data:
                    for item in data.get("@graph", []):
                        if isinstance(item, dict) and item.get("@type") == "Recipe":
                            return item
            except json.JSONDecodeError:
                continue
        return {} # Return empty dict if no JSON data found

    @cached_property
    def title(self) -> str:
        """Returns the title of the recipe."""
        title = self.__recipe_data.get("title") or self.__recipe_data.get("name")
        if title:
            return title
        # Absolute fallback if JSON fails
        title_tag = self.__soup.find("h1")
        return title_tag.get_text(strip=True) if title_tag else "Titel nicht gefunden"


    @cached_property
    def image_url(self) -> str:
        """Returns the URL of the recipe's main image."""
        if self.__is_new_format:
            image_info = self.__recipe_data.get("image", {})
            if image_info and "url" in image_info:
                return image_info["url"]

        image_data = self.__recipe_data.get("image")
        if isinstance(image_data, list) and image_data:
            return image_data[0]
        if isinstance(image_data, str):
            return image_data

        og_image = self.__soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]

        return "Bild nicht gefunden"

    def _parse_duration(self, time_val: Optional[Union[str, int]]) -> Optional[isodate.Duration]:
        """Helper to parse duration from ISO string ('PT15M') or minutes (15)."""
        if time_val is None: return None
        if isinstance(time_val, int):
            return isodate.parse_duration(f"PT{time_val}M")
        if isinstance(time_val, str) and time_val.startswith('P'):
            try:
                return isodate.parse_duration(time_val)
            except isodate.ISO8601Error:
                return None
        return None

    def _scrape_time(self, search_texts: List[str]) -> Optional[isodate.Duration]:
        """Robust helper to scrape time by searching for text labels in the HTML."""
        try:
            parent_tag = self.__soup.find(lambda tag: tag.string and any(s.lower() in tag.string.lower() for s in search_texts))
            if parent_tag:
                # Navigate up to a more meaningful parent if needed
                container = parent_tag.find_parent(class_=re.compile(r'recipe-meta-item|ds-mb-right'))
                text_to_search = container.get_text(strip=True) if container else parent_tag.get_text(strip=True)

                minutes_match = re.search(r'(\d+)\s*(Min\.|Minuten)', text_to_search, re.IGNORECASE)
                if minutes_match:
                    return isodate.parse_duration(f"PT{minutes_match.group(1)}M")
        except Exception:
            pass
        return None

    @cached_property
    def prep_time(self) -> Optional[isodate.Duration]:
        """Returns the preparation time of the recipe."""
        duration = self._parse_duration(self.__recipe_data.get("prepTime"))
        return duration or self._scrape_time(["Zubereitungszeit:", "Arbeitszeit:"])

    @cached_property
    def cook_time(self) -> Optional[isodate.Duration]:
        """Returns the cooking time of the recipe."""
        duration = self._parse_duration(self.__recipe_data.get("cookTime"))
        return duration or self._scrape_time(["Koch-/Backzeit:", "Backzeit:"])

    @cached_property
    def rest_time(self) -> Optional[isodate.Duration]:
        """Scrapes the resting time from the recipe meta data, if available."""
        return self._scrape_time(["Ruhezeit:"])

    @cached_property
    def total_time(self) -> Optional[isodate.Duration]:
        """Returns the total time required to prepare the recipe."""
        duration = self._parse_duration(self.__recipe_data.get("totalTime"))
        if duration:
            return duration

        # Fallback: Scrape or calculate
        scraped_total = self._scrape_time(["Gesamtzeit:"])
        if scraped_total:
            return scraped_total

        # Fallback: Sum prep and cook time
        total = datetime.timedelta()
        if self.prep_time: total += self.prep_time.td
        if self.cook_time: total += self.cook_time.td
        if self.rest_time: total += self.rest_time.td

        return isodate.parse_duration(str(total)) if total.total_seconds() > 0 else None


    @cached_property
    def difficulty(self) -> str:
        """Returns the difficulty level of the recipe."""
        # Priority 1: New JSON format
        if self.__is_new_format:
            diff_map = {"SIMPLE": "simpel", "NORMAL": "normal", "ADVANCED": "pfiffig"}
            difficulty_key = self.__recipe_data.get("difficulty")
            if difficulty_key: return diff_map.get(difficulty_key, "unklar").lower()

        # Priority 2: Old JSON-LD format
        difficulty_tag_json = self.__recipe_data.get("recipeDifficulty")
        if difficulty_tag_json: return str(difficulty_tag_json).lower()

        # Priority 3: Robust scraping for sibling structure from user snippet
        try:
            title_div = self.__soup.find('div', class_="recipe-meta-property-group__title", string=re.compile(r'Schwierigkeit', re.I))
            if title_div:
                value_div = title_div.find_previous_sibling("div", class_="recipe-meta-property-group__value")
                if value_div:
                    return value_div.get_text(strip=True).lower()
        except Exception:
            pass

        # Priority 4: Fallback for very old formats (find by text node)
        try:
            diff_text_node = self.__soup.find(string=re.compile(r'\s*Schwierigkeitsgrad\s*:?\s*', re.IGNORECASE))
            if diff_text_node:
                parent = diff_text_node.find_parent()
                if parent:
                    value_tag = parent.find("strong")
                    if value_tag:
                        return value_tag.get_text(strip=True).lower()
                    full_text = parent.get_text(strip=True)
                    if ":" in full_text:
                        return full_text.split(":")[-1].strip().lower()
        except Exception:
            pass

        return "unknown"

    @cached_property
    def servings(self) -> Optional[int]:
        """Returns the number of servings."""
        if self.__is_new_format:
            servings = self.__recipe_data.get("servings")
            if servings: return int(servings)

        yield_str = self.__recipe_data.get("recipeYield")
        if yield_str:
            match = re.search(r'\d+', str(yield_str))
            if match: return int(match.group(0))

        # Fallback to scraping the input field
        try:
            servings_input = self.__soup.find("input", {"name": "portionen", "type": "text"})
            if servings_input and servings_input.get("value"):
                return int(servings_input["value"])
        except (AttributeError, ValueError):
            pass
        return None

    @cached_property
    def ingredients(self) -> List[str]:
        """Returns the list of ingredients required for the recipe."""
        if self.__is_new_format:
            ingredients_list = []
            for group in self.__recipe_data.get("ingredientGroups", []):
                for ingredient in group.get("ingredients", []):
                    parts = [
                        str(ingredient["amount"]) if ingredient.get("amount") else "",
                        ingredient.get("unit", ""),
                        ingredient.get("name", ""),
                    ]
                    ingredients_list.append(" ".join(filter(None, parts)).strip())
            if ingredients_list: return ingredients_list

        ingredients = self.__recipe_data.get("recipeIngredient", [])
        if ingredients: return ingredients

        # Fallback to scraping the table
        table = self.__soup.find("table", class_="ingredients")
        if not table: return []

        scraped_ingredients = []
        for row in table.find_all("tr"):
            amount_td = row.find("td", class_="td-amount")
            name_td = row.find("td", class_="td-name")
            if amount_td and name_td:
                amount = amount_td.get_text(strip=True)
                name = name_td.get_text(strip=True)
                scraped_ingredients.append(f"{amount} {name}".strip())
        return scraped_ingredients


    @cached_property
    def instructions(self) -> str:
        """Returns the preparation instructions as a single string."""
        if self.__is_new_format:
            instructions = self.__recipe_data.get("instructions", "")
            if instructions: return instructions

        instruction_data = self.__recipe_data.get("recipeInstructions", [])
        if isinstance(instruction_data, list):
            texts = [step.get("text", "") for step in instruction_data if isinstance(step, dict)]
            if texts: return "\n".join(texts)
        if isinstance(instruction_data, str):
            return instruction_data

        # Fallback to scraping
        instructions_div = self.__soup.find("div", id="rezept-zubereitung")
        return instructions_div.get_text("\n", strip=True) if instructions_div else ""


    @cached_property
    def author(self) -> str:
        """Returns the name of the author of the recipe."""
        if self.__is_new_format:
            author_name = self.__recipe_data.get("author", {}).get("username")
            if author_name: return author_name

        author_data = self.__recipe_data.get("author", {})
        if isinstance(author_data, list) and author_data:
            return author_data[0].get("name", "Unbekannt")
        if isinstance(author_data, dict):
            return author_data.get("name", "Unbekannt")

        # Fallback
        author_tag = self.__soup.find(class_="recipe-author__name")
        return author_tag.get_text(strip=True) if author_tag else "Unbekannt"


    @cached_property
    def calories(self) -> str:
        """Returns the calories of the recipe as a string (e.g., '432 kcal')."""
        nutrition = self.__recipe_data.get("nutrition", {})
        if self.__is_new_format:
            kcal = nutrition.get("nutrients", {}).get("calories")
            if kcal: return f"{kcal} kcal"

        calories = nutrition.get("calories")
        if calories: return calories

        # Fallback scraping
        calories_tag = self.__soup.find(class_="recipe-calories")
        return calories_tag.get_text(strip=True) if calories_tag else "k.A."


    @cached_property
    def _aggregate_rating(self) -> Dict[str, Any]:
        """Helper to get rating block from either format."""
        return self.__recipe_data.get("rating", self.__recipe_data.get("aggregateRating", {}))

    @cached_property
    def number_ratings(self) -> int:
        """Returns the number of ratings for the recipe."""
        rating_data = self._aggregate_rating
        return int(rating_data.get("numRatings", rating_data.get("ratingCount", 0)))

    @cached_property
    def rating(self) -> float:
        """Returns the average rating of the recipe."""
        rating_data = self._aggregate_rating
        return float(rating_data.get("average", rating_data.get("ratingValue", 0.0)))
