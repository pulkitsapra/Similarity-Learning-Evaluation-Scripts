import sys
import os
sys.path.append('..')
from sl_eval.models import BaselineModel
from data_readers import SickReader
from gensim import downloader as api
import numpy as np
from keras.utils import to_categorical
    
def sent2vec(sent):
    if len(sent)==0:
        print('length is 0, Returning random')
        return np.random.random((kv_model.vector_size,))

    vec = []
    for word in sent:
        if word in kv_model:
            vec.append(kv_model[word])

    if len(vec) == 0:
        print('No words in vocab, Returning random')
        return np.random.random((kv_model.vector_size,))

    vec = np.array(vec)

    return np.mean(vec, axis=0)


if __name__ == '__main__':

    print('Evaluating SICK Baseline')

    sick_folder_path = os.path.join('..', 'data', 'SICK')
    sick_reader = SickReader(sick_folder_path)

    num_predictions = 3
    num_embedding_dims = 300
    kv_model = api.load('glove-wiki-gigaword-' + str(num_embedding_dims))


    x1, x2, label = sick_reader.get_entailment_data()
    train_x1, train_x2, train_labels = x1['TRAIN'], x2['TRAIN'], label['TRAIN']
    test_x1, test_x2, test_labels = x1['TEST'], x2['TEST'], label['TEST']


    vectored_train_x1 = [sent2vec(xi) for xi in train_x1]
    vectored_train_x1 = np.array(vectored_train_x1)

    vectored_train_x2 = [sent2vec(xi) for xi in train_x2]
    vectored_train_x2 = np.array(vectored_train_x2)

    one_hot_train_labels = [to_categorical(li, num_predictions) for li in train_labels]
    one_hot_train_labels = np.squeeze(np.array(one_hot_train_labels))


    vectored_test_x1 = [sent2vec(xi) for xi in test_x1]
    vectored_test_x1 = np.array(vectored_test_x1)

    vectored_test_x2 = [sent2vec(xi) for xi in test_x2]
    vectored_test_x2 = np.array(vectored_test_x2)

    one_hot_test_labels = [to_categorical(li, num_predictions) for li in test_labels]
    one_hot_test_labels = np.squeeze(np.array(one_hot_test_labels))

    regression_model = BaselineModel(
                        vector_size=num_embedding_dims, num_predictions=num_predictions, model_type='regression'
                        )
    regression_model.train({'x1': vectored_train_x1, 'x2': vectored_train_x2}, one_hot_train_labels, n_epochs=10)

    print('\nAccuracy of the Regression Model is:' +
            str(regression_model.model.evaluate({'x1': vectored_test_x1, 'x2': vectored_test_x2},
                                  one_hot_test_labels)[1]
            )
        )

    del regression_model

    multilayer_model = BaselineModel(
                        vector_size=num_embedding_dims, num_predictions=num_predictions, model_type='multilayer'
                        )
    multilayer_model.train({'x1': vectored_train_x1, 'x2': vectored_train_x2}, one_hot_train_labels, n_epochs=10)

    print('\nAccuracy of the Multilayer Model is:' +
            str(multilayer_model.model.evaluate({'x1': vectored_test_x1, 'x2': vectored_test_x2},
                                  one_hot_test_labels)[1]
            )
        )
