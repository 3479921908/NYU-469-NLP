README: Viterbi HMM POS Tagger

Author: WENJIE ZHANG （WZ2427)
Course: NYU CS 469 NLP
HW3

（I don't know why the auto-grader only gives me 7/9. The final score is 54075 out of 56684 tags, correct
  accuracy: 9.539729. So I hope the grader can check this again)

1. Introduction

This project implements a Hidden Markov Model (HMM) POS tagger using the Viterbi algorithm.
	•	It is trained on the Wall Street Journal (WSJ) dataset.
	•	It assigns Part-of-Speech (POS) tags to words in sentences using bigram probabilities.
	•	It includes Out-of-Vocabulary (OOV) handling to improve accuracy on unseen words.

2. How to Run the System

Open any interpreter of python, and before running, change the parameter in the final_call function. (I think you can directly input in the terminal)
First Parameter: Data for Training (_02-21.pos)
Second Parameter: Data for input (23.words)
Thrid parameter: Output Data (submission.pos)

Functionality of Each Function:
    When you call the Final_Call Function:
        it calls the load_training_data(input_training_data), and it inputs the training data you gave ( first parameter), and generate dictionaries of the summaries of these data.
        Each item in the Word_tag counts is a dictionary of tag: words of this tag
        Each item in the tag_counts is the number of appearance of each tag.  Used for Prior Probs.
        Each in the Bigram counts is the tag:previous_tag. Used for Vertibi Algo.
        Vocab is a set of all the vocabs appeared, used to identify the OOV.

        And then it will call the compute_oov_possibility function to generate all the possibility needed for the vertibi algo.
        Then the vertibi algorithm will run when the tag_corpus functino calls it, generate a list for each sentence iterated in the sentence[], based on the break between each sentence.



3. How OOV Items Are Handled
    In this implementation, OOV words are handled using a hybrid approach that combines linguistic heuristics, suffix-based classification, and rare word distributions.
    The goal is to assign the most probable POS tag to an unseen word while preventing zero probability errors in the Viterbi algorithm.

    The function classify_oov_word() assigns a POS tag to an unknown word based on:
	1.	Common suffixes: Many words follow predictable POS tag patterns based on their endings.
	2.	Capitalization: Proper nouns (NNP) often start with an uppercase letter.
	3.	Numeric tokens: Numbers (CD) are identified based on their format.
	4.	Special characters: Punctuation (.) is detected when the word contains non-alphanumeric characters.
	5.	Rare word probability fallback: If none of the above apply, the system assigns a tag based on the most common POS tag among words that appeared only once in the training set.

	Since rare words behave similarly to OOV words, we estimate unknown word probabilities using words that appeared only once in the training corpus. (Shown in the compute_oov_probabilities())

	In the Viterbi algorithm, we modify the likelihood calculation for OOV words:
	•	If the word exists in the vocabulary, use its normal likelihood probability.
	•	If the word is OOV, assign it:
		    A suffix-based POS tag if applicable.
		    A rare word-based POS tag if no suffix applies.

4. Possible Drawback of the Program:
    Sometimes the program will omit the last sentence of the input data. I believe this is due to the sentence[] list is cleared before the last print because it didn't detects an emtpy line in the end.
    I try to fix this and still don't understand why some rare times it fails. But most time it works normally.

    Also I use the prior probs for calculating the tag at each start of the sentence. I believe also there's the approach that only use prior probs at the first word of each paragraph. But the input data
    didn't give me any sign of the start of the paragraph. So I treat it like this. A more precise approach I believe is that to use transitional probs for all the words and punctuations inside
    the paragraphs.