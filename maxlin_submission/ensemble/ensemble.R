#!/usr/bin/env RScript
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

read.data <- function(name, ensemble, k) {
  x <- NULL
  for (b in ensemble) {
    xp <- read.table(sprintf("../%s/%s.k%d.pred", b, name, k))
    if (is.null(x)) {
      x <- xp
    } else {
      x <- cbind(x, xp)
    }
  }

  y <- as.numeric(read.table(sprintf("../split_data/%s.k%d.labels.csv", name, k))[, 1])

  return (data.frame(x, installed = y))
}

read.all.test <- function(ensemble) {
  x <- NULL
  for (b in ensemble) {
    xp <- read.table(sprintf("../%s/all_test.pred", b))
    if (is.null(x)) {
      x <- xp
    } else {
      x <- cbind(x, xp)
    }
  }

  return (data.frame(x, installed = rep(NA, nrow(x))))
}

evaluate <- function(ensemble) {
  all.pred <- NULL

  models <- list(1,2,3,4,5,6,7,8,9,10)
  for (k in 0:9) {
    print(sprintf("Fold %d", k))

    # Prepare training data for ensemble learners
    train <- read.data("com_train", ensemble, k)
    
    model <- glm(installed ~ .,
                 data = train,
                 family=binomial(link='logit'),
                 control=glm.control(trace=TRUE))
    models[[k+1]] <- model

    # Predict on the 10% test set
    test <- read.data("dev_test", ensemble, k)
    
    pred <- predict(model, test, type="response")
    all.pred <- c(all.pred, pred)
  }

  truth <- as.numeric(read.table("../split_data/dev_test.k.labels.csv")[, 1])
  pred.obj <- prediction(all.pred, truth)
  auc <- performance(pred.obj, "auc")@y.values[[1]]
  print(sprintf("Ensemble: AUC on the training set: %.6f", auc))

  return(models)
}

full <- function(ensemble, mdoels) {
  all.test <- read.all.test(ensemble)
  
  all.test.preds <- NULL
  for (k in 1:10) {
    pred <- predict(models[[k]], all.test, type="response")

    all.test.preds <- cbind(all.test.preds, pred)
  }

  write.table(rowSums(all.test.preds) / 10.0,
              file=sprintf("all_test.pred"),
              row.names=FALSE, col.names=FALSE)
}

ensemble <- c("model1", "model2", "model3", "model4")

# Run 10-fold cross validation on the training set
models <- evaluate(ensemble)

# Train a model against the entire training set and predict the test set
full(ensemble, models)
