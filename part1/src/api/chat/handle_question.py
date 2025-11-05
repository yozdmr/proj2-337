'''
Given a question asked by the user, 
understand WHAT STEP WE ARE AT
WHAT HAPPENS AT THE STEP

WHAT THE USER IS ASKING (clearly)

HOW TO PRESENT INFORMATION TO USER

UPDATE STEP INFORMATION AS NECESSARY

'''





def handle_question(question: str) -> str:
    
    # TODO Implement this function
    question_type = classify_question(question)

    if question_type == "step_information":
        pass
    elif question_type == "ingredient_information":
        pass
    elif question_type == "tool_information":
        pass
    # etc...

    # TODO Change this
    return "I don't know..."