import requests
import re
import os
from google import genai
from dotenv import load_dotenv

from chat.preprocess_question import extract_step_number, extract_clarification_subject, classify_question
from chat.frame_response.frame_ingredient_substitution import return_ingredient_substitution_response
from chat.frame_response.frame_ingredient_quantity import get_ingredient_quantity_response

from process_recipe.recipe import Recipe

from chat.conversation_history import ConversationHistory
from chat.llm_context import LLM_CONTEXT

# Load environment variables
load_dotenv()

# Initialize LLM client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash")

conversation = ConversationHistory()


global previous_question
global previous_answer
previous_question, previous_answer = None, None


def reset_conversation_state():
    global previous_question
    global previous_answer
    global chat
    previous_question = None
    previous_answer = None
    chat = client.chats.create(model="gemini-2.5-flash")


def _format_recipe_context(recipe: Recipe) -> str:
    if recipe is None:
        return "No recipe is currently loaded."
    
    context_parts = []
    
    # Recipe name and URL
    if recipe.get_name():
        context_parts.append(f"Recipe Name: {recipe.get_name()}")
    if recipe.get_url():
        context_parts.append(f"Recipe URL: {recipe.get_url()}")
    
    # Ingredients
    ingredients = recipe.get_ingredients()
    if ingredients:
        context_parts.append("\nINGREDIENTS:")
        for ing in ingredients:
            if isinstance(ing, dict):
                parts = []
                if ing.get("descriptor"):
                    parts.append(ing["descriptor"])
                if ing.get("name"):
                    parts.append(ing["name"])
                name = " ".join(parts) if parts else "Unknown ingredient"
                quantity = ing.get("quantity", "")
                measurement = ing.get("measurement", "")
                prep = ing.get("preparation", "")
                
                ing_str = f"  - {name}"
                if quantity or measurement:
                    ing_str += f": {quantity} {measurement}".strip()
                if prep:
                    ing_str += f" ({prep})"
                context_parts.append(ing_str)
            else:
                context_parts.append(f"  - {ing}")
    
    # Steps
    steps = recipe.get_steps()
    if steps:
        context_parts.append("\nDIRECTIONS:")
        for step in steps:
            step_num = step.get("step_number", "?")
            desc = step.get("description", "")
            context_parts.append(f"\nStep {step_num}: {desc}")
            
            # Add step-specific details
            step_ingredients = step.get("ingredients", [])
            step_tools = step.get("tools", [])
            step_methods = step.get("methods", [])
            step_time = step.get("time", {})
            step_temp = step.get("temperature", {})
            
            if step_ingredients:
                if isinstance(step_ingredients[0], str):
                    ing_list = ", ".join(step_ingredients)
                else:
                    ing_list = ", ".join([str(i.get("name", i)) for i in step_ingredients])
                context_parts.append(f"  Ingredients: {ing_list}")
            if step_tools:
                context_parts.append(f"  Tools: {', '.join(step_tools)}")
            if step_methods:
                context_parts.append(f"  Methods: {', '.join(step_methods)}")
            if step_time:
                time_info = []
                if step_time.get("prep"):
                    time_info.append(f"Prep: {step_time['prep']}")
                if step_time.get("cook"):
                    time_info.append(f"Cook: {step_time['cook']}")
                if step_time.get("total"):
                    time_info.append(f"Total: {step_time['total']}")
                if time_info:
                    context_parts.append(f"  Time: {'; '.join(time_info)}")
            if step_temp:
                temp_info = []
                if step_temp.get("oven"):
                    temp_info.append(f"Oven: {step_temp['oven']}")
                if step_temp.get("stovetop"):
                    temp_info.append(f"Stovetop: {step_temp['stovetop']}")
                if temp_info:
                    context_parts.append(f"  Temperature: {'; '.join(temp_info)}")
    
    return "\n".join(context_parts)


