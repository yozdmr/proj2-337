from typing import Optional
from bs4 import BeautifulSoup, Tag
import re as _re

from process_recipe.step_components.extract_tools import extract_tools
from process_recipe.step_components.extract_methods import extract_methods
from process_recipe.step_components.extract_time_temp import extract_time_info, extract_temperature_info


# Checks whether contains directions text in the tag or a span
def _contains_directions_text(tag: Tag) -> bool:
    text = tag.get_text(strip=True).lower()
    if "directions" in text:
        return True
    span = tag.find("span")
    if span and isinstance(span, Tag):
        span_text = span.get_text(strip=True).lower()
        if "directions" in span_text:
            return True
    return False



'''
{
    "step_number": int,
    "description": str,
    "ingredients": [list of ingredient names],
    "tools": [list of tools],
    "methods": [list of methods],
    "time": {
        "duration": str or dict of sub-times,
    },
    "temperature": {
        "oven": str (optional),
        "<ingredient>": str (optional)
    },
    "context": {
        "references": [related step numbers or preconditions],
        "warnings": [list of warnings or advice] (optional)
    }
}
'''
# Extracts steps from the recipe
def extract_steps(recipe: str, ingredients: list[dict]) -> list[dict]:
    soup = BeautifulSoup(recipe, "html.parser")

    header: Optional[Tag] = soup.find(
        lambda t: isinstance(t, Tag)  # Is a valid html tag
        and t.name in ("h2", "h3")    # is a h2 or h3 tag
        and _contains_directions_text(t)  # contains the text "directions" somehow
    )

    if not header:
        return []


    # Find Ordered List of Steps in identified header
    steps_list: Optional[Tag] = header.find_next("ol")
    if not steps_list:
        return []   
    
    context={}

    # Loop through steps in ordered list
    steps: list[dict] = []
    for idx, step in enumerate(steps_list.find_all("li"), start=1):
        description = step.get_text(strip=True)

        step_ingredients = []
        for ingredient in ingredients:
            ingredient_name = ingredient.get("name")
            if ingredient_name and ingredient_name in description:
                step_ingredients.append(ingredient_name)


        # NOTE: Main structure, do final output here
        step = {
            "step_number": idx,
            "description": description,
            "ingredients": step_ingredients,
            "tools": extract_tools(description),  # TODO implement this function
            "methods": extract_methods(description),  # TODO implement this function
            "time": extract_time_info(description)
        }
        temp_info, ctx_upd = extract_temperature_info(description, context)
        if temp_info:
            step["temperature"] = temp_info
        if ctx_upd:
            context.update(ctx_upd)

        if False:  # TODO implement optional temperature extraction
            step["temperature"] = {
                "oven": "TEMP_VAL",  # str (optional)
                "<ingredient>": "TEMP_VAL"  # str (optional)
            }


        steps.append(step)



    return steps
