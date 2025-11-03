from typing import Optional
from bs4 import BeautifulSoup, Tag
import re as _re


# Checks whether contains ingredients text in the tag or a span
def _contains_ingredients_text(tag: Tag) -> bool:
    text = tag.get_text(strip=True).lower()
    if "ingredients" in text:
        return True
    span = tag.find("span")
    if span and isinstance(span, Tag):
        span_text = span.get_text(strip=True).lower()
        if "ingredients" in span_text:
            return True
    return False


def _clean_space(text: str) -> str:
    return " ".join((text or "").replace("\u2009", " ").replace("\xa0", " ").split())


# Converts Unicode fraction characters to their text equivalents.
# Examples: ⅓ -> "1/3", ¼ -> "1/4", ½ -> "1/2", etc.
def _convert_unicode_fractions(text: Optional[str]) -> Optional[str]:
    if not text:
        return text
    
    # Mapping of Unicode fraction characters to their text equivalents
    unicode_fractions = {'\u00BC': '1/4', '\u00BD': '1/2', '\u00BE': '3/4', '\u2153': '1/3', '\u2154': '2/3', '\u2155': '1/5', '\u2156': '2/5', '\u2157': '3/5', '\u2158': '4/5', '\u2159': '1/6', '\u215A': '5/6', '\u215B': '1/8', '\u215C': '3/8', '\u215D': '5/8', '\u215E': '7/8'}
    
    result = text
    for unicode_char, text_equivalent in unicode_fractions.items():
        result = result.replace(unicode_char, text_equivalent)
    
    return result

