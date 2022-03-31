# -*- coding: utf-8 -*-

class Displayer:
    def __init__(self):
        pass

    def display(self, fields: [], lines: []):
        field2len = {}
        for r in lines:
            for k, v in r.items():
                if field2len.get(k) is None:
                    field2len[k] = len(k)
                field2len[k] = max(field2len[k], len(self.str_field(v)))
        # display column name
        border_line = "+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+"
        print(border_line)
        print("| " + " | ".join([k.ljust(v) for k, v in field2len.items()]) + " |")
        print(border_line)
        # display record fields
        for r in lines:
            print("| " + " | ".join([self.beautiful_column(r[k], v) for k, v in field2len.items()]) + " |")
        # display end line
        print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")

    @staticmethod
    def str_field(value):
        if value is None:
            return "NULL"
        else:
            return str(value)

    @staticmethod
    def beautiful_column(value, width):
        if type(value) is str:
            return Displayer.str_field(value).ljust(width)
        elif value is None:
            return Displayer.str_field(value).ljust(width)
        else:
            return Displayer.str_field(value).rjust(width)
