'''
Descripttion: 
Version: xxx
Author: WanJu
Date: 2021-05-24 20:03:38
LastEditors: WanJu
LastEditTime: 2021-05-26 11:42:02
'''
from json.decoder import JSONDecodeError
import os, sys
import json
import pandas as pd
import re

root_path = ''
str_model = 'model'  # 描述硬盘的系列

class preProcess:
    def __init__(self, data_path, replace) -> None:
        self.data_path_ = data_path
        self.replace_ = replace

    def run(self):
        data_path = os.path.join(root_path, 'original_data', self.data_path_)
        save_root = os.path.join(root_path, 'processed_data', self.data_path_)
        if os.path.exists(save_root) and not self.replace_:
            # 路径存在则说明数据已经预处理过
            print('[Warning ] Original datas in "%s" have already been preprocessed, sure to preprocess again?' % self.data_path_)
            return
        for sub_dirs in sorted(list(os.listdir(data_path))):
            sub_path = os.path.join(data_path, sub_dirs)
            for file in sorted(list(os.listdir(sub_path))):
                file_path = os.path.join(sub_path, file)
                print('\r Preprocessing:', file_path, end='')
                df = pd.read_csv(file_path)
                df_by_model = df.groupby(by=[str_model])
                
                for key, group in df_by_model:
                    save_path = os.path.join(save_root, re.sub('[\\/:*?\"<>|.]', '-', str(key)))
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                        
                    group.dropna(axis=1, how='all', inplace=True)
                    group.to_csv(os.path.join(save_path, file), header=True, index=False)
                    
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('parameter transport error:', sys.argv)
        sys.exit(0)
    try:
        param = json.loads(sys.argv[1])
        data_path = str(param['file_path'])
        replace = int(param['replace'])
        root_path = str(param['root_path'])
    except JSONDecodeError:
        print('The parameter-format is wrong, it must be "json-format", take care of \' " \':', sys.argv[1])
        sys.exit(0)
    except KeyError:
        if 'file_path' not in param.keys():
            missing_key = 'file_path'
        if 'root_path' not in param.keys():
            missing_key = 'root_path'
        else:
            missing_key = 'replace'
        print('Thr parameter-encoing is wrong, missing key:', '"%s"' % missing_key)
        sys.exit(0)
    
    obj = preProcess(data_path=data_path, replace=replace)
    obj.run()
    