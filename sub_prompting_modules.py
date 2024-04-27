import contextlib
import json
import logging.config
from unittest import case

from constants import segments
from open_ai_call import send_message, stream_message
from typing import Literal

logging.config.fileConfig(
    'logging.config',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)

segments_str = '\n'.join([str(x) for x in segments])


def identify_customer_segment(user_data: str, context_mem: list[dict]) -> str:

    logger.info("Identifying customer segment")
    # specify the way how a user is mapped to a segment
    context = [{'role': 'system',
                'content': "You are a skilled and helpful assistant, that maps a user to a specific segment based on "
                           "how well his profile fits and based on previous messages."
                           "You prioritize the info from the messages"
                           "You reply with just the name of the segment"}]
    context.extend(context_mem)
    # Pass the user data and every one of the 4 segments as reference
    prompt = ("User:\n"
              f"{user_data}\n"
              "Segments:\n"
              f"{segments_str}")
    # get classification from openai
    resp = send_message(message=prompt, role='user', context=context)
    logger.info(f"Identified customer segment {resp}")

    return resp


def mod_context_segments(current_segment: Literal['franz', 'peter', 'sally', 'viola'], current_context: list[dict]) -> list[dict]:
    # match current_segment:
        # case 'franz':
        #     current_context.append({'role': 'system', 'content': ''})
        # case 'peter':
        #     current_context.append({'role': 'system', 'content': ''})
        # case 'sally':
        #     current_context.append({'role': 'system', 'content': ''})
        # case 'viola':
        #     current_context.append({'role': 'system', 'content': ''})

    return current_context


def craft_first_message(user_data: str, context_mem) -> str:
    logger.info("Crafting first message")
    # specify how the user data is used to craft the message
    context = [{'role': 'system',
                # 'content': "You are a skilled and helpful assistant, greeting a mercedes customer and offering insights on electric vehicles."
                #            "You reference data you get from the users profile and try do deduce his purchase intention to best tailor your response."
                #            "You try to make the introduction as compelling and concise as possible, and highlight features that the user likes."
                #            "You only suggest mercedes cars"
                #            "Keep your message as short and engaging as possible, long messages are not appreciated."}]
                'content': "You are a skilled and helpful assistant, greeting a Mercedes customer and offering insights on electric vehicles. You reference data from the user's profile and try to deduce their purchase intention to best tailor your response. You aim to make the introduction as compelling and concise as possible, highlighting features that the user likes. You only suggest Mercedes cars. Keep your message as short and engaging as possible, as long messages are not appreciated."
                }]
    context.extend(context_mem)
    # only pass the user data
    prompt = ("User:\n"
              f"{user_data}\n")

    return stream_message(message=prompt, role='user', context=context, max_tokens=500)


def get_meta_data(context: str):
    system_prompt = "You are a skilled and helpful assistant, that extracts all valuable data from the context and summarizes it in natural language"

    messages = [{"role": "system", "content": system_prompt}]

    prompt = f"""Please summarize the following data:
    {context}
    """
    return send_message(prompt, "user", messages, max_tokens=500)


def generate_response(user_data, context: list[dict], car_data: str):
    if car_data != None:
        full_profile = "[Current profile:]" + str(user_data) + "[Car data:]" + car_data
    else:
        full_profile = "[Current profile]:" + str(user_data)

    print(user_data)
    print(car_data)

    system_prompt = "You are an asisstant that helps high end customers in their decission for an Mercedes electric vehicle. You have access to the users profile, Mercedes car database and the chat history. You should use this data to craft a response."

    context_new = context.copy()
    context_new.extend([{"role": "system", "content": system_prompt}])

    prompt = f"""Use the following use the following data to craft a response:

    User data: {get_meta_data(str(full_profile))}

    Retrieved data from Mercedes database: {car_data}

    Chat history: {context}

    Generated response: """


    print(system_prompt)    
    return stream_message(prompt, "user", context_new, temperature=0.25, max_tokens=500)
