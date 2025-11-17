from process_recipe.recipe import Recipe

def return_full_recipe_response(recipe: Recipe) -> str:
    answer = f"<h4 class='chat-header'>Full Recipe:</h4><span class='italic'>{recipe.name}</span>\n<ol class='recipe-list'>"
    for step in recipe.steps:
        answer += f"<li>{step['description']}</li>"
    answer += "</ol>"
    return answer