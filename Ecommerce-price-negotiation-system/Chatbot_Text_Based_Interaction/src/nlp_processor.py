import os

# for language model
# import torch
#The main package that contains functions to use Hugging Face
import transformers
from transformers import pipeline, Conversation

#Set to avoid warning messages.
transformers.logging.set_verbosity_error()


# Build the AI
class NLP_Block():
    def __init__(self, pre_defined_responses):
        # Load the pre-defined responses to the NLP processing block
        self.pre_defined_responses = pre_defined_responses

        # Load a pipeline. This will download the model checkpoint from huggingface and cache it
        # locally on disk. If model is already available in cache, it will simply use the cached version
        # Download will usually take a long time, depending on network bandwidth
        self.coversational_ai_classifier = pipeline("conversational")

        # Cache usually available at : <<user-home>>.cache\huggingface\hub
        cache_dir = os.path.expanduser('~') + "/.cache/huggingface/hub"
        print("Huggingface Cache directory is : ", cache_dir)

        # Contents of cache directory
        os.listdir(cache_dir)

    def get_response(self, user_input):
        # Check if the input matches any pre-defined question
        if user_input in self.pre_defined_responses:
            return self.pre_defined_responses[user_input]

        # If not, use the conversational model to generate a response
        conversation = Conversation(user_input)
        conversational_ai_results = self.coversational_ai_classifier(conversation, pad_token_id=50256)

        # print(conversational_ai_results)
        # print(conversational_ai_results.generated_responses[0])

        # Extract the generated response
        generated_response = conversational_ai_results.generated_responses[0]

        return generated_response