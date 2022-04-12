# -*- coding: utf-8 -*-

class Displayer:
    def __init__(self):
        pass

    def display(self, fields: [], lines: []):
        if len(lines) == 0:
            print("Empty set")
        else:
            self._display_table(fields, lines)
            if len(lines) == 1:
                print("1 line in set")
            else:
                print("{} lines in set".format(len(lines)))

    def _display_table(self, field_names: [], lines: []):
        field2len = dict(zip(field_names, [len(name) for name in field_names]))
        for r in lines:
            for k, v in r.items():
                if field2len.get(k) is None:
                    field2len[k] = len(k)
                field2len[k] = max(field2len[k], len(self.str_field(v)))
        # display column name
        border_line = "+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+"
        print(border_line)
        print("| " + " | ".join([field.ljust(field2len[field]) for field in field_names]) + " |")
        print(border_line)
        # display record fields
        for r in lines:
            print(
                "| " + " | ".join([self.beautiful_column(r[field], field2len[field]) for field in field_names]) + " |")
        # display end line
        print("+-" + "-+-".join(['-' * v for k, v in field2len.items()]) + "-+")

    @staticmethod
    def str_field(value):
        if value is None:
            return "NULL"
        elif type(value) == float:
            if value > 1e-6:
                return "%.06f" % value
            elif abs(value) < 1e-10:
                return "0"
            else:
                return str(value)
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
