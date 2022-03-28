# -*- coding: utf-8 -*-

def display(lines):
    field2len = {}
    for r in lines:
        for k, v in r.items():
            if field2len.get(k) is None:
                field2len[k] = len(k)
            field2len[k] = max(field2len[k], len(str_field(v)))
    # display column name
    print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")
    print("| " + " | ".join([k.ljust(v) for k, v in field2len.items()]) + " |")
    print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")
    # display record fields
    for r in lines:
        print("| " + " | ".join([beautiful_column(r[k], v) for k, v in field2len.items()]) + " |")
    # display end line
    print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")


def str_field(value):
    if value is None:
        return "NULL"
    else:
        return str(value)


def beautiful_column(value, width):
    if type(value) is str:
        return str_field(value).ljust(width)
    elif value is None:
        return str_field(value).ljust(width)
    else:
        return str_field(value).rjust(width)
