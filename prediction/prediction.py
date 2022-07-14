from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression, LinearRegression
import numpy as np
import pandas as pd
import pickle
import os
import re
from sklearn.preprocessing import OneHotEncoder

PARAMS = ['heart_rate', 'breath_freq', 'variability_index', 'start_time']


def crate_prediction_file(dir_path, file, data, results):
    '''
    создание файла с предсказанным результатом
    :param dir_path: директория
    :param file: имя файла
    :param data: численные данные
    :param results: результаты
    :return: имя файла
    '''
    t = []
    for param in PARAMS:
        t.append([param, results[param], data[param]])
    t.append(['result', results['result'], ''])

    filename = os.path.join(dir_path, f"{file}_p.csv")
    pd.DataFrame(t, columns=['ind', 'result', 'value']).to_csv(filename, index=False)
    return f"{file}_p.csv"


def save_model(file, model):
    """
    Сохранить модель
    :param file: имя файла
    :param model: модель
    :return: None
    """
    with open(file, 'wb') as f:
        pickle.dump(model, f)


def save_models(dir_path, models):
    '''
    сохранение моделей
    :param dir_path: директория
    :param models: словарь моделей
    :return: None
    '''
    for param in PARAMS + ['result', 'onehotencoder']:
        save_model(os.path.join(dir_path, param), models[param])


def load_model(file):
    '''
    загрузка модели
    :param file: имя файла с моделью
    :return: модель
    '''
    with open(file, 'rb') as f:
        return pickle.load(f)


def load_models(dir_path):
    '''
    загрузка моделей
    :param dir_path: директории
    :return: словарь моделей
    '''
    models = dict()
    for param in PARAMS + ['result', 'onehotencoder']:
        models[param] = load_model(os.path.join(dir_path, param))
    return models


def get_columns(param):
    '''
    получение листа колонок в зависимости от параметра
    :param param:
    :return:
    '''
    if param != 'result':
        columns = ['value']
    else:
        columns = PARAMS
    return columns + ['label']


def get_data(file, param):
    '''
    получение записи из файла
    :param file: полное имя файла
    :param param:
    :return: None
    '''
    columns = get_columns(param)

    data_file = pd.read_csv(file, delimiter=',')
    data_file = data_file.set_index('ind')

    if param != 'result':
        t = [float(data_file.loc[param]['value']), str(int(data_file.loc[param]['result']))]
    else:
        t = list(map(int, data_file['result'].tolist()))
        t[-1] = str(t[-1])

    return pd.DataFrame([t], columns=columns)


def get_dataset(dir_path, param):
    '''
    создание датасета
    :param dir_path: директория
    :param param:
    :return: датасет
    '''
    columns = get_columns(param)

    dataset = pd.DataFrame([], columns=columns)
    files = os.listdir(dir_path)
    for file in files:
        if re.search(r'\d\d.\d\d.\d{4} \d\d-\d\d-\d\d_r', file):
            data = get_data(os.path.join(dir_path, file), param)
            dataset = pd.concat([dataset, data], ignore_index=True)

    return dataset


def split_dataset(dataset):
    '''
    разделение датасета на признаки и метку
    :param dataset:
    :return:
    '''
    X = dataset.iloc[:, :-1]
    y = dataset.iloc[:, -1]
    return X, y


def transform(data, ohe):
    '''
    преобразование категориальных признаков
    :param data:
    :param ohe:
    :return:
    '''
    feature_arr = ohe.fit_transform(data[:]).toarray()
    feature_labels = ohe.categories_
    feature_labels = np.array(feature_labels).ravel()
    return pd.DataFrame(feature_arr, columns=feature_labels)


def fit(dir_path, ignor=None):
    '''
    обучение моделей
    :param dir_path: директория
    :param ignor: игнорируемая запись
    :return: словарь моделей
    '''
    models = dict()

    for param in PARAMS + ['result']:
        dataset = get_dataset(dir_path, param)
        if ignor is not None:
            dataset.drop(index=[ignor], axis=0, inplace=True)
            dataset = dataset.reset_index(drop=True)

        X, y = split_dataset(dataset)

        if param != 'result':
            # models[param] = SVC()
            models[param] = KNeighborsClassifier(n_neighbors=3)
        else:
            models['onehotencoder'] = OneHotEncoder(categories=[[0, 1, 2]] * len(PARAMS))
            X = transform(X, models['onehotencoder'])
            models[param] = LogisticRegression()
        X = X.values
        y = y.values
        models[param].fit(X, y)

    return models


def predict(dir_path, file, models):
    '''
    предсказание результата
    :param dir_path: директория
    :param file: файл
    :param models: словарь моделей
    :return: результат
    '''
    result = dict()
    y_pred = []
    # print(file)
    for param in PARAMS:
        X, y = split_dataset(get_data(os.path.join(dir_path, file), param))
        X = X.values
        y = y.values
        y_pred.append(int(models[param].predict(X)))
        # print(y, y_pred[-1])

        result[param] = y_pred[-1]

    X, y = split_dataset(get_data(os.path.join(dir_path, file), 'result'))

    X = transform(X, models['onehotencoder'])

    y_pred = pd.DataFrame([y_pred], columns=PARAMS)
    y_pred = transform(y_pred, models['onehotencoder'])
    X = X.values
    y = y.values
    y_pred = y_pred.values
    # print(y, int(models['result'].predict(X)[0]))
    result['result'] = int(models['result'].predict(y_pred)[0])
    return result


def main():
    dir_path = '../users/1656666431'

    files = os.listdir(dir_path)
    files = [file for file in files if file.find('_r') != -1]
    for i in range(len(files)):
        models = fit(dir_path, i)
        print(predict(dir_path, files[i], models))


if __name__ == '__main__':
    main()

