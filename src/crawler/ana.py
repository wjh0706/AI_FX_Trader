import re
import g4f
import os
import json
from openai import OpenAI
import httpx

# https://github.com/xtekky/gpt4free?tab=readme-ov-file#chatcompletion

def sort_numeric(file_name):
    #use regular expression to find all numbers in the file names
    numbers = re.findall(r'\d+', file_name)
    # turn the number part into int and return 0 if there's no numbers
    return int(numbers[0]) if numbers else 0




def askGPT(headline,brief):
    # # headline = 'Bank of Japan Keeps Policy Targets Unchanged'

    # # brief = 'The Bank of Japan kept its policy targets unchanged amid expectations among analysts that the bank is likely to end its negative-interest-rate policy early next year.'

    # response = g4f.ChatCompletion.create(
    #     #model=g4f.models.gpt_4,
    #      model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": f"Act as a sentiment analysis service of a financial platform. Based only on the following headline and brief '{headline}\n{brief}', provide a summary of the sentiment for the related forex or the currency of related country. Provide only the sentiment per forex or the currency of related country in JSON format e.g. {{'USD': 'positive'}}. The sentiment can be positive for buy, negative for sell or neutral for hold position. Provide only {{'error':'NA'}}  in JSON format if the headline is unrelated to a forex."}],
    # )  # Alternative model setting

        # #         "role": "user", 
        # #     "content": f"Act as a sentiment analysis service of a financial platform. Based only on the following headline and brief '{headline}\n{brief}', provide a sentiment score for the related forex or the currency of related country. The sentiment score should range from -5 to +5, where -5 strongly suggests selling, 0 suggests holding, and +5 strongly suggests buying. Provide the sentiment in JSON format e.g. {{'USD': 3}}. A score of -5 to 5 represents the sentiment from strongly sell to strongly buy. Provide only {{'error':'NA'}} in JSON format if the headline is unrelated to a forex."
        # # }]
    # response = response.replace('\n', '')
    # pattern = r'\{[^{}]+\}'
    # match = re.search(pattern, response)
    # if match:
    #     response = match.group(0).replace(' ', '')
    # return response
    client = OpenAI(
        base_url="https://oneapi.xty.app/v1", 
        api_key="sk-joT0FAOSsN7XILUu5a86D07fD5Ac4685A50a4d63E64c0731",
        http_client=httpx.Client(
        base_url="https://oneapi.xty.app/v1",
        follow_redirects=True,
    ),
    )

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"Act as a sentiment analysis service of a financial platform. Based only on the following headline and brief '{headline}\n{brief}', provide a sentiment score for the related forex or the currency of related country. The sentiment score should range from -5 to +5, where -5 strongly suggests selling, 0 suggests holding, and +5 strongly suggests buying. Provide the sentiment in JSON format e.g. {{'USD': 3}}. A score of -50 to 50 represents the sentiment from strongly sell to strongly buy. Provide only {{'error':'NA'}} in JSON format if the headline is unrelated to a forex."}
    ]
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the directory containing the JSONL files
jsonl_dir = os.path.join(current_dir, 'forexnews')
ana_dir = os.path.join(current_dir, 'analysis')
os.makedirs(jsonl_dir, exist_ok=True)
os.makedirs(ana_dir, exist_ok=True)

# List files in the folder
files = os.listdir(jsonl_dir)
# Filter JSONL files if needed
jsonl_files = sorted([f for f in files if f.endswith('.jsonl')], key = sort_numeric)[:100]

request_count = 0
    # Iterate over each JSONL file
for file_name in jsonl_files:
    file_path = os.path.join(jsonl_dir, file_name)
    jsonl = []
    with open(file_path, 'r') as file:
        # Read each line (JSON object) from the file
        for line in file:
            # Process JSON object
            data = json.loads(line)
            # Do something with data
            res = askGPT(data['headline'],data['brief'])
            analysis = {
                'response':res, 'headline':data['headline'], 'brief':data['brief'],'date':data['date']
                }
            jsonl.append(analysis)

            request_count += 1
            if request_count % 100 == 0:
                print("Reached 40 files. Waiting for 5 to 10 minutes...")
                time.sleep(random.randint(5*60, 10*60))
            else:
                # Wait for seconds before starting to analyse the next jsonl file
                time.sleep(random.randint(1, 5))


    jsonl_file_path = os.path.join(ana_dir, file_name)
    with open(jsonl_file_path, 'w') as writer:
        for item in jsonl:
            # Convert dictionary to JSON string
            json_line = json.dumps(item)
            # Write JSON string followed by newline character
            writer.write(json_line + '\n')
    
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{file_name} completed at {formatted_time}")