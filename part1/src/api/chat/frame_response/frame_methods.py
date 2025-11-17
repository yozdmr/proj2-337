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

