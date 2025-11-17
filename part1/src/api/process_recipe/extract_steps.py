from typing import Optional
from bs4 import BeautifulSoup, Tag
import re as _re

from process_recipe.step_components.extract_tools import extract_tools
from process_recipe.step_components.extract_methods import extract_methods
from process_recipe.step_components.extract_time_temp import extract_time_info, extract_temperature_info


# Split text into sentences based on sentence-ending punctuation.
def _split_into_sentences(text: str) -> list[str]:
    # Split on sentence-ending punctuation followed by whitespace or end of string
    # Pattern: . ! or ? followed by whitespace or end of string
    sentences = _re.split(r'(?<=[.!?])(?:\s+|$)', text)
    
    # Filter out empty strings and strip whitespace
    result = [s.strip() for s in sentences if s.strip()]
    
    return result


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

    # Get all text content from the directions section
    # Collect text from all siblings after the header until we hit another header or end
    directions_text_parts = []
    current = header.next_sibling
    
    while current:
        if isinstance(current, Tag):
            # Stop if we hit another header
            if current.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                break
            # Get text from this element
            text = current.get_text(separator=" ", strip=True)
            if text:
                directions_text_parts.append(text)
        elif isinstance(current, str):
            # Handle text nodes directly
            text = current.strip()
            if text:
                directions_text_parts.append(text)
        current = current.next_sibling
    
    # Combine all text parts
    directions_text = " ".join(directions_text_parts)
    
    if not directions_text.strip():
        return []
    
    # Split into sentences
    sentences = _split_into_sentences(directions_text)
    
    if not sentences:
        return []
    
    context={}

    # Loop through each sentence as a step
    steps: list[dict] = []
    for idx, description in enumerate(sentences, start=1):

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
