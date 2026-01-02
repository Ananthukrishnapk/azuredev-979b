from openai import OpenAI

endpoint = "https://johngeorge-2562-resource.openai.azure.com/openai/v1/"
deployment_name = "gpt-4o"
api_key = "<your-api-key>"

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
    temperature=0.7,
)

print(completion.choices[0].message)