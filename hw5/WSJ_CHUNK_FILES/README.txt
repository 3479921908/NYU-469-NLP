You will write a Noun Group tagger, using similar data that you used for Homework 3. However, for this program we will focus more on feature selection than on an algorithm.
Download the WSJ_CHUNKFILES.zip from NYU Drive. This includes the following data files
WSJ_02-21.pos-chunk -- the training file
WSJ_24.pos  -- the development file that you will test your system on
WSJ_24.pos-chunk -- the answer key to test your system output against
WSJ_23.pos -- the test file, to run your final system on, producing system output
Download MAX_ENT_files.zip, also from NYU Drive. This includes the following program files (using the OpenNLP package):
maxent-3.0.0.jar,  MEtag.java. MEtrain.java  and trove.jar -- Java files for running the maxent training and classification programs
score.chunk.py -- A python 3 scoring script
Create a program that takes a file like WSJ_02-21.pos-chunk as input and produces a file consisting of feature value pairs for use with the maxent trainer and classifier. As this step represents the bulk of the assignment, there will be more details below, including the format information, etc. This program should create two output files. From the training corpus (WSJ_02-21.pos-chunk), create a training feature file (training.feature). From the development corpus (WSJ_24.pos), create a test feature file (test.feature). See details below.
Compile and run MEtrain.java, giving it the feature-enhanced training file as input; it will produce a MaxEnt model. MEtrain and MEtest use the maxent and trove packages, so you must include the corresponding jar files, maxent-3.0.0.jar and trove.jar, on the classpath when you compile and run. Assuming all java files are in the same directory, the following command-line commands will compile and run these programs -- these commands are slightly different for posix systems (Linux or Apple), than for Microsoft Windows.
For Linux, Apple and other Posix systems, do:
javac -cp maxent-3.0.0.jar:trove.jar *.java ### compiling
java -cp .:maxent-3.0.0.jar:trove.jar MEtrain training.feature model.chunk ### creating the model of the training data
java -cp .:maxent-3.0.0.jar:trove.jar MEtag test.feature model.chunk response.chunk ### creating the system output

For Windows Only -- Use semicolons instead of colons in each of the above commands, i.e., the command for Windows would be:
javac -cp maxent-3.0.0.jar;trove.jar *.java ### compiling
java -cp .:maxent-3.0.0.jar;trove.jar MEtrain training.chunk model.chunk ### creating the model of the training data
java -cp .:maxent-3.0.0.jar;trove.jar MEtag test.chunk model.chunk response.chunk ### creating the system output
Quick Fixes
If the system is running out of memory, you can specify how much RAM java uses. For example, java -Xmx16g -cp ... will use 16 gigabytes of RAM.
If your system cannot find java files or packages and just doesn't run for that reason, the easiest fix is to run (the java steps) on one of NYU's linux servers. Accounts can be made available to all students in this class. Alternatively, you can make sure that all path variables are set properly, that java is properly installed, etc.
Score your results with the python script as follows:
python score.chunk.py WSJ_24.pos-chunk response.chunk ### WSJ_24.pos-chunk is the answer key and response.chunk is your output file
When you are done creating your system, create a test.feature file from the test corpus (WSJ_23.pos) and execute step 1.4.1.3 (or 1.4.2.3) to create your final response file (WSJ_23.chunk). Your submission to gradescope must contain the file WSJ_23.chunk or it will not be able to grade your work.
This pipeline is set up so you can write the code for producing the feature files in any programming language you wish. You have the alternative of using any Maxent package you would like, provided that the scoring script works on your output.
As mentioned in section 1.3, you are primarily responsible for a program that creates sets of features for the Maximum Entropy system.
Format Information:
There should be 1 corresponding line of features for each line in the input file (training or test)
If the input and feature files have different numbers of lines, you have a bug
Blank lines in the input file should correspond to blank lines in your feature file
Each line corresponding to text should contain tab separated values as follows:
the first field should be the token (word, puncutation, etc.)
this should be followed by as many features as you want (but no feature should contain white space). Typically, features are recommended to have the form attribute=value, e.g., POS=NN
This makes the features easy for humans to understand, but is not actually required by the program, e.g., the code does not look for the = sign.
for the training file only, the last field should be the BIO tag (B-NP, I-NP or O)
for the test file, there should be no final BIO field (as there is none in the .pos file that you would be training from)
A sample training file line (where \t represents tab):
'fish\tPOS=NN\tprevious_POS=DT\tprevious_word=the\tI-NP ## actual lines will probably be longer
There is a special symbol '@@' that you can use to refer to the previous BIO tag, e.g., Previous_BIO=@@
This allows you to simulate a (bigram) MEMM because you can refer to the previous BIO tag
Suggested features:
Features of the word itself: POS, the word itself, stemmed version of the word
Similar features of previous and/or following words (suggestion: use the features of previous word, 2 words back, following word, 2 words forward)
Beginning/Ending Sentence (at the beginning of the sentence, omit features of 1 and 2 words back; at end of sentence, omit features of 1 and 2 words forward)
capitalization, features of the sentence, your own special dictionary, etc.
When you have completed the assignment, submit the following in a zip file through GradeScope (link to be added):
Your code
A short write-up describing the features you tried and your score on the development corpus.
Your output file from the test corpus, i.e., WSJ_23.chunk. Your submission to gradescope must contain the file WSJ_23.chunk or it will not be able to grade your work.
Understanding the scoring:
Accuracy = (correct BIO tags)/Total BIO Tags
Precision, Recall and F-measure measure Noun Group performance: A noun group is correct if it in both the system output and the answer key.
Precision = Correct/System_Output
Recall = Correct/Answer_key
F-measure = Harmonic mean of Precision and Recall
Evaluation: A simple system should achieve about 90% F-measure. It is possible, but difficult to obtain 95-96%. Your grade will be judged as follows (for a maximum of 12 points):
2 points for format issues (correct filenames, correct line format)
10 points based on your f-measure: 1 point for an f-measure above 0; 2 points for an f-measure above 50; 3 if above 70; 4 if above 80; 5 if above 85; 6 if above 90; 7 if above 91; 8 if above 92; 9 if above 93; 10 if above 95.