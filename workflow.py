import logging.config

from sub_prompting_modules import craft_first_message, identify_customer_segment, mod_context_segments, generate_response

from retriever import Retriever

import streamlit as st

logging.config.fileConfig(
    'logging.config',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)

retriever = Retriever("sqlite:///electric_configurations.db")
def give_informed_resp(user_data: str, context_memory: list[dict], first: bool = False) -> str:

    # get customer segment
    customer_segment = identify_customer_segment(user_data=user_data, context_mem=context_memory)

    # add answering instructions based on the segment
    request_context = mod_context_segments(current_segment=customer_segment, current_context=context_memory)

    if first:
        return craft_first_message(context_mem=request_context, user_data=user_data)

    # Data retriever
    retrieved_evidence = retriever.retrieve(context_memory[-1].content, chat_history=context_memory[:-1])

    # Answer generation
<<<<<<< HEAD
    generate_response(user_data, context_memory, retrieved_evidence)    
=======


>>>>>>> 7a5d567cf9d669002d26d19e1fb83f9dd7e28b66
    # CTA enhancer
