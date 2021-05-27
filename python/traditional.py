'''
Author: your name
Date: 2021-05-16 18:12:24
LastEditTime: 2021-05-26 11:53:22
LastEditors: WanJu
Description: In User Settings Edit
FilePath: /DiskFailurePredictor/train/bb_train_no.py
'''
from json.decoder import JSONDecodeError
import sys, os
import time
import datetime
import json
import pickle
from numpy import e
import pandas as pd
from dateutil.relativedelta import relativedelta
# from mlxtend.feature_selection import SequentialFeatureSelector
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.feature_selection import SelectFromModel
from score import Score

root_path = 'E:\\BackBlaze\\DP_test'
X_ = 1
y_ = 0
index_dict = {
    'data':5,
    'failure':4,
    'date':0
}

class Traditional_Train:
    def __init__(self, data_path, model, param={'random_state':[18]}, folds=5, random_state=18, test_size=0.3) -> None:
        self.data_path_ = os.path.join(root_path, 'train_data', data_path, model)
        self.model = model
        self.test_size_ = test_size
        self.random_state_ = random_state
        self.index_dict_ = index_dict
        self.param_ = param
        self.folds_ = folds
        self.train_data_ = [pd.DataFrame() ,pd.DataFrame()]
        self.verify_data_ = pd.DataFrame()
        self.test_data_ = [pd.DataFrame() ,pd.DataFrame()]
        self.model_ = RandomForestClassifier()
        self.scale_ = StandardScaler()
        self.scale_exits_ = False
        self.feature_ = []

    def run(self):
        self.get_data()
        self.get_scale()
        self.get_feature()
        # self.feature_ = [3, 6, 7, 9, 14, 19, 20, 23, 30, 32, 33, 36, 37, 41, 42, 44, 47]
        self.grid_search()
        self.model_score()
        self.model_verify()
        self.save_model()
    
    def update_param(self, param):
        self.param_ = param

    def get_data(self):
        print("\n#1 Geting data...")
        train_data = pd.read_csv(os.path.join(self.data_path_, 'train.csv'), encoding='utf-8').sort_values(by='date')
        print(train_data)
        self.verify_data_ = pd.read_csv(os.path.join(self.data_path_, 'verify.csv'), encoding='utf-8')

        X = train_data.iloc[:, self.index_dict_['data']:]
        y = train_data.iloc[:, self.index_dict_['failure']]
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=self.test_size_, random_state=self.random_state_)
        self.train_data_[y_] = train_y
        self.train_data_[X_] = train_X
        self.test_data_[y_] = test_y
        self.test_data_[X_] = test_X
        train_data = None

    def get_scale(self):
        print("\n#2 归一化")
        scale_file_path = os.path.join(root_path, 'models', self.model, time.strftime("%Y-%m-%d"), 'scale.pkl')
        if os.path.exists(scale_file_path):
            self.scale_exits_ = True
            with open(scale_file_path, mode='rb') as file:
                self.scale_ = pickle.load(file)
                self.train_data_[X_]= pd.DataFrame(self.scale_.transform(self.train_data_[X_]))
                self.test_data_[X_]= pd.DataFrame(self.scale_.transform(self.test_data_[X_]))
        else:
            self.train_data_[X_]= pd.DataFrame(self.scale_.fit_transform(self.train_data_[X_]))
            self.test_data_[X_]= pd.DataFrame(self.scale_.transform(self.test_data_[X_]))
        
    def get_feature(self):
        print("\n#3 特征选择")
        # sfs = SequentialFeatureSelector(
        #     estimator=self.model_,
        #     k_features='best',
        #     verbose=2,
        #     scoring='roc_auc',
        #     n_jobs=-1
        # )
        # sfs.fit(X=self.train_data_[X_], y=self.train_data_[y_])
        clf = RandomForestClassifier(random_state=self.random_state_, n_estimators=50)
        clf = clf.fit(X=self.train_data_[X_], y=self.train_data_[y_])
        sfm = SelectFromModel(
            estimator=clf,
            prefit=True
        )
        print(' --- 特征重要性:')
        print(clf.feature_importances_)
        self.feature_ = list(sfm.get_support(indices=True))
        print(" --- 最佳特征：", self.feature_)


    def grid_search(self):
        print("\n#4 网格搜索/交叉验证")
        self.train_data_[X_] = self.train_data_[X_].iloc[:, self.feature_]
        self.test_data_[X_] = self.test_data_[X_].iloc[:, self.feature_]
        k_folds = StratifiedKFold(n_splits=self.folds_, shuffle=True, random_state=self.random_state_)
        gscv = GridSearchCV(
            estimator=self.model_,
            param_grid=self.param_,
            scoring='roc_auc',
            n_jobs=-1,
            cv=k_folds,
            verbose=2)
        gscv.fit(X=self.train_data_[X_], y=self.train_data_[y_])
        self.model_ = gscv.best_estimator_
        print(" --- 最佳参数：", self.model_.get_params())

    def model_score(self):
        print("\n#5 模型评估")
        predict_y = self.model_.predict(self.test_data_[X_])
        matrix_ = confusion_matrix(y_pred=predict_y, y_true=self.test_data_[y_])
        print("混淆矩阵：\n", matrix_)
        print("模型评估：\n", classification_report(y_true=self.test_data_[y_], y_pred=predict_y))
        Score.print_confusion_matrix(confusion_matrix=matrix_, y_true=self.test_data_[y_], y_score=predict_y)

    @staticmethod
    def add_one_mounth(date_form, old_date_str) -> str:
        return datetime.datetime.strftime(datetime.datetime.strptime(str(old_date_str), date_form) + relativedelta(months=1), date_form)

    def model_verify(self):
        print("\n#6 模型验证（按月份划分验证集）")

        begin_date = self.verify_data_.iloc[0, self.index_dict_['date']]
        end_date = self.verify_data_.iloc[-1, self.index_dict_['date']]
        print("--- 数据时间跨度[%s, %s)：" % (begin_date, end_date))
        print(" features:", self.feature_)
        print(" params:")
        print(pd.Series(self.model_.get_params()))

        while begin_date < end_date:
            cur_date = Traditional_Train.add_one_mounth("%Y-%m-%d", begin_date)
            
            cur_data = self.verify_data_[(self.verify_data_.iloc[:, self.index_dict_['date']] >= begin_date) & \
                                        (self.verify_data_.iloc[:, self.index_dict_['date']] < cur_date)]
            cur_data_y = cur_data.iloc[:, self.index_dict_['failure']]
            if len(cur_data_y.value_counts()) < 2:
                break
            cur_data_X = cur_data.iloc[:, self.index_dict_['data']:]
            cur_data_X = pd.DataFrame(self.scale_.transform(cur_data_X))  # 对当前测试数据进行归一化
            cur_data_X = cur_data_X.iloc[:, self.feature_]  # 对当前测试数据提取特征

            predict_y = self.model_.predict(cur_data_X)  # 使用当前模型进行预测
            matrix = confusion_matrix(cur_data_y, predict_y)

            print("\n--- 当前测试结果[%s, %s)：" % (begin_date, cur_date))
            Score.print_confusion_matrix(confusion_matrix=matrix, y_true=cur_data_y, y_score=predict_y)
            begin_date = cur_date

    def save_model(self):
        print("\n#7 模型保存")
        first_name = self.model_.__class__.__name__
        last_name = '.pkl'
        now_time = time.strftime("%Y-%m-%d")
        save_path = os.path.join(root_path, 'models', self.model, now_time)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        model_name = first_name + last_name
        with open(os.path.join(save_path, model_name), mode='wb') as file:
             pickle.dump(obj=self.model_, file=file)

        if not self.scale_exits_:
            with open(os.path.join(save_path, 'scale' + last_name), mode='wb') as file:
                pickle.dump(obj=self.scale_, file=file)

        with open(os.path.join(os.path.join(root_path, 'models', self.model), 'config.json'), mode='w+') as file:
            # 当前 model 的所有模型的最佳 feature 和 当前正在使用的模型
            try:
                config = json.load(file)
            except JSONDecodeError:
                config = {}
            config['current_model'] = os.path.join(now_time, model_name)
            model_feature = {
                'feature':list(self.verify_data_.columns),
                'index':str(self.feature_)
            }
            config[os.path.join(now_time, model_name)] = model_feature
            file.truncate()
            json.dump(config, file, indent=2)
            

        with open(os.path.join(root_path, 'models', 'features.json'), mode='w+') as file:
            # 统一管理所有 model 的当前模型的最佳 feature
            try:
                features = json.load(file)
            except JSONDecodeError:
                features = {}
            features[self.model] = [self.verify_data_.columns[i + self.index_dict_['data']] for i in self.feature_]
            file.truncate()
            json.dump(features, file, indent=2)
            

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('parameter transport error:', sys.argv)
        sys.exit(0)
    try:
        param = json.loads(sys.argv[1])
        data_path = str(param['file_path'])
        model = str(param['model'])
        params = dict(param['params'])
        root_path = str(param['root_path'])
        print(params)
    except JSONDecodeError:
        print('The parameter-format is wrong, it must be "json-format", take care of \' " \':', sys.argv[1])
        sys.exit(0)
    except KeyError:
        if 'file_path' not in param.keys():
            missing_key = 'file_path'
        elif 'model' not in param.keys():
            missing_key = 'model'
        elif 'root_path' not in param.keys():
            missing_key = 'root_path'
        else:
            missing_key = 'params'
        print('Thr parameter-encoing is wrong, missing key:', '"%s"' % missing_key)
        sys.exit(0)

    # data_path = '2016'
    # model = 'ST4000DM000'
    # params = {
    #             "max_depth": [10, 20, 30],
    #             "max_features": [4, 7, 10],
    #             "n_estimators": [10, 20, 30, 40]
    #         }
    obj = Traditional_Train(
        data_path=data_path, 
        model=model,
        param=params,
        folds=5,
        random_state=18,
        test_size=0.3
    )
    obj.run()