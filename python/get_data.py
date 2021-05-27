'''
Descripttion: 
Version: xxx
Author: WanJu
Date: 2021-05-24 21:23:49
LastEditors: WanJu
LastEditTime: 2021-05-26 16:37:23
'''
from json.decoder import JSONDecodeError
import os, sys
import json
from numpy.lib.npyio import save
import pandas as pd

root_path = ''
min_data_num = 200  # 当训练集数据少于 min_data_num 时，模型训练效果将很差
str_failure = 'failure'
int_pos = 1
int_neg = 0

class getData:
    def __init__(self, data_path, scale, verifySize, testSize=None) -> None:
        self.data_path_ = data_path
        self.scale_ = scale
        self.testSize_ = testSize
        self.verifySize_ = verifySize
        self.useful_model_ = []

    def run(self):
        data_path = os.path.join(root_path, 'processed_data', self.data_path_)
        save_root = os.path.join(root_path, 'train_data', self.data_path_)

        for sub_dirs in sorted(list(os.listdir(data_path))):
            train_data = pd.DataFrame()
            verify_data = pd.DataFrame()
            sub_path = os.path.join(data_path, sub_dirs)
            print('\r Preprocessing:', sub_path, end='')
            for file in sorted(list(os.listdir(sub_path))):
                file_path = os.path.join(sub_path, file)
                # 按比例提取训练集、验证集
                df = pd.read_csv(file_path)
                pos_data = df[df[str_failure] == int_pos].fillna(method='ffill', axis=1)
                if pos_data.shape[0] == 0:
                    continue
                neg_data = df[df[str_failure] == int_neg]
                neg_num = int(pos_data.shape[0] / self.scale_)
                if neg_num > neg_data.shape[0]:
                    neg_num = neg_data.shape[0]
                neg_data = neg_data.sample(n=neg_num, random_state=18).fillna(method='ffill', axis=1)
                train_data = pd.concat([train_data, pos_data, neg_data])


            if train_data.shape[0] >= min_data_num:
                self.useful_model_.append(sub_dirs)
                verify_num = int(train_data.shape[0] * (1 - self.verifySize_))
                verify_data = train_data.iloc[verify_num:, :]
                train_data = train_data.iloc[:verify_num, :]
                save_path = os.path.join(save_root, sub_dirs)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                train_data.to_csv(os.path.join(save_path, 'train.csv'), index=False, header=True)
                verify_data.to_csv(os.path.join(save_path, 'verify.csv'), index=False, header=True)
        
        print('\n[info --> ] useful_mode-%d:%s' % (len(self.useful_model_), self.useful_model_))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('parameter transport error:', sys.argv)
        sys.exit(0)
    try:
        param = json.loads(sys.argv[1])
        data_path = str(param['file_path'])
        scale = float(param['scale'])
        verifySize = float(param['verifySize'])
        root_path = str(param['root_path'])
    except JSONDecodeError:
        print('The parameter-format is wrong, it must be "json-format", take care of \' " \':', sys.argv[1])
        sys.exit(0)
    except KeyError:
        if 'file_path' not in param.keys():
            missing_key = 'file_path'
        elif 'scale' not in param.keys():
            missing_key = 'scale'
        elif 'root_path' not in param.keys():
            missing_key = 'root_path'
        else:
            missing_key = 'verifySize'
        print('Thr parameter-encoing is wrong, missing key:', '"%s"' % missing_key)
        sys.exit(0)
    
    obj = getData(data_path=data_path, scale=scale, verifySize=verifySize)
    obj.run()