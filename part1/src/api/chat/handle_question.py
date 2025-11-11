import re
from chat.question_bank import QUESTION_BANK
from chat.frame_response.frame_ingredients import return_ingredients_response

from process_recipe.recipe import Recipe


global previous_question
global previous_answer
previous_question = None
previous_answer = None

def classify_question(question: str) -> str:
    # Normalize question: lowercase, remove punctuation, normalize whitespace
    question_normalized = question.lower().strip()
    question_normalized = re.sub(r"[^\w\s]", "", question_normalized)
    question_normalized = " ".join(question_normalized.split())
    
    # Get question words (excluding common stop words for better matching)
    stop_words = {"a", "an", "the", "is", "are", "what", "which", "when", "where", "who", "why", "yes", "no"}
    question_words = set(w for w in question_normalized.split() if w not in stop_words)
    
    best_match = None
    best_match_score = 0
    exact_match_found = False
    
    # Check each question bank for matches
    for bank in QUESTION_BANK:
        for key_phrase, category in bank.items():
            # Normalize key phrase the same way
            key_normalized = key_phrase.lower().strip()
            key_normalized = re.sub(r"[^\w\s]", "", key_normalized)
            key_normalized = " ".join(key_normalized.split())
            
            # Get key words (excluding stop words)
            key_words = set(w for w in key_normalized.split() if w not in stop_words)
            
            # Step 1: Exact match (highest priority - should win over everything)
            if key_normalized == question_normalized:
                exact_match_found = True
                best_match = category
                best_match_score = float('inf')  # Highest possible score
                continue
            
            # Step 2: Exact substring match (only if no exact match found yet)
            if not exact_match_found:
                if key_normalized in question_normalized or question_normalized in key_normalized:
                    # For single-word questions, prevent matching against long multi-word keys
                    # This prevents "step" from matching "ingredients are used in this step"
                    question_word_count = len(question_words)
                    key_word_count = len(key_words)
                    
                    # Single-word questions should only match single-word or two-word keys
                    if question_word_count == 1 and key_word_count > 2:
                        continue
                    
                    # Prefer longer matches (more specific)
                    score = len(key_normalized)
                    if score > best_match_score:
                        best_match = category
                        best_match_score = score
                # Step 3: Word overlap (makes it more flexible)
                elif key_words and question_words:
                    # Calculate overlap: how many key words appear in question
                    overlap = len(key_words & question_words)
                    # Score based on overlap ratio (prefer matches with more overlap)
                    overlap_ratio = overlap / len(key_words)
                    # Also consider the length of the key (prefer longer, more specific keys)
                    score = overlap_ratio * len(key_normalized)
                    
                    # Require at least 50% word overlap to consider it a match
                    if overlap_ratio >= 0.5 and score > best_match_score:
                        best_match = category
                        best_match_score = score
    
    return best_match if best_match else "none"


def handle_question(question: str, recipe: Recipe) -> dict:
    global previous_question
    global previous_answer

    
    question_type = classify_question(question)
    print("\t", question_type)

    if question_type in ["next_step", "previous_step", "current_step", "first_step"]:

        # Set previous question, because the bot's response
        #   asks yes/no question at the end
        previous_question = question_type

        stepped = True

        if question_type == "first_step":
            # Avoid updating recipe.first_step so that it remains the same 
            first_step = recipe.first_step
            answer = f"<h4 class='chat-header'>Step {first_step.step_number}:</h4><p>{first_step.description}</p>\n<p>Would you like to know about the ingredients used in this step?</p>"

        else:
            if question_type == "next_step":
                curr_step, stepped = recipe.step_forward()
            elif question_type == "previous_step":
                curr_step, stepped = recipe.step_backward()
            elif question_type == "current_step":
                curr_step = recipe.current_step

            # Construct response
            answer = f"<h4 class='chat-header'>Step {curr_step.step_number}:</h4><p>{curr_step.description}</p>\n<p>Would you like to know about the ingredients used in this step?</p>"
        
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
                return "There are no more steps in this recipe."
            elif question_type == "previous_step":
                return "There are no previous steps in this recipe."
        
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
        step = recipe.current_step
        tinfo = getattr(step, "time", None) or {}
        def fmt(sec: int) -> str:
            m, s = divmod(int(sec), 60)
            h, m = divmod(m, 60)
            if h: 
                return f"{h} hr {m} min" if m else f"{h} hr"
            if m: 
                return f"{m} min"
            return f"{s} sec"
        answer = "I couldn't find an explicit time for this step."
        if tinfo:
            if tinfo.get("min_seconds") is not None and tinfo.get("max_seconds") is not None:
                if tinfo["min_seconds"] == tinfo["max_seconds"]:
                    answer = f"This step takes about {fmt(tinfo['min_seconds'])}."
                else:
                    answer = f"This step takes about {fmt(tinfo['min_seconds'])}–{fmt(tinfo['max_seconds'])}."
            elif tinfo.get("duration"):
                answer = f"This step takes {tinfo['duration']}."
            elif tinfo.get("qualitative"):
                answer = " / ".join(tinfo["qualitative"])
        previous_answer = {"answer": answer, "suggestions": None}
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


    # Affirmation responses (in response to a yes/no question from the previous bot response)
    #  As of right now, when asking for STEP information, the bot will ask:
    #    "Would you like to know about the ingredients used in this step?"
    # And this code handles it accordingly
    elif question_type in ["yes", "no", "repeat"]:        
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
            return previous_answer


    else:
        # TODO: Maybe add "did you mean this?" functionality
        return "I'm sorry, I don't know the answer to that question."
