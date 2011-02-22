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

all.test <- read.csv("../../data/test_data.csv")

seen.pairs <- read.csv("seen_pairs.csv")
depends <- read.csv("depends.csv")

pred <- read.table("../ensemble/all_test.pred")[, 1]

pred[!is.na(seen.pairs$Installed)] <- seen.pairs[!is.na(seen.pairs$Installed), "Installed"]
pred[!is.na(depends$Installed)] <- 1.0

write.table(data.frame(Package=all.test[,1], User=all.test[, 10], Installed=pred),
            file="submission.csv",
            sep=",", row.names=FALSE, col.names=TRUE, quote=FALSE)
