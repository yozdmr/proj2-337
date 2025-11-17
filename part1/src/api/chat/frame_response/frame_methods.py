from process_recipe.recipe import Recipe

# Returns formatted response for methods used in the current step.
def return_methods_response(recipe: Recipe) -> str:
    methods = recipe.current_step.methods
    
    if len(methods) == 0:
        return "<p>There are no methods used in this step.</p>"
    
    # Format methods as a comma-separated list
    methods_str = ", ".join(methods)
    return f"<h4 class='chat-header'>Methods used in this step:</h4><p>{methods_str}</p>"


# Returns formatted response for methods used across all steps in the recipe.
def return_all_methods_response(recipe: Recipe) -> str:
    answer = ""
    for step in recipe.steps:
        if len(step["methods"]) > 0:
            methods = ", ".join(step["methods"])
            answer += f"<p>Methods used in step {step['step_number']}: {methods}</p>"
        else:
            answer += f"<p>There are no methods used in step {step['step_number']}.</p>"
    
    return answer

from process_recipe.recipe import Recipe

def return_methods_response(recipe: Recipe, question_type: str = "", get_first: bool = False) -> str:
    # Decide which methods to show
    if question_type == "all_methods":
        header = "Methods used in the recipe:"
        all_methods = []
        for step in recipe.steps:
            if hasattr(step, "methods"):
                all_methods.extend(step.methods)
            elif isinstance(step, dict) and "methods" in step:
                all_methods.extend(step["methods"])
        methods = list(set(all_methods))
    else:
        header = "Methods used in this step:"
        if question_type == "step_methods":
            methods = getattr(recipe.current_step, "methods", [])
        elif get_first:
            methods = getattr(recipe.first_step, "methods", [])
        else:
            methods = []

    # Handle empty list
    if not methods:
        return "<p>There are no methods for this step.</p>"

    # Format response
    response = f'<h4 class="chat-header">{header}</h4>'
    response += '<ul class="method-list">'
    for method in methods:
        response += f"<li>{method.capitalize()}</li>"
    response += "</ul>"

    return response
