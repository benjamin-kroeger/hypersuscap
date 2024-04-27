import contextlib
import json
import logging.config
from unittest import case

from constants import segments
from open_ai_call import send_message
from typing import Literal

logging.config.fileConfig(
    'logging.config',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)

segments_str = '\n'.join([str(x) for x in segments])


def identify_customer_segment(user_data: str, context_mem: list[dict]) -> str:
    logger.info("Identifying customer segment")
    context = [{'role': 'system',
                'content': "You are a skilled and helpful assistant, that maps a user to a specific segment based on "
                           "how well his profile fits and based on previous messages."
                           "You prioritize the info from the messages"
                           "You reply with just the name of the segment"}]
    context.extend(context_mem)
    prompt = ("User:\n"
              f"{user_data}\n"
              "Segments:\n"
              f"{segments_str}")

    resp = send_message(message=prompt, role='user', context=context).content
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


def craft_first_message(user_data: str,context_mem) -> str:
    logger.info("Crafting first message")
    context = [{'role': 'system',
                'content': "You are a skilled and helpful assistant, greeting a customer that wants to buy an electric vehicle."
                           "You reference data you gat from the users profile and try do deduce his purchase intention to best tailor your response."
                           "You leverage data about how to market to the customer, to immediately make a captivating offer."}]
    context.extend(context_mem)
    prompt = ("User:\n"
              f"{user_data}\n")

    resp = send_message(message=prompt, role='user', context=context).content
    return resp


if __name__ == '__main__':
    with open('/home/benjaminkroeger/Documents/Hackathons/TumAI/hypersuscap/profiles/profile2.json', 'r') as f:
        user_data = str(json.load(f))
    identify_customer_segment(user_data)
