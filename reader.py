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


def get_meta_data(context:list[dict]):
    prompt = "retrieve all valuable data from this current context, write a short description of this person"
    return send_message(prompt, "system", context).content

def generate_response(profile_num:int, context:list[dict], car_data:dict=None): 
    
    profile = get_profile(profile_num)
    if car_data != None:
        full_profile = "[Current profile:]" + str(profile) + "[Car data:]" + str(data)
    else:
        full_profile = "[Current profile]:" + str(profile)

    context.append({"role": "system", "content": "If preferable use this data about the current context: " + get_meta_data(context)})
    return send_message(full_profile, "assistant", context).content


if __name__=="__main__":

    context = [  {"role": "system", "content": "You are an helpfull sales assistant. Allways tailor your responses to the current profile only adjust the language and style of your resonse. Include car data in your response if available."} ]

    context.append({"role": "user", "content": "Hi i would like to see what youve got for me"})
    print(generate_response(1, context))
    #print(generate_response("I would like a fast and cool looking car what can you recommend?", "user", context).content)
