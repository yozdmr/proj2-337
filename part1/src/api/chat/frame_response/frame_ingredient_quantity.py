def get_ingredient_quantity_response(ing):
    if ing is None:
        return (
            "I'm not sure which ingredient you're asking about. "
            "Try asking something like 'How much salt do I need?'."
        )
    
    name = str(ing.get("name") or "").strip()
    quantity = str(ing.get("quantity") or "").strip()
    measurement = str(ing.get("measurement") or "").strip()
    descriptor = str(ing.get("descriptor") or "").strip()

    display_name_parts = [p for p in [descriptor, name] if p]
    display_name = " ".join(display_name_parts) if display_name_parts else "this ingredient"

    if quantity or measurement:
        amount = " ".join(p for p in [quantity, measurement] if p)
        return f"You need {amount} of {display_name}."
    else:
        prep = ing.get("preparation")
        if prep:
            return (
                f"The recipe does not specify an exact amount for {display_name}, "
                f"but it says: {prep}."
            )
        else:
            return f"The recipe does not specify an exact amount for {display_name}."