# Extracts descriptor and preparation from ingredient name if present.
def _extract_descriptor_and_preparation_from_name(name: Optional[str]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not name:
        return name, None, None
    
    name_lower = name.lower()
    
    # Common descriptor words (adjectives/qualifiers that describe the ingredient)
    descriptor_words = {
        'boneless', 'skinless', 'bone-in', 'skin-on',
        'ground', 'whole', 'fresh', 'dried', 'frozen', 'raw', 'cooked', 
        'roasted', 'toasted', 'organic', 'pure', 'extra', 'fine', 'coarse',
        'large', 'small', 'medium', 'whole',
        'golden', 'red', 'white', 'yellow', 'green', 'black', 'brown', 'pink', 'purple', 'orange',
        'all-purpose', 'whole-wheat', 'extra-virgin',
    }
    
    # Multi-word descriptor phrases
    multi_word_descriptors = {
        'all purpose', 'whole wheat', 'baking soda', 'baking powder', 'extra virgin',
        'golden delicious', 'red delicious', 'granny smith'
    }
    
    # Preparation verb patterns (action verbs that indicate preparation)
    preparation_patterns = [
        r'\bcut\s+into\s+[^,]*',  # "cut into 1-inch cubes"
        r'\bchopped\s+(?:into|in)\s+[^,]*',  # "chopped into pieces"
        r'\bdiced\s+(?:into|in)\s+[^,]*',  # "diced into cubes"
        r'\bsliced\s+(?:into|in|thin|thick)\s+[^,]*',  # "sliced thin"
        r'\bminced\s+[^,]*',  # "minced garlic"
        r'\bgrated\s+[^,]*',  # "grated cheese"
        r'\bshredded\s+[^,]*',  # "shredded"
        r'\bcubed\s+[^,]*',  # "cubed"
        r'\bjulienned\s+[^,]*',  # "julienned"
        r'\bquartered\s+[^,]*',  # "quartered"
        r'\bhalved\s+[^,]*',  # "halved"
        r'\bpeeled\s+[^,]*',  # "peeled"
        r'\bseeded\s+[^,]*',  # "seeded"
        r'\btrimmed\s+[^,]*',  # "trimmed"
    ]
    
    # First, extract preparation instructions
    preparation = None
    remaining_name = name
    for pattern in preparation_patterns:
        match = _re.search(pattern, name_lower, _re.IGNORECASE)
        if match:
            # Extract with original case
            start, end = match.span()
            prep_text = name[start:end].strip()
            # Remove from name
            remaining_name = (name[:start] + name[end:]).strip()
            remaining_name = _re.sub(r'\s*,\s*,', ',', remaining_name)  # Clean up double commas
            remaining_name = remaining_name.rstrip(',').strip()
            preparation = prep_text
            break
    
    # If no pattern match, check for comma-separated preparation at the end
    if preparation is None:
        parts = [p.strip() for p in remaining_name.split(',') if p.strip()]
        if len(parts) > 1:
            # Check if last part(s) contain preparation verbs
            last_part = parts[-1].lower()
            prep_indicators = ['cut', 'chopped', 'diced', 'sliced', 'minced', 'grated', 
                             'shredded', 'cubed', 'quartered', 'halved', 'peeled', 
                             'trimmed', 'into', 'in']
            if any(ind in last_part for ind in prep_indicators):
                preparation = parts[-1]
                parts = parts[:-1]
                remaining_name = ', '.join(parts)
    
    # Now extract descriptors from the remaining name
    # Process word by word, handling commas
    descriptor_parts = []
    words = remaining_name.split()
    remaining_words = []
    i = 0
    
    # Extract descriptors from the beginning
    while i < len(words):
        found_descriptor = False
        
        # Check for multi-word descriptors first (2 words)
        if i + 1 < len(words):
            two_word_lower = ' '.join([words[i].lower(), words[i+1].lower()])
            if two_word_lower in multi_word_descriptors:
                # Remove trailing comma from second word if present
                word1 = words[i]
                word2 = words[i+1].rstrip(',')
                descriptor_parts.append(' '.join([word1, word2]))
                i += 2
                found_descriptor = True
                
                # If word2 had a comma, moved past a comma boundary
                # Continue checking for more descriptors after comma
                if words[i-1].endswith(','):
                    continue
        
        # Check single-word descriptors
        if not found_descriptor and i < len(words):
            word_lower = words[i].lower().rstrip(',')
            if word_lower in descriptor_words:
                descriptor_parts.append(words[i].rstrip(','))
                i += 1
                found_descriptor = True
            else:
                # First non-descriptor found, rest is the name
                break
        
        if not found_descriptor:
            break
    
    # Remaining words form the name
    remaining_words = words[i:]
    
    # Join descriptor parts (preserve comma separations if they were there)
    descriptor = ', '.join(descriptor_parts) if descriptor_parts else None
    
    # Join remaining words as the name
    cleaned_name = ' '.join(remaining_words).strip()
    cleaned_name = _re.sub(r'\s*,\s*$', '', cleaned_name)  # Remove trailing comma
    cleaned_name = _clean_space(cleaned_name) if cleaned_name else None
    
    # Clean up descriptor
    if descriptor:
        descriptor = descriptor.strip().rstrip(',')
    
    # Clean up preparation
    if preparation:
        preparation = preparation.strip().rstrip(',')
    
    return cleaned_name or None, descriptor or None, preparation or None


def _parse_li_structured(li: Tag) -> dict:
    p = li.find("p")
    target = p if isinstance(p, Tag) else li

    def first_text(selector: str) -> Optional[str]:
        node = target.find("span", attrs={selector: True})
        return _clean_space(node.get_text(" ", strip=True)) if node else None

    def all_texts(selector: str) -> list[str]:
        nodes = target.find_all("span", attrs={selector: True})
        return [_clean_space(n.get_text(" ", strip=True)) for n in nodes if _clean_space(n.get_text(" ", strip=True))]

    quantity = " ".join(all_texts("data-ingredient-quantity")) or None
    measurement = " ".join(all_texts("data-ingredient-unit")) or None
    name = first_text("data-ingredient-name")

    # Convert Unicode fractions in quantity to text format
    quantity = _convert_unicode_fractions(quantity)

    # Extract descriptor and preparation from name if present
    cleaned_name, extracted_descriptor, extracted_preparation = _extract_descriptor_and_preparation_from_name(name)

    # Collect any remaining text around spans as preparation/descriptor details
    extra_parts: list[str] = []
    for child in target.children:
        if isinstance(child, Tag) and child.name == "span" and (
            child.has_attr("data-ingredient-quantity") or child.has_attr("data-ingredient-unit") or child.has_attr("data-ingredient-name")
        ):
            continue
        extra = _clean_space(getattr(child, "get_text", lambda *a, **k: str(child))(" ", strip=True) if isinstance(child, Tag) else str(child))
        if extra:
            extra_parts.append(extra)
    extra_text = _clean_space(" ".join(extra_parts)).lstrip(",;: ")

    # Merge preparation from name extraction and extra text
    descriptor = extracted_descriptor
    preparation_parts = []
    if extracted_preparation:
        preparation_parts.append(extracted_preparation)
    if extra_text:
        preparation_parts.append(extra_text)
    preparation = ", ".join(preparation_parts) if preparation_parts else None

    return {
        "name": cleaned_name,
        "quantity": quantity,
        "measurement": measurement,
        "descriptor": descriptor,
        "preparation": preparation if preparation is not None and preparation[:3] != "( )" else None,
    }



def extract_ingredients(recipe: str) -> list[dict]:
    soup = BeautifulSoup(recipe, "html.parser")

    header: Optional[Tag] = soup.find(
        lambda t: isinstance(t, Tag)  # Is a valid html tag
        and t.name in ("h2", "h3")    # is a h2 or h3 tag
        and _contains_ingredients_text(t)  # contains the text "ingredients" somehow
    )

    if not header:
        return []

    def _is_ingredients_list(tag: Tag) -> bool:
        if not isinstance(tag, Tag):
            return False
        if tag.name not in ("ul", "ol"):
            return False
        cls = " ".join(tag.get("class", [])).lower()
        if "structured-ingredients__list" in cls:
            return True
        if "mm-recipes-structured-ingredients__list" in cls:
            return True
        if "o-Ingredients__a-Ingredient" in cls:
            return True
        # Fallback: generic list immediately under ingredients section
        return True

    def _extract_from_list(list_tag: Tag) -> list[dict]:
        results: list[dict] = []
        for li in list_tag.find_all("li", recursive=False):
            # Prefer <p> inside <li> if present, then fall back to li text
            p = li.find("p")
            target = p if isinstance(p, Tag) else li
            spans = target.find_all("span")
            if any(s.has_attr("data-ingredient-name") or s.has_attr("data-ingredient-quantity") or s.has_attr("data-ingredient-unit") for s in spans):
                item = _parse_li_structured(li)
            
            if any(item.get(k) for k in ("name", "quantity", "measurement", "descriptor", "preparation")):
                if item.get("name") is None:
                    if item.get("descriptor") is not None:
                        item["name"], item["descriptor"] = item["descriptor"], item["name"]
                    else:
                        continue
                
                results.append(item)
        return results

    ingredients: list[dict] = []
    node: Optional[Tag] = header
    for _ in range(1000):
        node = node.find_next()
        if node is None:
            break
        if isinstance(node, Tag) and node.name in ("h1", "h2", "h3", "h4"):
            # Stop at the next main section header
            break
        if isinstance(node, Tag) and _is_ingredients_list(node):
            items = _extract_from_list(node)
            if items:
                ingredients.extend(items)

    return ingredients