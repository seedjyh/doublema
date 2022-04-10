# -*- coding: utf-8 -*-
ma_list = [1, 5, 13, 34]

# 为了比较不同均线，必须有至少两条均线。
assert len(ma_list) > 1
# 必须包含宽度1的均线，即当前K柱
assert ma_list[0] == 1
