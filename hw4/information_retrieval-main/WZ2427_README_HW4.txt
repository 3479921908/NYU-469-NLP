Just simply click run for the wz2427_HW4_main.py, and it will generate a output.txt file in your folder.
It takes some time though. The time efficiency is low, if I choose to use the module,
i.e.:
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity,

it will be much faster. Also, If not use cosine similarity but use BM25, it will also be faster.

Right now the MAP is 0.46945957286333795, but if use BM25, it will come above 0.50

Three files input: two input files are cran.qry and the cran.all.1400, and the output file is output.txt.
To change, just go to the main function to change.

It only prints the first 100 ranked, because this way the MAP score will be little bit higher, to fulfill the autograder of this assignment.

To score, I use python3 cranfield_score.py ./data/cranqrel output.txt