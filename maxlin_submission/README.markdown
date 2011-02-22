Max Lin's Submission
====================

Max Lin developed the codes in the directory for his submission to the
[R recommendation engine contest] [1], held by [Dataists] [2] and
[Kaggle] [3].  This file describes the steps he took to train
classifiers and generate his final submission.  For more background on
the classification models behind these scripts, please see the [post]
[4].

The programs are written in R and Python.

Steps
-----

Suppose the root of this directory is stored in an envirnment variable
`BASE`.

    $ export BASE=/path/to/r_recommendation_system/maxlin_submission

1. Split training data into 3 subsets and repeat 10 times for cross
   validation.

        $ (cd ${BASE}/split_data && split_data.py)

2. Train Model 1

        $ (cd ${BASE}/model1 && ./model1.R)

3. Train Model 2

        $ (cd ${BASE}/model2 && ./model2.py)

4. Train Model 3

        $ (cd ${BASE}/model3 && ./model3.py)

5. Train Model 4

        $ (cd ${BASE}/model4 && ./model4.py)

6. Train ensemble combiners

        $ (cd ${BASE}/ensemble && ./ensemble.R)

7. Generate two post-processing filters and apply them to generate
   final submission file, `submission.csv`.

        $ (cd ${BASE}/post_processing && ./seen_pairs.py)
        $ (cd ${BASE}/post_processing && ./depends.py)

        $ (cd ${BASE}/post_processing && ./post_processing.py)

Contact
-------
You can reach Max Lin by email, max at m4xl1n dot com.

License
-------
The source codes in this directory are licensed under Apache 2.0.

<pre>
   Copyright 2011 Max Lin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
</pre>

[1]: http://www.kaggle.com/R "The R Recommendation Engine Contest"
[2]: http://www.dataists.com/ "Dataists"
[3]: http://www.kaggle.com/ "Kaggle"
[4]: http://globalmaximum.wordpress.com/2011/02/21/how-i-developed-a-r-package-recommendation-engine/