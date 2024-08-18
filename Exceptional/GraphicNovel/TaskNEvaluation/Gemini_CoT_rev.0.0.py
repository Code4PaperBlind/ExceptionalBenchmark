import os
import random
import base64
import json
import re
import pandas as pd
import ast
import google.generativeai as genai
from google.api_core import client_options as client_options_lib
from google.generativeai import GenerationConfig
from PIL import Image
import io


# Set your Gemini API key
genai.configure(api_key="Enter your API Key")  # Replace with your actual key
client_options = client_options_lib.ClientOptions(api_endpoint="us-east1-generativelanguage.googleapis.com") 

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Function to encode the image (same as before)
#def open_image(image_path):
#    sample_file = PIL.Image.open(image_path)
#    return sample_file

# Function to load image paths (same as before)
def load_images(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

# Path to your image directory
root_directory = "root_directory/images/4_"
df = pd.DataFrame(columns=['No.', 'last_directory', 'Accuracy', 'Suffled image list', 'Result'])

for num in range(1001, 1311):
    image_directory = root_directory + "%d" % num

    if os.path.exists(image_directory):
        images = load_images(image_directory)
        random.shuffle(images)

        base64_images = []
        if images:
            for idx in range(len(images)):
#                opened_image = open_image(images[idx])
#                base64_image = encode_image(opened_image)
                base64_image = encode_image(images[idx])
                base64_images.append(base64_image)

        else:
            print("No images found in the directory.")

        # Gemini API request setup (modified)
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        prompt_images = []
        for image_path in images:
            try:
                with open(image_path, "rb") as image_file:
                    image_bytes = image_file.read()
                    image = Image.open(io.BytesIO(image_bytes))
                    prompt_images.append(image)
            except (IOError, OSError) as e:
                print(f"Error loading image '{image_path}': {e}")

#        for prompt_image in base64_images:
#            prompt_images.append(prompt_image)

        prompt = "Q. The uploaded images represent parts of a story that has been shuffled and consists of 4 images.\
                Arrange images in the correct order.\n\n\
                IMPORTANT: Respond ONLY with the list of numbers 1 to 4 in this format: [1, 2, 3, 4].\n\n"
        prompt_cot = "A. Let's think step by step. ** Print the list of numbers 1 to 4 in this format: [1, 2, 3, 4].** \n\
                    The correct order is :"

        combined_input = [prompt, prompt_images[0], prompt_images[1], prompt_images[2], prompt_images[3], prompt_cot]

        # Create generation configuration
        generation_config = GenerationConfig(
            temperature=0.01,
        )

        # Generate content
        response = model.generate_content(
            combined_input,
            generation_config=generation_config) 

#        content = response.candidates[0].message.content
        print(response.text)  # Print the full Gemini API response
        print(response.usage_metadata)
        content = response.text
        # Extract the value of 'content' and convert it to a list
        # (Assuming the response is a list like '[1, 2, 3, 4]')
        number_list = ast.literal_eval(content)

        # Print the shuffled image names
        suffled_image_list = []
        for image in images:
            file_name = os.path.basename(image)
            num_of_image = re.search(r'\d+', file_name).group()
            suffled_image_list.append(int(num_of_image))
        # print("Shuffled images:", suffled_image_list)

        # Result list initialization
        answer_list_4 = [1, 3, 2, 4]
        result = [0] * len(suffled_image_list)

        # Place shuffled elements at new index using gpt_result
        for i, index in enumerate(number_list):
            result[i] = suffled_image_list[index - 1]

        # Count the number of elements with the same value at the same index
        A = sum(1 for x, y in zip(result, answer_list_4) if x == y)

        # Calculate Accuracy by dividing by the length of the list
        accuracy = A / len(result)

        # image folder name
        last_directory = image_directory.split('/')[-1]
        # add row
        df.loc[len(df)] = [num, last_directory, accuracy, suffled_image_list, result]
        print(df)
    else:
        continue

# save csv file
df.to_csv('your_directory/CoT_Zero.csv', index=False)
print("done")
