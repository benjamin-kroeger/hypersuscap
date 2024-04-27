import json

from constants import segments
from open_ai_call import send_message
from openai import OpenAI
client = OpenAI()




context = [
        
        {"role": "system", "content": "You are an helpfull sales assistant. Allways tailor your responses to the current profile only adjust the language and style of your resonse."} 
        ]

def get_profile(profile_num:int):
    path = "./profiles/profile" + str(profile_num) + ".json"
    with open(path, "r") as file:
        data = json.load(file)

    return data


def generate_response(profile_num:int, context:list[dict]): 
    
    profile = get_profile(profile_num)
    full_profile = "[Current profile]:" + str(profile)
    return send_message(full_profile, "system", context).content


if __name__=="__main__":
    context.append({"role": "user", "content": "Hi i would like to see what youve got for me"})
    print(generate_response(1, context))
    #print(generate_response("I would like a fast and cool looking car what can you recommend?", "user", context).content)
