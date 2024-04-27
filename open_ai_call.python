from openai import OpenAI
client = OpenAI()

messages=[
		{"role": "system", "content": "You are a hellpfull, sales assistant"}
	]

def send_message(message:str, role:str, context:list[dict]):
	context.append({"role": role, "content": message})

	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=context
		)
	
	return completion.choices[0].message

response = send_message("Hello", "system", messages)
print(response.content)
