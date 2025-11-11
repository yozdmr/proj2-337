from process_recipe.recipe import Recipe

def return_ingredients_response(recipe: Recipe, question_type: str="", get_first: bool = False) -> str:
    # Determine what ingredients to use
    if question_type == "all_ingredients":
        header = "Ingredients in the recipe:"
        ingredients = recipe.ingredients
    else:
        header = "Ingredients used in this step:"

        if question_type == "step_ingredients":
            ingredients = recipe.current_step.ingredients
        elif get_first:
            ingredients = recipe.first_step.ingredients

    if len(ingredients) == 0 and header.split(" ")[-1] == "step:":
        return "There are no ingredients for this step."
    
    # Construct response with custom CSS class
    response = f'<h4 class="chat-header">{header}</h4>'

    if isinstance(ingredients[0], dict):
        for ingredient in ingredients:
            response += f'<ul class="ingredient-list"><li>'
            if ingredient['descriptor'] is not None:
                desc_and_name = ingredient['descriptor'] + " " + ingredient['name']
            else:
                desc_and_name = ingredient['name']
            
            if len(desc_and_name) > 1:
                desc_and_name = desc_and_name[0].upper() + desc_and_name[1:]
            
            
            response += f"{desc_and_name}: {ingredient['quantity']}"

            if ingredient['measurement'] is not None:
                response += f" {ingredient['measurement']}"
            
            if ingredient['preparation'] is not None:
                response += f' <span>({ingredient["preparation"]})</span>'
            response += "</li>"
        response += "</ul>"
    elif isinstance(ingredients, list):
        ingredient_str = ", ".join(ingredients)
        response += f'<p>{ingredient_str}</p>'

    
    return response