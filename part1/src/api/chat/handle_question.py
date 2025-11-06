'''
Given a question asked by the user, 
understand WHAT STEP WE ARE AT
WHAT HAPPENS AT THE STEP

WHAT THE USER IS ASKING (clearly)

HOW TO PRESENT INFORMATION TO USER

UPDATE STEP INFORMATION AS NECESSARY

'''


# TODO Implement this function
def classify_question(question: str) -> str:
    return "none"



def handle_question(question: str) -> str:
    
    # TODO Implement this function
    question_type = classify_question(question)

    if question_type == "step_information":
        return "Sample response for step information..."
    elif question_type == "ingredient_information":
        pass
    elif question_type == "tool_information":
        pass
    # etc...

    else:
        return "I'm sorry, I don't know the answer to that question."