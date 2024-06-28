# chatbot_text:based_main.py

import os
import nlp_processor
import resources.dataset as ds

# Initialize the ChatBot and NLP_Block instances
# ai = voice_processor.ChatBot(name="PriceNegotiator")
nlp = nlp_processor.NLP_Block(ds.pre_defined_responses)

# Callback function for starting the text based interaction
# of the chatbot with the user
def start_text_based_interaction():
    # Start the interaction
    while True:
        user_input = input('Question: ')
        # print(user_input)
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = nlp.get_response(user_input)
        print("Virtual Assistant: ", response)

# Entry point of the script
if __name__ == "__main__":
    # Run the verification process
    start_text_based_interaction()
