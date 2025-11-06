# Directional questions
#  - What is the next step? (and variations of this phrase))
#  - What is the previous step? ...
#  - What is the current step? ...

DIRECTIONAL_QUESTIONS = {
    # Next step
    "what is the next step": "next_step",
    "next": "next_step",
    "next step": "next_step",
    "what's next": "next_step",
    "what happens next": "next_step",

    # Previous step
    "what is the previous step": "previous_step",
    "previous": "previous_step",
    "what did we do before?": "previous_step",
    "what happened last": "previous_step",
    "what did we do before?": "previous_step",
    # Current step
    "what is the current step": "current_step",
    "current": "current_step",
    "what happens now": "current_step",
    "what to do now": "current_step",
    "what now": "current_step"
}

# Ingredient questions
#  - What are the ingredients to use in this recipe?
#  - What ingredients should I use in this step?

INGREDIENT_QUESTIONS = {
    # Get all ingredients in the recipe
    "what are the ingredients": "all_ingredients",
    "what are the ingredients to use in this recipe": "all_ingredients",
    "what ingredients should i use": "all_ingredients",
    "what ingredients do i need": "all_ingredients",
    "what ingredients are needed": "all_ingredients",
    "what ingredients are required": "all_ingredients",
    "what ingredients are used": "all_ingredients",

    # Get ingredients for a specific step
    "what ingredients are used in this step": "step_ingredients",
    "what ingredients should i use in this step": "step_ingredients",
    "what ingredients do i need in this step": "step_ingredients",
    "what ingredients are needed in this step": "step_ingredients",
    "what ingredients are required in this step": "step_ingredients",
    "what ingredients in this step": "step_ingredients"
}