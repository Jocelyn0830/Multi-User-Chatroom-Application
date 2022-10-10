# Jocelyn Wang
#!/usr/bin/python3
#
# Wesleyan University
# COMP 411 Fall 2022
# Web server helper functions

# Project modules
import header_constants as const


def get_field(msg, name, end_str):

    try:
        name_start = msg.index(name)
        name_end = name_start + len(name)
        field_end = name_end + msg[name_end:].index(end_str)
        value = msg[name_end: field_end]
        return value

    except ValueError as e:
        print("Field not found: ", e)
        return -1
