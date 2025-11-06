# Directional questions
#  -  is the next step? (and variations of this phrase))
#  -  is the previous step? ...
#  -  is the current step? ...

DIRECTIONAL_QUESTIONS = {
    # Next step
    "next": "next_step",
    "is next": "next_step",
    "next step": "next_step",
    "happens next": "next_step",

    # Previous step
    "is previous step": "previous_step",
    "previous": "previous_step",
    "do before?": "previous_step",
    "did we do before?": "previous_step",
    "happened last": "previous_step",
    "happened previously": "previous_step",
    "did previously": "previous_step",
    "did before": "previous_step",
    
    # Current step
    "is current step": "current_step",
    "current step": "current_step",
    "this step": "current_step",
    "happens now": "current_step",
    "do now": "current_step",
}

# Ingredient questions
#  -  are the ingredients to use in this recipe?
#  -  ingredients should I use in this step?

INGREDIENT_QUESTIONS = {
    # Get all ingredients in the recipe
    "are the ingredients": "all_ingredients",
    "are the ingredients to use in this recipe": "all_ingredients",
    "ingredients should i use": "all_ingredients",
    "ingredients do i need": "all_ingredients",
    "ingredients are needed": "all_ingredients",
    "ingredients are required": "all_ingredients",
    "ingredients are used": "all_ingredients",

    # Get ingredients for a specific step
    " ingredients are used in this step": "step_ingredients",
    " ingredients should i use in this step": "step_ingredients",
    " ingredients do i need in this step": "step_ingredients",
    " ingredients are needed in this step": "step_ingredients",
    " ingredients are required in this step": "step_ingredients",
    " ingredients in this step": "step_ingredients"
}

TIME_QUESTIONS = {
    "how long does this step take": "time",
    "how long does this take": "time",
    "how long does it take": "time",
    "how long does it take to make": "time",
    "how long does it take to cook": "time",
    "how long does it take to bake": "time",
    "how long does it take to prepare": "time",
    "how long will it take": "time",
    "how long will it take to make": "time",
    "how long will it take to cook": "time",
    "how long will it take to bake": "time",
    "how long will it take to prepare": "time",
    "how long will this take": "time",
    "how long will this step take": "time",
    "how much time": "time",
    "how much time does it take": "time",
    "how much time does it take to make": "time",
    "how much time does it take to cook": "time",
    "how much time does it take to bake": "time",
    "how much time does it take to prepare": "time",
    "how much time will it take": "time",
    "how much time will it take to make": "time",
    "how much time will it take to cook": "time",
    "how much time will it take to bake": "time",
    "how much time will it take to prepare": "time",
}