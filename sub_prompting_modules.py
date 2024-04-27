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
    match current_segment:
        case 'franz':
            current_context.append({'role': 'system', 'content': ''})
        case 'peter':
            current_context.append({'role': 'system', 'content': ''})
        case 'sally':
            current_context.append({'role': 'system', 'content': ''})
        case 'viola':
            current_context.append({'role': 'system', 'content': ''})

    return current_context


def craft_first_message(user_data: str, context_mem) -> str:
    logger.info("Crafting first message")
    # specify how the user data is used to craft the message
    context = [{'role': 'system',
                'content': "You are a skilled and helpful assistant, greeting a mercedes customer and offering insights on electric vehicles."
                           "You reference data you get from the users profile and try do deduce his purchase intention to best tailor your response."
                           "You try to make the introduction as compelling and concise as possible, and highlight features that the user likes."
                           "You only suggest mercedes cars"}]
    context.extend(context_mem)
    # only pass the user data
    prompt = ("User:\n"
              f"{user_data}\n")

    return stream_message(message=prompt, role='user', context=context)


def get_meta_data(context: list[dict]):
    prompt = "retrieve all valuable data from this current context, write a short description of this person"
    return send_message(prompt, "system", context)


def generate_response(user_data: dict, context: list[dict], car_data: str = None):
    if car_data != None:
        full_profile = "[Current profile:]" + str(user_data) + "[Car data:]" + str(car_data)
    else:
        full_profile = "[Current profile]:" + str(user_data)

    system_prompt = "Use this data for your next response: " + get_meta_data([{"role": "user", "content": full_profile}])})
    return send_message(system_prompt, "system", context)
