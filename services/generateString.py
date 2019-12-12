import string
import random


def generate_random_string(base_string_character, string_size=10):
    response_string = ''
    for i in range(string_size):
        character = random.choice(base_string_character)

        # Append the selected character to the response string
        response_string += character
    return response_string


def generate_random_alpha_num(str_len=10):
    ret = generate_random_string(string.digits + string.ascii_letters, str_len)
    return ret


