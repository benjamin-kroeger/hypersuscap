import json

from constants import segments
from open_ai_call import send_message
from openai import OpenAI
client = OpenAI()



def get_profile(profile_num:int):
    path = "./profiles/profile" + str(profile_num) + ".json"
    with open(path, "r") as file:
        data = json.load(file)

    return data['demographics']





if __name__=="__main__":

    context = [  {"role": "system", "content": "You are an helpfull sales assistant. Allways tailor your responses to the current profile only adjust the language and style of your resonse. Include car data in your response if available."} ]

    context.append({"role": "user", "content": "Hi i would like to see what youve got for me"})
    print(generate_response(1, context))
    #print(generate_response("I would like a fast and cool looking car what can you recommend?", "user", context).content)