def _get_current_step_context(recipe: Recipe) -> str:
    if recipe is None or recipe.current_step is None:
        return ""
    
    step = recipe.current_step
    context_parts = [f"\nCurrent Step: {step.step_number}"]
    context_parts.append(f"Description: {step.description}")
    
    if step.ingredients:
        if isinstance(step.ingredients[0], str):
            ing_list = ", ".join(step.ingredients)
        else:
            ing_list = ", ".join([str(i.get("name", i)) for i in step.ingredients])
        context_parts.append(f"Ingredients: {ing_list}")
    if step.tools:
        context_parts.append(f"Tools: {', '.join(step.tools)}")
    if step.methods:
        context_parts.append(f"Methods: {', '.join(step.methods)}")
    if step.time:
        time_info = []
        if step.time.get("prep"):
            time_info.append(f"Prep: {step.time['prep']}")
        if step.time.get("cook"):
            time_info.append(f"Cook: {step.time['cook']}")
        if step.time.get("total"):
            time_info.append(f"Total: {step.time['total']}")
        if time_info:
            context_parts.append(f"Time: {'; '.join(time_info)}")
    if step.temperature:
        temp_info = []
        if step.temperature.get("oven"):
            temp_info.append(f"Oven: {step.temperature['oven']}")
        if step.temperature.get("stovetop"):
            temp_info.append(f"Stovetop: {step.temperature['stovetop']}")
        if temp_info:
            context_parts.append(f"Temperature: {'; '.join(temp_info)}")
    
    return "\n".join(context_parts)


def _call_llm(question: str, recipe: Recipe, question_type: str = None, additional_context: str = "", recipe_context_text: str = None) -> str:
    global chat
    
    # Format recipe context
    recipe_context = _format_recipe_context(recipe)
    
    # Add current step context if available
    current_step_context = _get_current_step_context(recipe)
    
    # Build prompt
    prompt_parts = [f"Instructions:{LLM_CONTEXT}"]
    
    if question_type:
        prompt_parts.append(f"\nQuestion Type: {question_type}")
    
    prompt_parts.append(f"\nRecipe:\n{recipe_context}")
    
    if current_step_context:
        prompt_parts.append(current_step_context)
    
    # Add recipe context text as secondary source of information
    if recipe_context_text:
        prompt_parts.append(f"\n\nAdditional Recipe Context (from original HTML):\n{recipe_context_text}")
    
    if additional_context:
        prompt_parts.append(f"\nAdditional Context: {additional_context}")
    
    prompt_parts.append(f"\nUser Question: {question}")
    
    prompt = "\n".join(prompt_parts)
    
    # Send message using the chat session
    response = chat.send_message(prompt)
    return response.text

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



