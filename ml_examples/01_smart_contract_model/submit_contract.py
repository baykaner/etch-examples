from fetchai.ledger.api import LedgerApi
from fetchai.ledger.contract import Contract
from fetchai.ledger.crypto import Entity, Address
import sys
import time

# TODO - make different train and test files
# TODO - make 10 mnist images file
# TODO - read in all 10 examples


REGRESSION_DATA_TRAIN_FILE = "../data/boston_data.csv"
REGRESSION_LABEL_TRAIN_FILE = "../data/boston_label.csv"
REGRESSION_DATA_TEST_FILE = "../data/boston_data.csv"
REGRESSION_LABEL_TEST_FILE = "../data/boston_label.csv"

CLASSIFICATION_DATA_TRAIN_FILE = "../data/mnist_1_image.csv"
CLASSIFICATION_LABEL_TRAIN_FILE = "../data/mnist_1_label.csv"
CLASSIFICATION_DATA_TEST_FILE = "../data/mnist_1_image.csv"
CLASSIFICATION_LABEL_TEST_FILE = "../data/mnist_1_label.csv"


# generic contract setup
def contract_setup():

    # Create keypair for the contract owner
    entity1 = Entity()
    address = Address(entity1)
    entity2 = Entity()
    address = Address(entity2)

    # Setting API up
    api = LedgerApi('127.0.0.1', 8000)

    # Need funds to deploy contract
    api.sync(api.tokens.wealth(entity1, 10000000000000))
    api.sync(api.tokens.wealth(entity2, 10000000000000))

    # Create contract
    contract = Contract(source, entity1)

    # Deploy contract
    api.sync(contract.create(api, entity1, 1000000000))

    return api, entity1, entity2


# helper function for reading in training data
def read_one_line_data_csv_as_string(fname):

    f = open(fname, 'r')
    return f.readline()

def load_training_data(mode):

    if mode == "boston":

        data_string = read_one_line_data_csv_as_string(REGRESSION_DATA_TRAIN_FILE)
        label_string = read_one_line_data_csv_as_string(REGRESSION_LABEL_TRAIN_FILE)

        print("initial data: " + data_string)
        print("initial label: " + label_string)

    elif mode == "mnist":

        data_string = read_one_line_data_csv_as_string(CLASSIFICATION_DATA_TRAIN_FILE)
        label_string = read_one_line_data_csv_as_string(CLASSIFICATION_LABEL_TRAIN_FILE)

        print("initial data: " + data_string)
        print("initial label: " + label_string)

    return data_string, label_string

def train_and_evaluate(entity, data_string, label_string):

    # train on the input data
    fet_tx_fee = 16000000
    api.sync(contract.action(api, 'train', fet_tx_fee, [entity], data_string, label_string))

    # evaluate the initial loss
    initial_loss = contract.query(api, 'evaluate')
    print("initial_loss")


def main(source, mode):

    api, entity1, entity2 = contract_setup()

    # load training data
    data_string, label_string = load_training_data(mode)

    # train and evaluate
    train_and_evaluate(entity1, data_string, label_string)

    # make a prediction on the training data
    prediction = contract.query(api, 'predict', data_string=data_string)
    print("model training prediction: " + prediction)

    # entity2 decides to set some new data and label
    fet_tx_fee = 160000
    contract.action(api, 'setDataAndLabel', fet_tx_fee, [entity2], data_string, label_string)

    # entity 1 grabs the latest data for inspection
    # we don't need to do this - but we just demonstrate how here
    data_string = contract.query(api, 'getData')
    label_string = contract.query(api, 'getLabel')
    print("some new data: " + data_string)
    print("some new label: " + label_string)

    # entity 1 makes a prediction on the new (test) data
    prediction = contract.query(api, 'predict', data_string=data_string)
    print("model test prediction: " + prediction)



if __name__ == '__main__':

    # Loading contract
    if len(sys.argv) != 6:
      print("Usage: ", sys.argv[0], "[filename] [mode]")
      exit(-1)

    with open(sys.argv[1], "r") as fb:
      source = fb.read()

    if (sys.argv[2] != ("boston" or "mnist")):
        raise Exception('mode must be set to boston or mnist')


    main(source, sys.argv[2])