'''
Descripttion: 
Version: xxx
Author: WanJu
Date: 2021-05-25 21:11:37
LastEditors: WanJu
LastEditTime: 2021-05-26 19:00:56
'''
import time
from json.decoder import JSONDecodeError
from operator import index, le
import os, sys
import pickle
import json
from typing import Any
from numpy import zeros
import pandas as pd
import re

from pandas.core.frame import DataFrame
from pandas.core.series import Series

chunk_size = 10000
root_path = ''
str_model = 'model'  # 描述硬盘的系列
index_dict = {
    'data':5,
    'failure':4,
    'date':0
}
class predict:
    def __init__(self, data_path) -> None:
        self.data_path_ = data_path
        self.model_dict_ = {}
        
    def run(self):
        self.get_config()
        self.predict()

    def get_config(self):
        print('#1 读取配置文件...')
        config_path = os.path.join(root_path, 'models', 'features.json')
        try:
            with open(config_path, mode='r') as file:
                self.model_dict_ = json.load(file)
        except FileNotFoundError:
            print(config_path, ':config not exits.')
            sys.exit(0)
        except JSONDecodeError:
            print(config_path, 'config-format is wrong.')
            sys.exit(0)

    def get_model_name(self, model, features_name):
        # 找到匹配度最高的 model
        model = re.sub('[\\/:*?\"<>|.]', '-', str(model))
        scores = []
        if model in self.model_dict_.keys():
            return model
        else:
            for model_features in self.model_dict_.values():
                scores.append(len(features_name) / len([i for i in features_name if i in model_features]))
            max_index = scores.index(max(scores))
            return list(self.model_dict_.keys())[max_index]

    def load_model(self, model_name):
        model_path = os.path.join(root_path, 'models', model_name)
        try:
            with open(os.path.join(model_path, 'config.json'), mode='r') as file:
                config = json.load(file)
                cur_model_name = str(config['current_model'])
                features_name = list(config[cur_model_name]['feature'])
                features_index = list(json.loads(config[cur_model_name]['index']))
                
        except FileNotFoundError:
            print(model_path, ": config file not found.")
            sys.exit(0)
        except JSONDecodeError:
            print(model_path, ": config-format wrong.")
            sys.exit(0)
        except KeyError:
            print(model_path, ": config missing key: current_model / feature / index.")
            sys.exit(0)

        model_path = os.path.join(model_path, cur_model_name)
        scale_path = os.path.join(os.path.dirname(model_path), 'scale.pkl')
        try:
            with open(model_path, mode='rb') as file:
                model = pickle.load(file)
                
            with open(scale_path, mode='rb') as file:
                scale = pickle.load(file)
                
            return {
                    'model': model,
                    'scale': scale,
                    'feature_name': features_name,
                    'feature_index': features_index
                }
        except FileNotFoundError:
            print(os.path.join(model_path, cur_model_name), ": model file not found.")

    @staticmethod
    def get_ordered_data(features_name, data) -> DataFrame:
        new_data = pd.DataFrame()
        for feature in features_name:
            if feature in data.columns:
                new_col = data[feature]
            else:
                new_col = zeros(data.shape[0])
            new_data[feature] = new_col
        return new_data

    def write_back(self, save_path, result, file_name):
        first = True
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        if os.path.exists(os.path.join(save_path, file_name)):
            first = False
            
        result.to_csv(os.path.join(save_path, file_name), mode='a', header=first, index=False)
            
    
    def predict(self):
        print('#2 故障预测...')
        model_dict = {}
        try:
            save_path = os.path.join(root_path, 'result', time.strftime("%Y-%m-%d"))
            for data_file in sorted(os.listdir(self.data_path_)):
                print('\r processing:', data_file, end='')
                
                if os.path.exists(os.path.join(save_path, data_file)):
                    os.remove(os.path.join(save_path, data_file))
            
                df = pd.read_csv(os.path.join(self.data_path_, data_file), chunksize=chunk_size)
                for chunk in df:
                    group_chunk = chunk.groupby(by=[str_model])
                    for key, group in group_chunk:
                        group.dropna(how='all', axis=1, inplace=True)
                        group = group.fillna(method='ffill', axis=1)
                        model_name = self.get_model_name(key, list(group.columns)[index_dict['data']:])
                        if model_name not in model_dict.keys():
                            model_dict[model_name] = self.load_model(model_name=model_name)
                        best_model = model_dict[model_name]
                        
                        data = predict.get_ordered_data(features_name=best_model['feature_name'], data=group)
                        data = data.iloc[:, index_dict['data']:]
                        data = pd.DataFrame(best_model['scale'].transform(data))
                        data = data.iloc[:, best_model['feature_index']]
                        result = best_model['model'].predict(data)
                        group['result'] = result
                        self.write_back(save_path=save_path, result=group[['date', 'serial_number', 'model', 'failure', 'result']], file_name=data_file)

        except FileNotFoundError:
            print(self.data_path_, ': data not found.')
            sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('parameter transport error:', sys.argv)
        sys.exit(0)
    try:
        param = json.loads(sys.argv[1])
        data_path = str(param['file_path'])
        root_path = str(param['root_path'])
    except JSONDecodeError:
        print('The parameter-format is wrong, it must be "json-format", take care of \' " \':', sys.argv[1])
        sys.exit(0)
    except KeyError:
        if 'file_path' not in param.keys():
            missing_key = 'file_path'
        else:
            missing_key = 'root_path'
        print('Thr parameter-encoing is wrong, missing key:', '"%s"' % missing_key)
        sys.exit(0)

    obj = predict(
        data_path=data_path
    )
    obj.run()