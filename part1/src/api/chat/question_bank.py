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
    "what is the next step": "next_step",
    "what do i do next": "next_step",

    # Previous step
    "is previous step": "previous_step",
    "previous": "previous_step",
    "do before?": "previous_step",
    "did we do before?": "previous_step",
    "happened last": "previous_step",
    "happened previously": "previous_step",
    "did previously": "previous_step",
    "did before": "previous_step",
    "what is the previous step": "previous_step",
    "what do i do before": "previous_step",
    
    # Current step
    "step": "current_step",
    "is current step": "current_step",
    "current step": "current_step",
    "this step": "current_step",
    "happens now": "current_step",
    "do now": "current_step",
    "what do i do now": "current_step",

    # First step
    "first step": "first_step",
    "what do i do first": "first_step",
    "what is the first step": "first_step",
    "what is the first step in the recipe": "first_step"
}

# Ingredient questions
#  -  are the ingredients to use in this recipe?
#  -  ingredients should I use in this step?

INGREDIENT_QUESTIONS = {
    # Get all ingredients in the recipe
    "ingredients": "all_ingredients",
    "are the ingredients": "all_ingredients",
    "are the ingredients to use in this recipe": "all_ingredients",
    "ingredients should i use": "all_ingredients",
    "ingredients do i need": "all_ingredients",
    "ingredients are needed": "all_ingredients",
    "ingredients are required": "all_ingredients",
    "ingredients are used": "all_ingredients",
    "ingredients in this recipe": "all_ingredients",
    "ingredients do i need in this recipe": "all_ingredients",
    "ingredients in the instructions": "all_ingredients",
    "all the ingredients": "all_ingredients",

    # Get ingredients for a specific step
    "this ingredients": "step_ingredients",
    "ingredients are used in this step": "step_ingredients",
    "ingredients should i use in this step": "step_ingredients",
    "ingredients do i need in this step": "step_ingredients",
    "ingredients are needed in this step": "step_ingredients",
    "ingredients are required in this step": "step_ingredients",
    "ingredients in this step": "step_ingredients",

    # Quantity of an ingredient:
    "how much do i need": "how_much_ingredient",
    "how many do i need": "how_much_ingredient",
    "how much of do i need": "how_much_ingredient",
    "how many of do i need": "how_much_ingredient",

    # Replacement of ingredient:
    "what can i use instead": "replacement_ingredient",
    "what can i use instead of": "replacement_ingredient",
    "what can i use instead of this": "replacement_ingredient",

}

TIME_QUESTIONS = {
    "time": "time",
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

TEMPERATURE_QUESTIONS = {
    "temperature": "temperature",
    "what temperature": "temperature",
    "what temp": "temperature",
    "oven temp": "temperature",
    "how hot": "temperature",
    "what degree": "temperature",
    "what degrees": "temperature",
    "bake at what temperature": "temperature",
}

AFFIRMATIONS = {
    # Positive answers
    "yes": "yes",
    "yeah": "yes",
    "yep": "yes",
    "yup": "yes",
    "sure": "yes",
    "definitely": "yes",
    "absolutely": "yes",
    "certainly": "yes",
    "indeed": "yes",
    "affirmative": "yes",

    # Negative answers
    "no": "no",
    "nope": "no",
    "nah": "no",
    "no way": "no",
    "not sure": "no",
    "not sure about that": "no",
    "negative": "no",

    # Repeat answers
    "repeat": "repeat",
    "repeat please": "repeat",
    "repeat that": "repeat",
    "repeat again": "repeat",
    "repeat one more time": "repeat",
    "repeat one more time please": "repeat",
    "repeat one more time that": "repeat",
    "repeat one more time again": "repeat",
    "say again": "repeat",
    "say it again": "repeat",
    "What was that again": "repeat"
}




# NOTE: Add question banks here
QUESTION_BANK = [
    DIRECTIONAL_QUESTIONS,
    INGREDIENT_QUESTIONS,
    TIME_QUESTIONS,
    TEMPERATURE_QUESTIONS,
    AFFIRMATIONS
]
