# coding: utf-8

import re

name = '''
          失落迷迭
        '''

match_re = re.match(".*?([\u4E00-\u9FA5]*)", name)

print(match_re.group(1))



