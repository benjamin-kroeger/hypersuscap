import json
import logging.config
from constants import segments
from open_ai_call import send_message

logging.config.fileConfig(
    'logging.config',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)

segments_str = '\n'.join([str(x) for x in segments])
def identify_customer_segment(user_data: str):
    prompt = ("Please tell me into which segment the user fits in best.\n"
              "User:\n"
              f"{user_data}\n"
              "Segments:\n"
              f"{segments_str}")

    resp = send_message(message=prompt,role='user').content
    print(resp)


if __name__ == '__main__':
    with open('/home/benjaminkroeger/Documents/Hackathons/TumAI/hypersuscap/profiles/profile1.json', 'r') as f:
        user_data = str(json.load(f))
    identify_customer_segment(user_data)
