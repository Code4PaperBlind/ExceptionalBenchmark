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

for num in range(11, 1311):
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

        #For Few-shot example
        Fewshot_root_directory = "few_shot/"
        fewshot_example1 = []
        for idx in range(1,5):
            fewshot_image = Fewshot_root_directory+ "ex1/e1-%d.jpg" % idx
            fewshot_example1.append(fewshot_image)

        fewshots1 = []
        if fewshot_example1:
            # Getting the base64 string of the first image
            for fewshot_image_path in fewshot_example1:
                try:
                    with open(fewshot_image_path, "rb") as fewshot_image_file:
                        fewshot_image_bytes = fewshot_image_file.read()
                        fewshot_image = Image.open(io.BytesIO(fewshot_image_bytes))
                        fewshots1.append(fewshot_image)
                except (IOError, OSError) as e:
                    print(f"Error loading image '{fewshot_image_path}': {e}")

        else:
            print("No images found in the directory.")

        fewshot_example2 = []
        for idx2 in range(1,5):
            fewshot_image2 = Fewshot_root_directory+ "ex2/e1-%d.jpg" % idx
            fewshot_example2.append(fewshot_image2)

        fewshots2 = []
        if fewshot_example2:
            # Getting the base64 string of the first image
            for fewshot_image_path2 in fewshot_example2:
                try:
                    with open(fewshot_image_path2, "rb") as fewshot_image_file2:
                        fewshot_image_bytes2 = fewshot_image_file2.read()
                        fewshot_image2 = Image.open(io.BytesIO(fewshot_image_bytes2))
                        fewshots2.append(fewshot_image2)
                except (IOError, OSError) as e:
                    print(f"Error loading image '{fewshot_image_path2}': {e}")

        else:
            print("No images found in the directory.")

        fewshot_example3 = []
        for idx3 in range(1,5):
            fewshot_image3 = Fewshot_root_directory+ "ex3/e1-%d.jpg" % idx
            fewshot_example3.append(fewshot_image3)

        fewshots3 = []
        if fewshot_example3:
            # Getting the base64 string of the first image
            for fewshot_image_path3 in fewshot_example3:
                try:
                    with open(fewshot_image_path3, "rb") as fewshot_image_file3:
                        fewshot_image_bytes3 = fewshot_image_file3.read()
                        fewshot_image3 = Image.open(io.BytesIO(fewshot_image_bytes3))
                        fewshots3.append(fewshot_image3)
                except (IOError, OSError) as e:
                    print(f"Error loading image '{fewshot_image_path3}': {e}")

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
        prompt_few1 = "The First, Example:\n\n"
        prompt_few2 = "The Second, Example:\n\n"
        prompt_few3 = "The Third, Example:\n\n"
        prompt_few_answer = "A. Let's think step by step. The correct order is [1, 2, 3, 4]"

        prompt_cot = "A. Let's think step by step.\n\
                        Once Again, Respond ONLY with the list of numbers 1, 2, 3, 4\n\
                            Once Again, Respond ONLY with the list of numbers 1, 2, 3, 4\n\
                        The correct order is :"

        combined_input = [prompt, prompt_few1, fewshots1[0], fewshots1[1], fewshots1[2], fewshots1[3], prompt_few_answer,
                           prompt, prompt_few2, fewshots2[0], fewshots2[1], fewshots2[2], fewshots2[3], prompt_few_answer,
                           prompt, prompt_few3, fewshots3[0], fewshots3[1], fewshots3[2], fewshots3[3], prompt_few_answer,
                           prompt, prompt_images[0], prompt_images[1], prompt_images[2], prompt_images[3], prompt_cot]

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
df.to_csv('your_directory/CoT+Few-Shot.csv', index=False)
print("done")
