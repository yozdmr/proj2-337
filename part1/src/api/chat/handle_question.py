import requests

from chat.preprocess_question import extract_step_number, extract_clarification_subject, classify_question

from chat.frame_response.frame_ingredients import return_ingredients_response
from chat.frame_response.frame_full_recipe import return_full_recipe_response
from chat.frame_response.frame_time import return_time_response
from chat.frame_response.frame_clarifications import return_specific_clarification_response
from chat.frame_response.frame_methods import return_methods_response, return_all_methods_response
from chat.frame_response.frame_methods import return_methods_response


from process_recipe.recipe import Recipe


global previous_question
global previous_answer
previous_question, previous_answer = None, None


def reset_conversation_state():
    global previous_question
    global previous_answer
    previous_question = None
    previous_answer = None


def handle_question(question: str, recipe: Recipe) -> dict:
    global previous_question
    global previous_answer

    
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
        
        return previous_answer
    
    elif question_type in ["step_methods", "all_methods"]:
        if question_type == "step_methods":
            answer = return_methods_response(recipe)
        elif question_type == "all_methods":
            answer = return_all_methods_response(recipe)
        previous_answer = {
            "answer": answer,
            "suggestions": None
        }
        return previous_answer


    elif question_type in ["how_much_ingredient"]:
        # TODO Xinhe implement this

        # The 'recipe' is passed to this function
        # Do 'recipe.ingredients' to get the dictionary of ingredients
        #  Each ingredient is a dictionary with the following keys:
        # "name"
        # "quantity"
        # "measurement"
        # "descriptor"
        # "preparation"



        return "HOW MUCH!!!!"



        # NOTE: Store your answer in previous_answer then return it
        # so that we can track the conversation history

    elif question_type in ["time"]:
        previous_answer = {
            "answer": return_time_response(recipe),
            "suggestions": None
        }
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
        

        link_buttons = '<div class="mt-4 pt-3 border-t flex flex-row flex-wrap gap-4 border-zinc-300 dark:border-zinc-700">'
        link_buttons += (
            f"<a href='{search_str_google}' class='ref-link-button google font-extrabold flex gap-0' target='_blank' rel='noopener noreferrer' style='letter-spacing: 0;'>"
            f"<span style='color: #2563eb;'>G</span>"
            f"<span style='color: #dc2626;'>o</span>"
            f"<span style='color: #fb923c;'>o</span>"
            f"<span style='color: #2563eb;'>g</span>"
            f"<span style='color: #16a34a;'>l</span>"
            f"<span style='color: #dc2626;'>e</span>"
            f"</a>"
        )
        link_buttons += (
            f"<a href='{search_str_youtube}' class='ref-link-button youtube' target='_blank' rel='noopener noreferrer'>"
            f"You<span>Tube</span>"
            f"</a></div>"
        )

        final_definition_with_buttons = f"<p>{final_definition}</p>{link_buttons}"

        previous_answer = {
            "answer": final_definition_with_buttons,
            "suggestions": None
        }
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
            return previous_answer
        
        elif question_type == "repeat":
            if previous_answer is None:
                return "I don't have anything to repeat."
            return previous_answer
        elif question_type == "thanks":
            return "You're welcome! What other questions do you have?"


    else:
        # TODO: Maybe add "did you mean this?" functionality
        return "I'm sorry, I don't know the answer to that question."
