import requests
import re

from chat.preprocess_question import extract_step_number, extract_clarification_subject, classify_question

from chat.frame_response.frame_ingredients import return_ingredients_response
from chat.frame_response.frame_full_recipe import return_full_recipe_response
from chat.frame_response.frame_time import return_time_response
from chat.frame_response.frame_clarifications import return_specific_clarification_response
from chat.frame_response.frame_methods import return_methods_response, return_all_methods_response
from chat.frame_response.frame_methods import return_methods_response
from chat.frame_response.frame_ingredient_substitution import return_ingredient_substitution_response


from process_recipe.recipe import Recipe

from chat.conversation_history import ConversationHistory
conversation = ConversationHistory()


global previous_question
global previous_answer
previous_question, previous_answer = None, None


def reset_conversation_state():
    global previous_question
    global previous_answer
    previous_question = None
    previous_answer = None

# helper functions for ingredient-based questions
_INGREDIENT_STOPWORDS = {
    "a", "an", "the", "of", "to", "for", "with",
    "how", "much", "many", "do", "does", "did",
    "i", "you", "we", "they", "he", "she", "it",
    "need", "needs", "needed", "use", "used", "using",
    "should", "this", "that", "step", "recipe",
    "instead", "can", "could",
}


def _normalize_text_for_match(text: str) -> str:
    """Lowercase, keep only letters and spaces, collapse whitespace."""
    text = re.sub(r"[^a-zA-Z\\s]", " ", text.lower())
    return " ".join(text.split())


def _get_ingredient_list(recipe):
    """Get the list of ingredient dicts from the Recipe object or dict."""
    if recipe is None:
        return []
    # recipe class
    if hasattr(recipe, "get_ingredients"):
        try:
            ing = recipe.get_ingredients()
            if ing:
                return list(ing)
        except Exception:
            pass
    # fallback attributes
    if hasattr(recipe, "ingredients"):
        ing = getattr(recipe, "ingredients")
        if ing:
            return list(ing)
    # Dict-style
    if isinstance(recipe, dict):
        ing = recipe.get("ingredients")
        if ing:
            return list(ing)
    return []


def _best_match_ingredient_from_question(question: str, recipe):
    """Heuristically find the ingredient mentioned in the question."""
    ingredients = _get_ingredient_list(recipe)
    if not ingredients:
        return None

    q_norm = _normalize_text_for_match(question)
    if not q_norm:
        return None

    q_tokens = [
        t for t in q_norm.split()
        if t and t not in _INGREDIENT_STOPWORDS
    ]
    if not q_tokens:
        # Fall back to using all tokens
        q_tokens = q_norm.split()
    q_token_set = set(q_tokens)

    best = None
    best_score = 0.0

    for ing in ingredients:
        # ingredient can be a dict or a simple string
        if isinstance(ing, dict):
            name = str(ing.get("name") or ing.get("ingredient") or ing.get("ingredient_name") or "")
        else:
            name = str(ing)
        name_norm = _normalize_text_for_match(name)
        if not name_norm:
            continue
        name_tokens = name_norm.split()
        name_token_set = set(name_tokens)
        if not name_token_set:
            continue

        overlap = len(q_token_set & name_token_set)
        overlap_ratio = overlap / len(name_token_set)

        substring_bonus = 0.0
        if name_norm in q_norm:
            substring_bonus = 0.5

        score = overlap_ratio + substring_bonus
        if score > best_score:
            best_score = score
            best = ing
            
    if best_score == 0.0:
        return None
    return best



