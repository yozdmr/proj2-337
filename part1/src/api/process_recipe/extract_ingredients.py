from typing import Optional
from bs4 import BeautifulSoup, Tag


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


def _parse_li_structured(li: Tag) -> dict:
    """Parse an <li> that contains structured spans with data-ingredient-* attributes."""
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

    descriptor = None
    preparation = extra_text or None

    return {
        "name": name,
        "quantity": quantity,
        "measurement": measurement,
        "descriptor": descriptor,
        "preparation": preparation,
    }


def _parse_text_fallback(text: str) -> dict:
    """Heuristic parsing for plain text ingredients."""
    import re as _re

    t = _clean_space(text)

    # Match quantity (supports mixed numbers and unicode fractions)
    frac = "[0-9]+\s+[0-9]/[0-9]|[0-9]/[0-9]|[0-9]+(?:\.[0-9]+)?|[¼½¾⅓⅔⅛⅜⅝⅞]"
    m_qty = _re.match(rf"^({frac})\b", t)
    quantity = m_qty.group(1) if m_qty else None
    rest = t[m_qty.end():].strip() if m_qty else t

    units = (
        "teaspoon|tsp|tablespoon|tbsp|cup|cups|ounce|ounces|oz|pound|pounds|lb|lbs|gram|grams|g|kilogram|kilograms|kg|pinch|dash|teaspoons|tablespoons|clove|cloves|slice|slices|package|packages|can|cans|quart|quarts|pint|pints|ml|l|litre|litres"
    )
    m_unit = _re.match(rf"^((?:{units}))\b", rest, _re.IGNORECASE)
    measurement = m_unit.group(1) if m_unit else None
    rest2 = rest[m_unit.end():].strip() if m_unit else rest

    # Parenthetical details treated as preparation
    m_paren = _re.search(r"\(([^\)]*)\)", rest2)
    preparation = m_paren.group(1).strip() if m_paren else None
    rest3 = _re.sub(r"\([^\)]*\)", "", rest2).strip()

    # Split by comma into name + preparation/descriptors
    parts = [p.strip() for p in rest3.split(",") if p.strip()]
    name = parts[0] if parts else rest3
    trailing = ", ".join(parts[1:]) if len(parts) > 1 else None
    preparation = preparation or trailing or None

    return {
        "name": name or None,
        "quantity": quantity,
        "measurement": measurement,
        "descriptor": None,
        "preparation": preparation,
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
            else:
                text = _clean_space(target.get_text(" ", strip=True))
                item = _parse_text_fallback(text)
            if any(item.get(k) for k in ("name", "quantity", "measurement", "descriptor", "preparation")):
                results.append(item)
        return results

    ingredients: list[dict] = []
    node: Optional[Tag] = header
    for _ in range(1000):
        node = node.find_next()
        if node is None:
            break
        if isinstance(node, Tag) and node.name in ("h2", "h3"):
            # Stop at the next main section header
            break
        if isinstance(node, Tag) and _is_ingredients_list(node):
            items = _extract_from_list(node)
            if items:
                ingredients.extend(items)

    return ingredients