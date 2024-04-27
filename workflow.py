import logging.config

from sub_prompting_modules import craft_first_message, identify_customer_segment, mod_context_segments

import streamlit as st
logging.config.fileConfig(
    'logging.config',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def give_informed_resp(user_data: str, context_memory: list[dict]) -> str:
    # Get customer segment
    inital_context_length = len(context_memory)
    logger.info('Inital_context_length: {}'.format(inital_context_length))
    # get customer segment
    customer_segment = identify_customer_segment(user_data=user_data,context_mem=context_memory)
    #
    request_context = mod_context_segments(current_segment=customer_segment, current_context=context_memory)

    if inital_context_length == 1:
        return craft_first_message(context_mem=request_context, user_data=user_data)
