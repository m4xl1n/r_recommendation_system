#!/usr/bin/env python
#
#    Copyright 2011 Max Lin
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import math
import os
import pickle
import random
import sys


def random_init(scale=0.01):
    return scale * random.random()

def read_topics(topics_filename):
    topics = {}

    i = 0
    for line in file(topics_filename):
        if i == 0:
            i += 1
            continue

        pieces = line.rstrip().split(",")
        package = pieces[0]
        topic = int(pieces[1])

        topics[package] = topic
        i += 1

    print "number of LDA topics:", len(set(topics.values()))
    return topics

def dot_product(x, y):
    assert len(x) == len(y)

    p = 0.0
    for i in range(len(x)):
        p += x[i] * y[i]

    return p

def train(train_filename, topics, alpha, max_iter, beta):
    num_topics = len(set(topics.values()))

    instances = []
    users = set()
    packages = set()

    mu = 0.0
    for line in file(train_filename):
        pieces = line.rstrip().split(",")

        package = pieces[0]
        user = pieces[9].replace("\"", "")
        if pieces[10] == "0":
            installed = -1
        else:
            installed = 1
        mu += installed

        instances.append((user, package, installed))
        users.add(user)
        packages.add(package)
    
    mu /= float(len(instances))

    user_means = {}
    package_means = {}
    topic_weights = {}

    # initialize parameters
    for user in users:
        user_means[user] = random_init()
    for package in packages:
        package_means[package] = random_init()

    for user in users:
        for t in set(topics.values()):
            topic_weights[(user, t)] = random_init()
        topic_weights[(user, 'unknown')] = random_init()

    epoch = 0
    last_loss_epoch = 1e30
    while epoch < max_iter:
        loss_epoch = 0.0

        for user, package, installed in instances:
            if package not in topics:
                topics[package] = 'unknown'

            try:
                exp_loss = math.exp(-installed * (mu + user_means[user] + package_means[package] + topic_weights[(user, topics[package])]))
            except OverflowError:
                print mu, user_means[user], package_means[package], topic_weights[(user, topics[package])]
                sys.exit(1)

            loss_epoch += exp_loss

            m = exp_loss * installed
            user_means[user] +=  alpha * (m - beta * user_means[user])
            package_means[package] += alpha * (m - beta * package_means[package])
            topic_weights[(user, topics[package])] += alpha * (m - beta * topic_weights[(user, topics[package])])

        regularizer = beta * ( \
                      mu * mu + \
                      sum([user_means[k] * user_means[k] for k in user_means.keys()]) + \
                      sum([package_means[k] * package_means[k] for k in package_means.keys()]))
        for k in topic_weights:
            regularizer += beta * topic_weights[k] * topic_weights[k]

        print "epoch", epoch, loss_epoch, regularizer

        epoch += 1
        alpha *= 0.9

        assert loss_epoch + regularizer < last_loss_epoch
        last_loss_epoch = loss_epoch + regularizer

    return (mu, user_means, package_means, topic_weights, topics)

def predict(model, test_filename, skip=0):
    (mu, user_means, package_means, topic_weights, topics) = model

    predictions = []
    i = 0
    for line in file(test_filename):
        if i < skip:
            i += 1
            continue

        pieces = line.rstrip().split(",")
        user = pieces[9].replace("\"", "")
        package = pieces[0]

        v = mu + user_means[user] + package_means[package] + topic_weights[(user, topics[package])]
        predictions.append(math.exp(v) / (1.0 + math.exp(v)))

        i += 1

    return predictions

def evaluate(topics, alpha, beta, max_iter):
    dev_test_k_pred = []
    for k in range(10):
        print "Fold %d" % k

        dev_train_filename = "../split_data/dev_train.k%d.csv" % k
        com_test_filename = "../split_data/com_train.k%d.csv" % k
        dev_test_filename = "../split_data/dev_test.k%d.csv" % k

        model = train(dev_train_filename, topics, alpha, max_iter, beta)

        # Apply the model on the 10% ensemble training set
        com_train_pred = predict(model, com_test_filename)
        file("com_train.k%d.pred" % k, "w").writelines(["%f\n" % pred for pred in com_train_pred])

        # Apply the model on the 10% test set
        dev_test_pred = predict(model, dev_test_filename)
        file("dev_test.k%d.pred" % k, "w").writelines(["%f\n" % pred for pred in dev_test_pred])

        dev_test_k_pred += dev_test_pred

    file("dev_test.k.pred", "w").writelines(["%f\n" % pred for pred in dev_test_k_pred])
    os.system("../evaluate/evaluate_dev_test.R dev_test.k.pred ../split_data/dev_test.k.labels.csv auc 2> /dev/null")
    auc = float(file("auc").read().rstrip())
    print "Model 3: AUC on the training set: %.6f" % auc
    
def full(topics, alpha, beta, max_iter):
    all_train_filename = "../split_data/all_train.csv"
    all_test_filename = "../../data/test_data.csv"

    model = train(all_train_filename, topics, alpha, max_iter, beta)

    predictions = predict(model, all_test_filename, skip=1)
    file("all_test.pred", "w").writelines(["%f\n" % pred for pred in predictions])

if __name__ == "__main__":
    random.seed(1)

    topics_filename = "../../data/topics.csv"
    topics = read_topics(topics_filename)

    alpha = 0.02                # learning rate
    beta = 0.01                 # controls penalty from regularizers
    max_iter = 100

    # Run 10-fold cross validation on the training set
    evaluate(topics, alpha, beta, max_iter)

    # Train a model against the entire training set and predict the test set
    full(topics, alpha, beta, max_iter)