def handle_question(question: str, recipe: Recipe, recipe_context_text: str = None) -> dict:
    global previous_question
    global previous_answer

    conversation.print_history()

    
    question_type = classify_question(question)
    print("\t", question_type)

    if question_type in ["recipe"]:
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)
        previous_answer = {
            "answer": answer,
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

        # Call LLM to generate response about the step
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)
        
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
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)
        
        if question_type == "step_methods":
            previous_answer = {
                "answer": answer,
                "suggestions": {
                    "What ingredients do I need?": "What ingredients do I need in this step?",
                    "What tools should I use?": "What tools should I use in this step?",
                    "What do I do next?": "What do I do next?",
                }
            }
        elif question_type == "all_methods":
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
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)
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
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)
        
        if question_type == "step_tools":
            previous_answer = {
                "answer": answer,
                "suggestions": {
                    "What ingredients do I need?": "What ingredients do I need in this step?",
                    "How long will this step take?": "How long will this step take?",
                    "What do I do next?": "What do I do next?",
                }
            }
        elif question_type == "all_tools":
            previous_answer = {
                "answer": answer,
                "suggestions": {
                    "What ingredients does this recipe need?": "What ingredients for the whole recipe?",
                    "What do I do next?": "What do I do next?",
                }
            }

        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    elif question_type in ["how_much_ingredient", "vague_quantity"]:
        
        if question_type == "vague_quantity":
            # Look at previous step in the conversation
            prev_node = conversation.current
            
            if prev_node is None or prev_node.step is None:
                answer_text = "I'm not sure what you're referring to."
            else:
                prev_step = prev_node.step

                # Get ingredients from the previous step
                ingredients = prev_step.ingredients
                num_ingredients = len(ingredients)
                
                if num_ingredients == 1:
                    # Find the ingredient dict from the recipe that matches the ingredient name
                    ingredient_name = ingredients[0]
                    recipe_ingredients = _get_ingredient_list(recipe)
                    
                    # Find matching ingredient dict
                    matched_ing = None
                    ingredient_name_norm = _normalize_text_for_match(ingredient_name)
                    for ing in recipe_ingredients:
                        if isinstance(ing, dict):
                            ing_name = str(ing.get("name") or "").strip()
                            ing_name_norm = _normalize_text_for_match(ing_name)
                            # Check if the ingredient name matches (substring or exact match)
                            if ingredient_name_norm in ing_name_norm or ing_name_norm in ingredient_name_norm:
                                matched_ing = ing
                                break
                    
                    # Use LLM with ingredient context
                    ing_context = f"The user is asking about the quantity of {ingredient_name} from the previous step."
                    answer_text = _call_llm(question, recipe, question_type, ing_context, recipe_context_text=recipe_context_text)
                elif num_ingredients == 0:
                    answer_text = "I couldn't find any ingredients in the previous step."
                else:
                    # Join the ingredients list with commas
                    ingredient_list = ", ".join(ingredients)
                    answer_text = (
                        f"I'm not sure which of these ingredients you're referring to: {ingredient_list}."
                        "\nPlease ask again and be more specific."
                    )
            
            previous_answer = {
                "answer": f"<p>{answer_text}</p>",
                "suggestions": None
            }
            conversation.add_step(question, question_type, previous_answer, recipe.current_step)
            return previous_answer

        elif question_type == "how_much_ingredient":
            ing = _best_match_ingredient_from_question(question, recipe)
            # Use LLM with ingredient context
            ing_context = f"The user is asking about the quantity of {ing.get('name', 'an ingredient') if ing else 'an ingredient'}."
            answer_text = _call_llm(question, recipe, question_type, ing_context, recipe_context_text=recipe_context_text)

            suggestions = {
                "What do I do next?": "What do I do next?",
            }
            if ing and ing.get("name"):
                suggestions["What can I use instead?"] = f"What can I use instead of {ing['name']}?"

            previous_answer = {
                "answer": f"<p>{answer_text}</p>",
                "suggestions": suggestions,
            }
            conversation.add_step(question, question_type, previous_answer, recipe.current_step)
            return previous_answer

    elif question_type in ["replacement_ingredient"]:
        # Ingredient substitution, e.g. "What can I use instead of butter?"
        # Still use the helper function for API calls, but enhance with LLM
        answer, ingr = return_ingredient_substitution_response(recipe, question)
        
        # Enhance with LLM if we have ingredient info
        if ingr:
            llm_answer = _call_llm(question, recipe, question_type, f"The user is asking about substitutes for {ingr}.", recipe_context_text=recipe_context_text)
            # Combine both responses - LLM can provide additional context
            if answer and llm_answer:
                answer = f"{answer}\n\n{llm_answer}"

        previous_answer = {
            "answer": answer,
            "suggestions": {
                "How much do I need?": f"How much {ingr} do I need?",
                "What do I do next?": "What do I do next?",
            },
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer
    
    elif question_type in ["vague_item", "vague_method"]:
        # Look at previous step in the conversation
        prev_node = conversation.current
        
        if prev_node is None or prev_node.step is None:
            answer_text = "I'm not sure what you're referring to."
        else:
            prev_step = prev_node.step
            
            if question_type == "vague_method":
                # Get methods from the previous step
                methods = prev_step.methods
                num_methods = len(methods)
                
                if num_methods == 0:
                    answer_text = "I couldn't find any methods in the previous step."
                elif num_methods == 1:
                    # Use LLM for clarification
                    method_name = methods[0]
                    clarification_question = f"How do I {method_name}?"
                    answer_text = _call_llm(clarification_question, recipe, "clarification_specific", 
                                           f"The user is asking about the method '{method_name}' from the previous step.", recipe_context_text=recipe_context_text)
                    
                    # Prepare search URLs
                    search_term = method_name.replace(" ", "+")
                    search_str_google = f"https://www.google.com/search?q={search_term}"
                    search_str_youtube = f"https://www.youtube.com/results?search_query={search_term}"
                    
                    previous_answer = {
                        "answer": f"<p>{answer_text}</p>",
                        "suggestions": {
                            "Google": search_str_google,
                            "YouTube": search_str_youtube
                        }
                    }
                    conversation.add_step(question, question_type, previous_answer, recipe.current_step)
                    return previous_answer
                else:
                    # Join the methods list with commas
                    methods_list = ", ".join(methods)
                    answer_text = (
                        f"I'm not sure which of these methods you're referring to: {methods_list}."
                        "\nPlease ask again and be more specific."
                    )
            
            else:  # vague_item
                # Check both tools and ingredients from the previous step
                tools = prev_step.tools
                ingredients = prev_step.ingredients
                
                # Combine tools and ingredients for item checking
                items = []
                if tools:
                    items.extend(tools)
                if ingredients:
                    items.extend(ingredients)
                
                num_items = len(items)
                
                if num_items == 0:
                    answer_text = "I couldn't find any tools or ingredients in the previous step."
                elif num_items == 1:
                    # Use LLM for clarification
                    item_name = items[0]
                    clarification_question = f"What is {items[0]}?"
                    answer_text = _call_llm(clarification_question, recipe, "clarification_specific",
                                           f"The user is asking about '{item_name}' from the previous step.", recipe_context_text=recipe_context_text)
                    
                    # Prepare search URLs
                    search_term = clarification_question.replace(" ", "+")
                    search_str_google = f"https://www.google.com/search?q={search_term}"
                    search_str_youtube = f"https://www.youtube.com/results?search_query={search_term}"
                    
                    previous_answer = {
                        "answer": f"<p>{answer_text}</p>",
                        "suggestions": {
                            "Google": search_str_google,
                            "YouTube": search_str_youtube
                        }
                    }
                    conversation.add_step(question, question_type, previous_answer, recipe.current_step)
                    return previous_answer
                else:
                    # Join the items list with commas
                    items_list = ", ".join(items)
                    answer_text = (
                        f"I'm not sure which of these items you're referring to: {items_list}."
                        "\nPlease ask again and be more specific."
                    )

        previous_answer = {
            "answer": f"<p>{answer_text}</p>",
            "suggestions": None
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    elif question_type in ["time"]:
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)
        previous_answer = {
            "answer": answer,
            "suggestions": None
        }
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer

    
    elif question_type in ["temperature"]:
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)
        previous_answer = {"answer": answer, "suggestions": None}
        conversation.add_step(question, question_type, previous_answer, recipe.current_step)
        return previous_answer 


    

    elif question_type in ["clarification_specific"]:
        # Prepare search URLs for both types
        question_search_term = question.replace(" ", "+")
        search_str_google = f"https://www.google.com/search?q={question_search_term}"
        search_str_youtube = f"https://www.youtube.com/results?search_query={question_search_term}"
        
        answer = _call_llm(question, recipe, question_type, recipe_context_text=recipe_context_text)

        previous_answer = {
            "answer": answer,
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

        # If yes, return appropriate response dynamically using LLM
        elif question_type == "yes":
            # Get the previous conversation node (the bot's last response) to understand context
            # conversation.current points to the last node added, which is the bot's previous response
            prev_node = conversation.current if conversation.current else None
            
            if prev_node is None:
                previous_answer = {
                    "answer": "I'm sorry, I'm not sure what you're responding to.",
                    "suggestions": None
                }
                conversation.add_step(question, question_type, previous_answer, recipe.current_step)
                return previous_answer
            
            # Get the bot's previous response to understand what question was asked
            prev_answer = prev_node.answer
            prev_answer_text = prev_answer.get("answer", "") if isinstance(prev_answer, dict) else str(prev_answer)
            prev_question = prev_node.question
            prev_question_type = prev_node.question_type
            
            # Build context for the LLM to understand what the user is saying "yes" to
            context_parts = [
                f"Conversation Context:",
                f"- Previous user question: {prev_question}",
                f"- Previous question type: {prev_question_type}",
                f"- Bot's previous response: {prev_answer_text}",
                "",
                "The user is responding 'yes' to a question or offer in the bot's previous response.",
                "Please analyze the bot's previous response to determine what the user is saying yes to,",
                "and provide an appropriate, helpful response based on that context."
            ]
            
            # Use LLM to dynamically generate response based on conversation context
            # Pass the actual question "yes" but provide rich context
            additional_context = "\n".join(context_parts)
            resp = _call_llm("The user said 'yes'. What should I respond?", recipe, question_type, additional_context, recipe_context_text=recipe_context_text)

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
