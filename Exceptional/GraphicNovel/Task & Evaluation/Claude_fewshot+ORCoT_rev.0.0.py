import os
import random
import base64
import re
import pandas as pd
import ast
import requests
from PIL import Image
import io
import json

# Set your Claude API key
CLAUDE_API_KEY = "YOUR API KEY"
API_URL = "https://api.anthropic.com/v1/messages"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_images(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

def load_fewshot_examples(directory):
    examples = []
    for i in range(1, 4):  # Load 3 examples
        example = []
        for j in range(1, 5):  # Each example has 4 images
            image_path = os.path.join(directory, f"ex{i}/e1-{j}.jpg")
            example.append(image_path)
        examples.append(example)
    return examples

def claude_api_request(prompt, images, fewshot_examples):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01"
    }

    content = []
    
    # 1. Text for test question (initial prompt)
    content.append({"type": "text", "text": prompt})

    # 2-7. Few-shot examples
    for i, example in enumerate(fewshot_examples):
        # Text for few-shot example
        content.append({"type": "text", "text": f"The {['First', 'Second', 'Third'][i]}, Example:\n\n"})
        # Images for few-shot example
        for img_path in example:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": encode_image(img_path)}})
        content.append({"type": "text", "text": "A. Let's think step by step. The correct order is [1, 2, 3, 4]"})

    # 8. Text for test question (repeated)
    content.append({"type": "text", "text": prompt})

    # 9. Images for test question
    for img in images:
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img}})

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1000,
        "temperature": 0,
        "messages": [{"role": "user", "content": content}]
    }

    response = requests.post(API_URL, json=data, headers=headers)
    return response.json()

# Path to your image directory
root_directory = "root_directory/comics/4_cropped/4_"
fewshot_directory = "fewshot_directory/comics/few_shot/"
df = pd.DataFrame(columns=['No.', 'last_directory', 'Accuracy', 'Shuffled image list', 'Result'])

# Load few-shot examples
fewshot_examples = load_fewshot_examples(fewshot_directory)

# Define the prompt
prompt = "Q. The uploaded images represent parts of a story that has been shuffled and consists of 4 images.\
        Arrange images in the correct order.\n\n\
        IMPORTANT: Respond ONLY with the list of numbers 1 to 4 in this format: [1, 2, 3, 4].\n\n\
        A. Let's think step by step.\n\
        Once Again, Respond ONLY with the list of numbers 1, 2, 3, 4\n\
        Once Again, Respond ONLY with the list of numbers 1, 2, 3, 4\n\
        The correct order is :"

for num in range(1, 1311):
    image_directory = root_directory + "%d" % num

    if os.path.exists(image_directory):
        images = load_images(image_directory)
        random.shuffle(images)

        base64_images = []
        if images:
            for idx in range(len(images)):
                base64_image = encode_image(images[idx])
                base64_images.append(base64_image)
        else:
            print("No images found in the directory.")
            continue

        # Claude API request
        response = claude_api_request(prompt, base64_images, fewshot_examples)

        print("Full API Response:")
        print(json.dumps(response, indent=2))

        # Extract content from Claude's response
        if 'content' in response and isinstance(response['content'], list) and len(response['content']) > 0:
            text_content = response['content'][0]['text']
            print("Extracted Text Content:", text_content)
            
            try:
                # Extract the list from the text content
                number_list = ast.literal_eval(re.search(r'\[.*?\]', text_content).group())
                if isinstance(number_list, list) and len(number_list) == 4:
                    print("Extracted Number List:", number_list)
                else:
                    print("Unexpected format in text content")
                    continue
            except (ValueError, SyntaxError, AttributeError) as e:
                print("Error parsing text content:", e)
                continue
        elif 'error' in response:
            print("API Error:", response['error'])
            continue
        else:
            print("Unexpected response structure:", response)
            continue

        # Print the shuffled image names
        shuffled_image_list = []
        for image in images:
            file_name = os.path.basename(image)
            num_of_image = re.search(r'\d+', file_name).group()
            shuffled_image_list.append(int(num_of_image))

        # Result list initialization
        answer_list_4 = [1, 3, 2, 4]
        result = [0] * len(shuffled_image_list)

        # Place shuffled elements at new index using claude_result
        for i, index in enumerate(number_list):
            result[i] = shuffled_image_list[index - 1]

        # Count the number of elements with the same value at the same index
        A = sum(1 for x, y in zip(result, answer_list_4) if x == y)

        # Calculate Accuracy by dividing by the length of the list
        accuracy = A / len(result)

        # image folder name
        last_directory = image_directory.split('/')[-1]
        # add row
        df.loc[len(df)] = [num, last_directory, accuracy, shuffled_image_list, result]
        print(df)
    else:
        continue

# save csv file
df.to_csv('csv_directory/Claude_ORCoT+Few-Shot_1-1310.csv', index=False)
print("done")