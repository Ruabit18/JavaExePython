'''
Descripttion: 
Version: xxx
Author: WanJu
Date: 2021-05-20 09:57:02
LastEditors: WanJu
LastEditTime: 2021-05-24 20:46:01
'''
import time
import sys
import json

if __name__ == '__main__':
    # try:
    # except 
    print('json:', sys.argv[1])
    param = json.loads(str(sys.argv[1]))
    print('param:', param)
    param_1 = param['param_1']
    param_2 = param['param_2']
    
    print('param_1:', param_1)
    print('param_2:', param_2)
    i = int(param_1)
    while i:
        print('\rprocessing:', i, end='')
        i = i - 1
        time.sleep(1)