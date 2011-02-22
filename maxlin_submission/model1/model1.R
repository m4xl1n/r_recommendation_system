#!/bin/env RScript
##
##    Copyright 2011 Max Lin
##
##    Licensed under the Apache License, Version 2.0 (the "License");
##    you may not use this file except in compliance with the License.
##    You may obtain a copy of the License at
##
##        http://www.apache.org/licenses/LICENSE-2.0
##
##    Unless required by applicable law or agreed to in writing, software
##    distributed under the License is distributed on an "AS IS" BASIS,
##    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##    See the License for the specific language governing permissions and
##    limitations under the License.

library(ROCR)

col.names <- c("Package", "DependencyCount", "SuggestionCount",
               "ImportCount", "ViewsIncluding", "CorePackage",
               "RecommendedPackage", "Maintainer",
               "PackagesMaintaining", "User", "Installed",
               "LogDependencyCount", "LogSuggestionCount",
               "LogImportCount", "LogViewsIncluding",
               "LogPackagesMaintaining")

train <- function(train.filename) {
  train.dat <- read.table(train.filename, col.names=col.names, sep=",")
  
  model <- glm(Installed ~ LogDependencyCount + LogSuggestionCount +
               LogImportCount + LogViewsIncluding +
               LogPackagesMaintaining + CorePackage +
               RecommendedPackage + factor(User),
               data = train.dat, family=binomial(link='logit'),
               control = glm.control(trace = TRUE, maxit = 25))

  return(model)
}

evaluate <- function() {
  dev.test.pred <- c()

  for (k in 0:9) {
    print(sprintf("Fold %d", k))
    
    train.filename <- sprintf("../split_data/dev_train.k%d.csv", k)
    com.filename <- sprintf("../split_data/com_train.k%d.csv", k)
    test.filename <- sprintf("../split_data/dev_test.k%d.csv", k)
    
    model <- train(train.filename)

    ## Apply the model on the 10% ensemble training set
    com <- read.table(com.filename, col.names=col.names, sep=",")
    
    write.table(predict(model, com, type="response"),
                file=sprintf("com_train.k%d.pred", k),
                row.names=FALSE, col.names=FALSE)

    ## Apply the model on the 10% test set
    test <- read.table(test.filename, col.names=col.names, sep=",")
    pred <- predict(model, test, type="response")
    write.table(pred,
                file=sprintf("dev_test.k%d.pred", k),
                row.names=FALSE, col.names=FALSE)
    
    dev.test.pred <- c(dev.test.pred, pred)
  }

  truth <- read.table("../split_data/dev_test.k.labels.csv")
  pred.obj <- prediction(dev.test.pred, truth)
  write.table(dev.test.pred,
              file=sprintf("dev_test.k.pred", k),
              row.names=FALSE, col.names=FALSE)

  auc <- performance(pred.obj, "auc")@y.values[[1]]

  sprintf("Model 1: AUC on the training set: %.6f", auc)
}

full <- function() {
  model <- train(sprintf("../split_data/all_train.csv"))
  test <- read.csv("../../data/test_data.csv")
  pred <- predict(model, test, type="response")
  write.table(pred,
              file="all_test.pred",
              row.names=FALSE, col.names=FALSE)
}

# Run 10-fold cross validation on the training set
evaluate()

# Train a model against the entire training set and predict the test set
full()
