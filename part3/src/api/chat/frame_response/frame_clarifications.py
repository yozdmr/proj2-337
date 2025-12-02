import requests
from chat.preprocess_question import extract_clarification_subject
from process_recipe.recipe import Recipe


def return_specific_clarification_response(recipe: Recipe, question: str) -> str:
    # Get recipe tools
    recipe_tools = []
    for step in recipe.steps:
        recipe_tools.extend(step["tools"])
    
    print(question, recipe.ingredients, recipe_tools)
    clarification_subject, clarification_type = extract_clarification_subject(question, recipe.ingredients, recipe_tools)

    print("\t", clarification_subject, clarification_type)

    # Get definiton from https://dictionaryapi.dev/
    if clarification_subject:

        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{clarification_subject}")
        if response.status_code == 200:
            definitions = response.json()[0]["meanings"]

            # Each item in definitions is a dict and has a key "partOfSpeech"
            # Find the item with the key "partOfSpeech" that matches the clarification_type if possible
            # Else pick the first item
            final_definition = None
            for definition in definitions:
                if definition["partOfSpeech"] == clarification_type:
                    final_definition = definition["definitions"][0]["definition"]
                    break
            
            if final_definition is None:
                final_definition = definitions[0]["definitions"][0]["definition"]

            final_definition += ". You might find more useful information below!"
            final_definition = f"{clarification_subject}: " + final_definition
        else:
            final_definition = "I wasn't able to find a definition for that myself."
            final_definition += " Use the resources below to find more information."
    else:
        final_definition = "I'm sorry, I'm not sure what you're referring to."
    

    return final_definition