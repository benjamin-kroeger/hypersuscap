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


def generate_response(user_data, context: list[dict], car_data: str, customer_segment: str):
        
    full_profile = "[Current profile:]" + str(user_data) + "[Car data:]" + car_data

    print(user_data)
    print(car_data)

    system_prompt = "You are an asisstant that helps high end customers in their decission for an Mercedes electric vehicle." 

    if customer_segment == "franz":
        system_prompt += "Given the demographic composition and preferences of our customer base, please ensure that responses are crafted with fitting language and speech patterns. This demographic, comprising 4% of our international clientele, demonstrates a penchant for traditional transactions and values personal service. They are typically affluent males, aged 39 and above, residing in rural areas, smaller cities, or suburbs, often in leadership roles or enjoying retirement. This segment boasts high earners who prioritize luxury, convenience, and quality over price sensitivity. Their loyalty to established brands and service providers is unwavering, as they prioritize brand prestige, maintenance, and resale value. Additionally, they have a keen interest in classic luxury experiences and traditional pastimes such as tennis, theater, and cruising. Please ensure that marketing initiatives align with our positioning strategy of high-end luxury, targeting this discerning demographic with a focus on personalized service and luxury experiences."
        pass
    elif customer_segment == "peter":
        system_prompt += "Given the demographic composition and psychological inclinations of our customer base, please ensure that responses are crafted with fitting language and speech patterns. This segment, comprising 8% of our global clientele, exhibits a strong presence in key markets such as China, Brazil, and Canada, with an average age of 34. They are predominantly urban, often holding management roles and boasting high incomes, symbolizing affluent professionals with growth potential. Their preference for new, young luxury compact SUVs underscores their passion for cars and desire for exclusive experiences. While cost-aware, they prioritize quality and performance, especially from high-end brands in various sectors, including tech and luxury EVs. Marketing initiatives should focus on premium positioning, targeting this digitally savvy audience with a mix of digital and personalized services. Please ensure responses resonate with their values of luxury, sustainability, and quality service, emphasizing a clear value proposition tailored to their preferences. The EQC is the outdated electric SUV model, the EQE and EQS SUVs are the new ones."
        pass
    elif customer_segment == "sally":
        system_prompt += "Given the demographic composition and psychological tendencies of our customer base, please ensure that responses are crafted with fitting language and speech patterns. This segment, representing 14% of our global clientele, exhibits a strong presence in key markets such as China, France, and Switzerland. With an average age of 32, they are predominantly urban, with many in management roles and boasting high disposable incomes. This demographic, though slightly skewed towards males, features significant representation from childless couples. Their preference for new entry-level luxury vehicles, particularly modern compact executive cars, reflects their inclination towards luxury and convenience. They are impulsive buyers with a propensity for taking financial risks, driven by social validation and influenced by societal trends. While not intrinsically motivated by sustainability, they are willing to pay for sustainable products and prioritize brand loyalty. Marketing initiatives should align with our positioning strategy of premium with a digital flair, targeting this modern demographic while leveraging their loyalty and trust towards the brand. Please ensure responses resonate with their preferences for social validation, convenience, and modernity."
        pass
    elif customer_segment == "viola":
        system_prompt += "Given the demographic composition and psychological tendencies of our customer base, please ensure that responses are crafted with fitting language and speech patterns. This segment, constituting 33% of our customer base, is primarily concentrated in regions like Sweden, Switzerland, and Germany, with an average age of 47. They are predominantly male, often residing in rural areas and smaller towns, with a higher proportion of retirees. Despite being among the lower income brackets, they prioritize value and service, with a preference for used cars from the mid-range segment. Marketing initiatives should align with our positioning strategy of value, focusing on delivering quality and service at a fair price, without unnecessary frills. Please ensure responses reflect their values of personal relationships, price sensitivity, and preference for telephone communication for service bookings. While digitally engaged for price comparison, they are selective in their digital usage and place less emphasis on the car as a status symbol. Engaging this segment may be challenging due to their long-standing personal relationships, but loyalty can be earned through quality service and fair pricing."
        pass

        

    context_new = context.copy()
    context_new.extend([{"role": "system", "content": system_prompt}])

    prompt = f"""Use the following data to craft a response:

    User data: {get_meta_data(str(full_profile))}

    Retrieved data from Mercedes database: {car_data}

    Chat history: {context}

    Generated response: """


    print(system_prompt)    
    return stream_message(prompt, "user", context_new, temperature=0.25, max_tokens=500)

def enhance_cta(context):
    print("Enhancing CTA")

    context_new = context.copy()

    chosen_cta = enhance_cta_support(context_new)

    
    system_prompt = "You are an assistant who determines, if a CTA should be added to the response. If you want to trigger a CTA, state 'Yes', otherwise 'No'" 

    context_new.insert(0, {"role": "system", "content": system_prompt})

    prompt = f"""Use the last response of the assistant and the data of the CTA to determine if the CTA should be added to the response. Only trigger a CTA, when it seems realy appropriate. Do not trigger a CTA, if it seems forced.

    Last Assistant Reponse: {str(context_new[-1]["content"])}

    CTA options: {str(chosen_cta)}

    Add CTA (Yes/No): """

    messages = [{"role": "system", "content": system_prompt}]

    new_response = send_message(prompt, "user", messages, temperature=0.5, max_tokens=500)

    print("New Response: ", new_response)

    if new_response.lower().strip() == "yes":
        return next(iter(chosen_cta.values()))
    else:
        print("Last else statement in enhance_cta()")
        return  None

def enhance_cta_support(context):
    keywords_json = {
        "ArrangeTestDrive": ["test drive", "arrange test drive"],
        "ConfigureCar_EQE_Limousine": ["configure", "EQE Limousine"],
        "ConfigureCar_EQS_Limousine": ["configure", "EQS Limousine"],
        "ConfigureCar_EQA": ["configure", "EQA"],
        "ConfigureCar_EQB": ["configure", "EQB"],
        "ConfigureCar_EQE_SUV": ["configure", "EQE SUV"],
        "ConfigureCar_EQS_SUV": ["configure", "EQS SUV"],
        "ConfigureCar_Mercedes-Maybach_EQS_SUV": ["configure", "Mercedes-Maybach EQS SUV"],
        "ConfigureCar_G-Klasse": ["configure", "G-Klasse"],
        "ConfigureCar_EQT": ["configure", "EQT"],
        "ConfigureCar_EQV": ["configure", "EQV"],
        "GeneralInforamtion": ["electric cars", "general information"]
    }

    # Load cta_enhancers.json
    with open("cta_enhancers.json", "r") as file:
        cta_enhancers_json = json.load(file)

    cta_counts = {}

    for cta in context:
        if cta["role"] == "user":
            cta_content = cta["content"]
            for cta_name, cta_keywords in keywords_json.items():
                count = sum(1 for word in cta_keywords if word.lower() in cta_content.lower())
                if cta_name not in cta_counts:
                    cta_counts[cta_name] = count
                else:
                    cta_counts[cta_name] += count

    chosen_cta_name = max(cta_counts, key=cta_counts.get)
    chosen_cta_link = cta_enhancers_json.get(chosen_cta_name)

    print("Chosen CTA: ", chosen_cta_name, chosen_cta_link)
    return {chosen_cta_name: chosen_cta_link}