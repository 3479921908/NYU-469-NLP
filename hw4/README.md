Create a system for an Ad Hoc Information Retrieval task using TF-IDF weights and cosine similarity scores. Vectors should be based on all the words in the query, after removing the members of a list of stop words. Create the system in the following steps:
Download (and unpack) the zip file: Cranfield_collection_HW.zip. It contains the following documents:
The Cranfield collection --- also avaialble from http://ir.dcs.gla.ac.uk/resources/test_collections/cran/. This includes a readme that describes the data, but further details are provided here:
cran.qry -- contains a set of 225 queries numbered 001 through 365, but referred to in cranqrel below as 1 through 225 -- this is an important detail which, if missed, can make debugging confusing.
Lines beginning with .I are ids for the queries (001 to 365)
Lines following .W are the queries
cran.all.1400 -- contains 1400 abstracts of aerodynamics journal articles (the document collection)
Lines beginning with .I are ids for the abstracts
Lines following .T are titles
Lines following .A are authors
Lines following .B are some sort of bibliographic notation
Lines following .W are the abstracts
cranqrel is an answer key. Each line consists of three numbers separated by a space
the first number is the query id (1 through 225) --- convert 001 to 365 by position: 001 --> 1, 002 --> 2, 004 --> 3, ... 365 --> 225
the second number is the abstract id (1 through 1400)
the third number is a number (-1,1,2,3 or 4)
These numbers represent how related the query is to the given abstract
Unrelated query/abstract pairs are not listed at all (they would get a score of 5): There are 1836 lines in cranqrel. If all combinations were listed, there would be 225 * 1400 = 315,000 lines.
We will treat -1 as being the same as 1. We suspect it means something like "the best choice for the query", but the specs don't say.
A stoplist (currently written in python) called stop_list.py -- you can use this list to eliminate words that you should not bother including in your vectors
A sample output file ( sample_cranfield_output.txt). You can use this as a guide to the format of your output and also to test the scorer. It was created by randomly changing the answer key. You should not seriously compare it to your output file.
For each query, create a feature vector representing the words in the query:
Calculate IDF scores for each word in the collection of queries (after removing stop words, punctuation and numbers)
Count the number of instances of each non-stop-word in each query
The vector lists the TF-IDF scores for the words in the vector
Compute the IDF scores for each word in the collection of abstracts, after removing stop words, punctuation and numbers.
Count the number of instances of each non-stop-word in each abstract
For each query
For each abstract,
Create a vector representing scores for words in the query, based on their TF-IDF values in the abstract, e.g., if the only words contained in both query and abstract are "chicken" and "fish", then values in the vector representing these words would have non-zero values and the other values in the vector would be zero. The vector would be the same length as the query's vector.
Calculate the cosine similarity between vectors for query and abstract
Sort the abstracts by cosine similarity scores. So for each query there should be a ranking of between 100 and 1400 documents (the sample output file which contains 225*1400=315,000 lines)
For tokenization, you can use nltk if you want, but if you use some other system of tokenization, please indicate what rules you use.
Your final output should look similar to cranqrel: the first column should be the query number, the second column should be the abstract number, and the third column should be the cosine similarity score. For each query, list the abstracts in order from highest scoring to lowest scoring, based on cosine-similarity. Note that your third column will be a different sort of score than the answer key score -- that is OK. Example line:
1 304 0.273

Additional Factors:
There is an alternative framing of the problem in which the vectors used for all documents and all queries have the same length and the features represent the same set of words. One could select N words with the highest IDF scores or perhaps all the words found in the queries. Under that framing, the presense and the absense of words would effect the final results.
The description so far does not account for cases where there are zero counts. Some of the above formulas can become undefined if one attempts to divide or take the log of zero. This factor problem can be avoided by adding one to all counts in all formulas. This is important if you implement the previous bullet.
Systems will be evaluated by the metric: Mean Average Precision based on the precision of your system at each 10% recall level from 10 to 100%.
For each query, establish 10 cutoffs based on recall: 10%, 20%, ... 100%
Average the precision of these 10 cutoffs.
Average these precision scores across all queries, ignoring a query if the system gets a recall score of 0 or if there are no matching abstracts.
To score your system, submit it to gradescope and it will run a scoring script (an implementation of MAP). It will assume that you provide at least 100 ranked candidate matches for each query -- you need not rank all 1400 documents if they have low scores (as noted above). You can resubmit as many times as you'd like.
A Mapscore of about 20% is normal for this task (although higher scores are possible). Ultimate grades will be based on the results of the class. A general rule of thumb for determining if your system is working is: if your MAP score is in double digits, it is probably working OK. If you are getting a score of less than 3% MAP, there is probably something wrong. [Most likely, it is a format error.]
Possible extensions to make the system work better:
Add additional features: incorporate stemming (e.g., treat plural/singular forms as single terms)
Determine if there is a correlation between the TF-IDF based ranks and the relevance score ranks and find a way to predict the rankings, or to simplify the rankings and predict the simplified rankings.
We initially assume a simple method of counting term frequency: a straight count of the number of times a term occurs in a document. However, in practice, there is usually some adjustment for the length of the document, for example:
Divide this count by the number of words in the document
Use the logarithm of the term frequency
Use 1 if the term exists in the document and 0 if it does not
Combine some of the above methods together
Try more than one of these methods and determine which method achieves the highest scores.
If you eliminate items from the ranked lists when the cosine similarity value is 0, the MAP score will improve. However, the scoring program will score your system as if there are a minimum of 100 attempted matches for each query. So there is no benefit for outputing less than 100 matches.
One hypothetical optimization would be to use the same set of words for all queries and all vectors. The difficulty is in choosing the words and the size of the vector. For example, you could try using the top N IDF score words (based on the query corpus or based on the abstract corpus). For this to work well, it may be the case that at least one key word for each query needs to be included in the vector. Note that both the absense and presense of words may make vectors more similar to each other.
Grading is based on your final MAP score (which is typically higher if you implemented additional options), as well as basic format considerations. If your files are correctly named and formatted, you will get 3 points. If your system works, you should expect to get the remaining 9 points based on your score, as follows: 1% MAP: 1 point; 10% MAP; 2 points; 15% MAP; 3 points; 20% MAP; 4 points; 25% MAP; 5 points; 30% MAP; 6 points; 35% MAP; 7 points (this is generally the median range) 40% MAP; 8 points over 45% MAP; 9 points (a full score)
Submit the following to GradeScope in a zip file called NetID-HW4.zip, e.g., alm4-HW4.zip. The zip file should contain:
Your source code
Instructions for running your system (NetID_README_HW4.txt)
Your output file (output.txt) in the format described above. It should look very similar to cranqrel and you should make sure that the scoring program works on it. The main differences are:
your cosine similarity score should be the third column instead of a -1 to 4 ranking
If you get an error submitting a zip file, you can submit all the files unzipped. Remember, do not include any directories in your zip file (do not include Apple's __MACOSX directory in the zip file).
