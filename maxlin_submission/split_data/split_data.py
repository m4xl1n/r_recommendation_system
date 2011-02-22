#
#     Copyright 2011 Max Lin
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Split training data, training_data.csv, into the following 3 files,
# and repeat 10 times for cross validation.
#
# dev_train.k%d.csv - 80% for training individual classifiers
# com_train.k%d.csv - 10% for training ensemble
# dev_test.k%d.csv - 10% for evaluating classifiers

import random

def extract_labels(lines):
    labels = []
    for line in lines:
        pieces = line.rstrip().split(",")
        labels.append("%s\n" % pieces[10])

    return labels

if __name__ == "__main__":
    training_filename = "../../data/training_data.csv"

    dev_train_ratio = 0.8
    com_train_ratio = 0.1
    dev_test_ratio = 0.1
    K = 10
    seed = 1

    random.seed(seed)

    all_train = file(training_filename).readlines()
    all_train = all_train[1:]       # ignore headers
    file("all_train.csv", "w").writelines(all_train)

    all_train_num_instances = len(all_train)

    random.shuffle(all_train)

    dev_test_labels = []
    dev_train_composed = all_train
    for k in range(10):
        dev_train = dev_train_composed[0:int(all_train_num_instances * dev_train_ratio)]
        file("dev_train.k%d.csv" % k, "w").writelines(dev_train)
        file("dev_train.k%d.labels.csv" % k, "w").writelines(extract_labels(dev_train))

        com_train = dev_train_composed[int(all_train_num_instances * dev_train_ratio):int(all_train_num_instances * (dev_train_ratio + com_train_ratio))]
        file("com_train.k%d.csv" % k, "w").writelines(com_train)
        file("com_train.k%d.labels.csv" % k, "w").writelines(extract_labels(com_train))

        dev_test = dev_train_composed[int(all_train_num_instances * (1.0 - dev_test_ratio)): all_train_num_instances]
        file("dev_test.k%d.csv" % k, "w").writelines(dev_test)
        file("dev_test.k%d.labels.csv" % k, "w").writelines(extract_labels(dev_test))

        dev_test_labels += extract_labels(dev_test)
        dev_train_composed = dev_test + dev_train + com_train

    file("dev_test.k.labels.csv", "w").writelines(dev_test_labels)