def handle_question(question: str, recipe: Recipe) -> dict:
    global previous_question
    global previous_answer

    conversation.print_history()

    
    question_type = classify_question(question)
    print("\t", question_type)

    if question_type in ["recipe"]:
        previous_answer = {
            "answer": return_full_recipe_response(recipe),
            "suggestions": {
                "What ingredients do I need?": "What ingredients do I need in the whole recipe?",
                "What tools should I use?": "What tools should I use in the whole recipe?",
                "What do I do first?": "What do I do first?",
            }
        }

        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer


    elif question_type in ["next_step", "previous_step", "current_step", "first_step", "nth_step"]:
        # Default value
        stepped = True

        if question_type == "first_step":
            # Avoid updating recipe.first_step so that it remains the same 
            subject_step = recipe.first_step
            answer = f"<h4 class='chat-header'>Step {subject_step.step_number}:</h4><p>{subject_step.description}</p>"

        else:
            if question_type == "next_step":
                subject_step, stepped = recipe.step_forward()
            elif question_type == "previous_step":
                subject_step, stepped = recipe.step_backward()
            elif question_type == "current_step":
                subject_step = recipe.current_step
            elif question_type == "nth_step":

                step_number = extract_step_number(question)
                temp_step = recipe.nth_step(step_number)

                if temp_step is not None:
                    recipe.current_step = temp_step
                subject_step = recipe.current_step

            # Construct response
            answer = f"<h4 class='chat-header'>Step {subject_step.step_number}:</h4><p>{subject_step.description}</p>"
        
        # NOTE: If this is true, set previous question, because the bot's response
        #   asks yes/no question at the end
        if subject_step.ingredients:
            answer += f"\n<p>Would you like to know about the ingredients used in this step?</p>"
            previous_question = question_type
        
        previous_answer = {
            "answer": answer,
            "suggestions": {
                # visible text, text to put in the input field
                "What are the methods?": "What methods are used in this step?",
                "What ingredients do I need?": "What ingredients do I need in this step?",
                "What do I do next?": "What do I do next?"
            }
        }

        if stepped:
            conversation.add_step(question, question_type, previous_answer, recipe.current_step)
            return previous_answer
        else:
            if question_type == "next_step":
                return "Congratulations! You've completed the recipe."
            elif question_type == "previous_step":
                return "You're at the beginning of the recipe. Onwards!"


    elif question_type in ["step_methods", "all_methods"]:
        if question_type == "step_methods":
            methods = getattr(recipe.current_step, "methods", [])
            if methods:
                methods_str = ", ".join(methods)
                answer = f"<p>Methods used in this step: {methods_str}</p>"
            else:
                answer = "<p>There are no methods for this step.</p>"

            previous_answer = {
                "answer": answer,
                "suggestions": {
                    "What ingredients do I need?": "What ingredients do I need in this step?",
                    "What tools should I use?": "What tools should I use in this step?",
                    "What do I do next?": "What do I do next?",
                }
            }

        elif question_type == "all_methods":
            answer = ""
            for step in recipe.steps:
                methods = step.get("methods", [])
                if methods:
                    methods_str = ", ".join(methods)
                    answer += f"<p>Methods used in step {step['step_number']}: {methods_str}</p>"
                else:
                    answer += f"<p>There are no methods in step {step['step_number']}.</p>"
            
            previous_answer = {
                "answer": answer,
                "suggestions": {
                    "What ingredients are in this recipe?": "What ingredients does this recipe have?",
                    "What tools do I need?": "What tools do I need for this recipe?",
                    "What do I do next?": "What do I do next?",
                }
            }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer
        
    elif question_type in ["all_ingredients", "step_ingredients"]:
        answer = return_ingredients_response(recipe, question_type)
        previous_answer = {
            "answer": answer,
            "suggestions": {
                "What methods should I use?": "What methods should I use in this step?",
                "How long will this step take?": "How long will this step take?",
                "What do I do next?": "What do I do next?",
            }
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer
    

    elif question_type in ["step_tools", "all_tools"]:
        if question_type == "step_tools":
            if len(recipe.current_step.tools) > 0:
                tools = ", ".join(recipe.current_step.tools)
                answer = f"<p>Tools used in this step: {tools}</p>"
            else:
                answer = "<p>There are no tools used in this step.</p>"
            
            previous_answer = {
                "answer": answer,
                "suggestions": {
                    "What ingredients do I need?": "What ingredients do I need in this step?",
                    "How long will this step take?": "How long will this step take?",
                    "What do I do next?": "What do I do next?",
                }
            }
        elif question_type == "all_tools":
            answer = ""
            for step in recipe.steps:
                if len(step["tools"]) > 0:
                    tools = ", ".join(step["tools"])
                    answer += f"<p>Tools used in step {step['step_number']}: {tools}</p>"
                else:
                    answer += f"<p>There are no tools used in step {step['step_number']}.</p>"
        
            previous_answer = {
                "answer": answer,
                "suggestions": {
                    "What ingredients does this recipe need?": "What ingredients for the whole recipe?",
                    "What do I do next?": "What do I do next?",
                }
            }

        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    elif question_type in ["how_much_ingredient"]:
        ing = _best_match_ingredient_from_question(question, recipe)

        if ing is None:
            answer_text = (
                "I'm not sure which ingredient you're asking about. "
                "Try asking something like 'How much salt do I need?'."
            )
        else:
            name = str(ing.get("name") or "").strip()
            quantity = str(ing.get("quantity") or "").strip()
            measurement = str(ing.get("measurement") or "").strip()
            descriptor = str(ing.get("descriptor") or "").strip()

            display_name_parts = [p for p in [descriptor, name] if p]
            display_name = " ".join(display_name_parts) if display_name_parts else "this ingredient"

            if quantity or measurement:
                amount = " ".join(p for p in [quantity, measurement] if p)
                answer_text = f"You need {amount} of {display_name}."
            else:
                prep = ing.get("preparation")
                if prep:
                    answer_text = (
                        f"The recipe does not specify an exact amount for {display_name}, "
                        f"but it says: {prep}."
                    )
                else:
                    answer_text = f"The recipe does not specify an exact amount for {display_name}."

        previous_answer = {
            "answer": f"<p>{answer_text}</p>",
            "suggestions": {
                "What can I use instead?": f"What can I use instead of {ing['name']}?",
                "What do I do next?": "What do I do next?",
            },
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    elif question_type in ["replacement_ingredient"]:
        # Ingredient substitution, e.g. "What can I use instead of butter?"
        answer, ingr = return_ingredient_substitution_response(recipe, question)

        previous_answer = {
            "answer": answer,
            "suggestions": {
                "How much do I need?": f"How much {ingr} do I need?",
                "What do I do next?": "What do I do next?",
            },
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    elif question_type in ["time"]:
        previous_answer = {
            "answer": return_time_response(recipe),
            "suggestions": None
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    
    elif question_type in ["temperature"]:
        step = recipe.current_step
        tinf = getattr(step, "temperature", None) or {}
        answer = "This step does not specify a temperature."
        if tinf:
            parts = []
            if tinf.get("oven"):
                parts.append(f"Oven: {tinf['oven']}")
            if tinf.get("stovetop"):
                parts.append(f"Stovetop: {tinf['stovetop']}")
            if parts:
                answer = "; ".join(parts)
            elif tinf.get("mentions"):
                answer = tinf["mentions"][0].get("qualitative") or tinf["mentions"][0].get("text") or answer
        previous_answer = {"answer": answer, "suggestions": None}
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer 


    

    elif question_type in ["clarification_specific", "clarification_general"]:
        # Prepare search URLs for both types
        question_search_term = question.replace(" ", "+")
        search_str_google = f"https://www.google.com/search?q={question_search_term}"
        search_str_youtube = f"https://www.youtube.com/results?search_query={question_search_term}"
        
        if question_type == "clarification_specific":
            final_definition = return_specific_clarification_response(recipe, question)
        elif question_type == "clarification_general":
            final_definition = "not done yet..."
        

        previous_answer = {
            "answer": f"<p>{final_definition}</p>",
            "suggestions": {
                "Google": search_str_google,
                "YouTube": search_str_youtube
            }
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    # Affirmation responses (in response to a yes/no question from the previous bot response)
    #  As of right now, when asking for STEP information, the bot will ask:
    #    "Would you like to know about the ingredients used in this step?"
    # And this code handles it accordingly
    elif question_type in ["yes", "no", "repeat", "thanks"]:        
        # If no, await next question from user
        if question_type == "no":
            previous_answer = {
                "answer": "Alright. What else would you like to know?",
                "suggestions": {
                    "What do I do now?": "What do I do now?",
                    "Ingredients this step.": "What ingredients do I need this step?"
                }
            }
            conversation.add_step(question, question_type, previous_answer, recipe.current_step)
            return previous_answer

        # If yes, return appropriate response
        #  GIVEN PREVIOUS QUESTION
        elif question_type == "yes":
            #  If previous question is None there is nothing to respond to
            if previous_question is None:
                previous_answer = "I'm sorry, I'm not sure what you're responding to."
                return previous_answer

            # Return appropriate response based on previous question
            if previous_question in ["next_step", "previous_step", "current_step"]:
                resp = return_ingredients_response(recipe, "step_ingredients")
            elif previous_question in ["first_step"]:
                resp = return_ingredients_response(recipe, get_first=True)
            # elif ...

            # Reset previous question
            previous_question = None
            previous_answer = {
                "answer": resp,
                "suggestions": None
            }
            conversation.add_step(question, question_type, previous_answer, recipe.current_step)
            return previous_answer
        
        elif question_type == "repeat":
            if previous_answer is None:
                return "I don't have anything to repeat."
            conversation.add_step(question, question_type, previous_answer, recipe.current_step)
            return previous_answer
        elif question_type == "thanks":
            return "You're welcome! What other questions do you have?"


    else:
        # TODO: Maybe add "did you mean this?" functionality
        return "I'm sorry, I don't know the answer to that question."
