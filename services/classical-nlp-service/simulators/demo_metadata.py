"""
Demo initialization metadata for all classical NLP simulators.
Each algorithm gets research-backed demo input, parameters, explanations, formulas, and references.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))

from shared_schemas import (
    DemoMetadata,
    FormulaCard,
    StepExplanation,
    HoverAnnotation,
    ReferenceEntry,
    ReceiverModeExplanation,
    TeachingNotes,
    ReceiverMode,
)


# ──────────────────────────────────────────────────────────────────────────────
# Tokenization Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

tokenization_demo = DemoMetadata(
    demo_input={
        "text": "Hello world! This is a sample sentence for tokenization. Let's see how it works - 123, test."
    },
    auto_parameters={
        "tokenizer_type": "word",
        "lowercase": True,
        "remove_punctuation": False,
        "split_contractions": True,
    },
    expected_output_preview={
        "tokens": ["hello", "world", "!", "this", "is", "a", "sample", "sentence", "for", "tokenization", ".", "let's", "see", "how", "it", "works", "-", "123", ",", "test", "."],
        "token_count": 21,
        "unique_tokens": 20,
    },
    beginner_explanation="Tokenization is like splitting a sentence into individual words or pieces. It's the first step in almost all NLP tasks - like breaking a chocolate bar into small, manageable pieces before eating.",
    advanced_explanation="Tokenization segments text into tokens (words, subwords, or characters) based on whitespace, punctuation, and language-specific rules. It enables downstream tasks like vectorization, parsing, and model input preparation. Common approaches include word tokenization, subword tokenization (BPE, WordPiece), and character tokenization.",
    formula_cards=[
        FormulaCard(
            title="Tokenization Function",
            formula="T = tokenize(s) = [w₁, w₂, ..., wₙ]",
            explanation="A tokenization function maps a string s to an ordered list of tokens T.",
            variables={"s": "input string", "T": "list of tokens", "n": "number of tokens"},
            example="tokenize('Hello world!') → ['Hello', 'world', '!']",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="t1",
            stage="input_validation",
            title="Validate Input Text",
            description="Check that the input text is non-empty and is a valid string.",
            input_preview={"text": "Hello world! This is a sample sentence..."},
            output_preview={"valid": True, "text_length": 85},
            why_it_matters="Invalid input (empty, None, or non-string) would cause downstream errors in tokenization and all subsequent steps.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="t2",
            stage="preprocessing",
            title="Normalize Text",
            description="Apply lowercase transformation and initial cleaning if configured.",
            input_preview={"text": "Hello world! This is a sample sentence..."},
            output_preview={"text": "hello world! this is a sample sentence..."},
            why_it_matters="Normalization ensures consistent processing regardless of input casing, improving model robustness.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="t3",
            stage="tokenization",
            title="Split into Tokens",
            description="Split the normalized text on whitespace and punctuation boundaries to produce individual tokens.",
            input_preview={"text": "hello world! this is a sample sentence..."},
            output_preview={"tokens": ["hello", "world", "!", "this", "is", "..."]},
            formula="T = split(text)",
            why_it_matters="Tokens are the fundamental units that all downstream NLP algorithms operate on - like atoms in a molecule.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="t4",
            stage="output",
            title="Generate Token Statistics",
            description="Compute token count, unique tokens, and optionally remove punctuation or stop words.",
            input_preview={"tokens": ["hello", "world", "!", "..."]},
            output_preview={"token_count": 21, "unique_tokens": 20},
            why_it_matters="Token statistics help understand text complexity and are used by downstream algorithms like TF-IDF.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="tokens",
            definition="Individual units extracted from text, typically words or subwords.",
            formula_meaning="wᵢ represents the i-th token in the sequence",
            example="In 'Hello world', tokens are ['Hello', 'world']",
            common_mistake="Assuming tokens are always words - punctuation and numbers can also be tokens",
            reference_label="Tokenization (NLP)",
        ),
        HoverAnnotation(
            target="token_count",
            definition="The total number of tokens in the tokenized text.",
            formula_meaning="n = |T| where T is the token list",
            example="21 tokens in the demo sentence",
            common_mistake="Counting characters instead of tokens",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Speech and Language Processing",
            authors="Jurafsky, D. and Martin, J.H.",
            year=2024,
            url="https://web.stanford.edu/~jurafsky/slp3/",
            relevance="Chapter 2 covers tokenization and text normalization fundamentals.",
        ),
        ReferenceEntry(
            title="Natural Language Processing with Python",
            authors="Bird, S., Klein, E., and Loper, E.",
            year=2009,
            url="https://www.nltk.org/book/ch03.html",
            relevance="NLTK book chapter on processing raw text and tokenization.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="Tokenization splits text into words. Try changing the sentence and see how the tokens change!",
            teaching_notes="Use the default demo sentence. Ask students to predict token count before running.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="Tokenization uses regex or whitespace splitting. The formula T = tokenize(s) maps string → list of tokens.",
            technical_detail="Common tokenizers: word_tokenize (NLTK), TokTok, and whitespace split. Subword tokenization uses BPE or WordPiece for OOV handling.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="Tokenization choices affect downstream performance. Subword methods (BPE, WordPiece) handle OOV better than word-level tokenization.",
            technical_detail="Research shows subword tokenization improves performance on morphologically rich languages and rare words (Sennrich et al., 2016).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="Tokenization is O(n) where n is character count. Use pre-compiled regex patterns for speed. Consider using spaCy or transformers tokenizer for production.",
            technical_detail="Complexity: O(n). Memory: O(n) for token list. API returns token list and statistics.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="Tokenization is the foundation of NLP. Show how punctuation, contractions, and numbers are handled differently.",
            teaching_notes="Quiz: How many tokens in 'I'm learning NLP!'? Discuss why 'I'm' might be 1 or 2 tokens. Demo with different languages.",
        ),
    ],
    research_context="Tokenization is the foundational step in all NLP pipelines. Research has evolved from simple whitespace splitting to subword algorithms (BPE, WordPiece, Unigram) that balance vocabulary size and coverage.",
    teaching_notes=TeachingNotes(
        summary="Tokenization splits text into meaningful units for NLP processing.",
        quiz_questions=[
            "What is the difference between word and subword tokenization?",
            "Why might 'I'm' be tokenized as 1 or 2 tokens?",
            "How does tokenization affect downstream tasks like classification?",
        ],
        classroom_demo_tips=[
            "Show tokenization of the same sentence in different languages",
            "Compare whitespace vs. rule-based tokenization",
            "Highlight challenges with social media text and emojis",
        ],
        common_misconceptions=[
            "Tokenization always splits on spaces (false - punctuation matters)",
            "More tokens always means more information (false - stop words add noise)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# TF-IDF Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

tfidf_demo = DemoMetadata(
    demo_input={
        "documents": [
            {"id": "d1", "text": "The cat sat on the mat."},
            {"id": "d2", "text": "The dog played with the ball."},
            {"id": "d3", "text": "The cat and dog are friends."},
        ]
    },
    auto_parameters={
        "max_features": 1000,
        "min_df": 1,
        "max_df": 1.0,
        "use_idf": True,
        "smooth_idf": True,
        "sublinear_tf": False,
    },
    expected_output_preview={
        "vocabulary": ["cat", "dog", "sat", "mat", "played", "ball", "friends"],
        "idf_scores": {"cat": 1.0, "dog": 1.0, "sat": 1.7, "mat": 1.7},
        "tfidf_matrix_shape": [3, 7],
    },
    beginner_explanation="TF-IDF helps find important words in a document by checking how often a word appears in that document versus how rare it is across all documents. Common words like 'the' get low scores, unique words get high scores.",
    advanced_explanation="TF-IDF (Term Frequency-Inverse Document Frequency) weighs terms by their frequency in a document (TF) and inversely by their frequency across documents (IDF). It transforms text into a numerical vector space where similar documents are close together. TF-IDF is computed as TF(t,d) × IDF(t), where IDF(t) = log(N / df(t)).",
    formula_cards=[
        FormulaCard(
            title="Term Frequency (TF)",
            formula="TF(t, d) = f_{t,d} / Σ_{t'∈d} f_{t',d}",
            explanation="TF measures how frequently a term t appears in document d, normalized by the total number of terms in d.",
            variables={"t": "term", "d": "document", "f_{t,d}": "raw frequency of term t in document d"},
            example="In 'cat cat dog', TF('cat') = 2/3, TF('dog') = 1/3",
        ),
        FormulaCard(
            title="Inverse Document Frequency (IDF)",
            formula="IDF(t) = log(N / df(t))",
            explanation="IDF measures how rare a term is across all N documents. Rare terms get higher IDF scores.",
            variables={"N": "total number of documents", "df(t)": "number of documents containing term t"},
            example="With 3 docs, if 'cat' appears in 2 docs: IDF('cat') = log(3/2) ≈ 0.405",
        ),
        FormulaCard(
            title="TF-IDF Score",
            formula="TF-IDF(t, d) = TF(t, d) × IDF(t)",
            explanation="The final TF-IDF score combines term frequency and inverse document frequency.",
            variables={"TF(t,d)": "term frequency", "IDF(t)": "inverse document frequency"},
            example="TF-IDF('cat', doc1) = (1/3) × log(3/2) ≈ 0.135",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="tf1",
            stage="input_validation",
            title="Validate Document Collection",
            description="Ensure at least one document is provided and all documents have valid text.",
            input_preview={"document_count": 3, "documents": ["The cat sat...", "The dog played...", "..."]},
            output_preview={"valid": True, "total_terms": 15},
            why_it_matters="TF-IDF requires multiple documents to compute meaningful IDF scores. Single-document input produces degenerate results.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="tf2",
            stage="preprocessing",
            title="Tokenize and Build Vocabulary",
            description="Tokenize each document and build a global vocabulary of unique terms.",
            input_preview={"documents": ["..."]},
            output_preview={"vocabulary_size": 7, "terms": ["cat", "dog", "sat", "..."]},
            why_it_matters="The vocabulary defines the feature space dimension. Larger vocabularies capture more information but increase computational cost.",
            visualization_type="bar",
        ),
        StepExplanation(
            step_id="tf3",
            stage="computation",
            title="Compute Term Frequencies (TF)",
            description="Calculate how often each term appears in each document, normalized by document length.",
            input_preview={"tokenized_docs": ["..."]},
            output_preview={"tf_matrix_shape": [3, 7], "sample": {"cat": [0.33, 0, 0.33]}},
            formula="TF(t, d) = f_{t,d} / Σ f_{t',d}",
            why_it_matters="TF captures local importance - terms that appear frequently in a document are likely important to that document's topic.",
            visualization_type="heatmap",
        ),
        StepExplanation(
            step_id="tf4",
            stage="computation",
            title="Compute Inverse Document Frequency (IDF)",
            description="Calculate how rare each term is across all documents. Rare terms get higher scores.",
            input_preview={"vocabulary": ["..."], "doc_freqs": {}},
            output_preview={"idf_scores": {"cat": 1.0, "sat": 1.7}},
            formula="IDF(t) = log(N / df(t))",
            why_it_matters="IDF downweights common words (like 'the') that appear in every document and don't help distinguish topics.",
            visualization_type="bar",
        ),
        StepExplanation(
            step_id="tf5",
            stage="computation",
            title="Compute TF-IDF Matrix",
            description="Multiply TF and IDF scores element-wise to get the final TF-IDF matrix.",
            input_preview={"tf_matrix": ["..."], "idf_vector": ["..."]},
            output_preview={"tfidf_shape": [3, 7], "sample_row": [0.33, 0, "..."]},
            formula="TF-IDF(t, d) = TF(t, d) × IDF(t)",
            why_it_matters="The TF-IDF matrix is a numerical representation of documents that can be used for clustering, classification, and similarity search.",
            visualization_type="heatmap",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="TF",
            definition="Term Frequency - how often a term appears in a document.",
            formula_meaning="TF(t,d) = raw_count(t,d) / total_terms(d)",
            example="If 'cat' appears 2 times in a 10-word doc, TF = 0.2",
            common_mistake="Forgetting to normalize by document length (raw counts bias long documents)",
        ),
        HoverAnnotation(
            target="IDF",
            definition="Inverse Document Frequency - measures term rarity across documents.",
            formula_meaning="IDF(t) = log(N / df(t)) where N is total docs and df(t) is docs containing t",
            example="If 'cat' is in 2 of 3 docs, IDF = log(3/2) ≈ 0.405",
            common_mistake="Using log without smoothing (add 1 to df to avoid division by zero)",
        ),
        HoverAnnotation(
            target="tfidf_matrix",
            definition="A matrix where rows are documents and columns are terms, with TF-IDF scores as values.",
            formula_meaning="M[d, t] = TF(t,d) × IDF(t)",
            example="3 docs × 7 terms = 3×7 matrix with TF-IDF scores",
            common_mistake="Thinking higher values always mean more important (context matters)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="A Vector Space Model for Automatic Indexing",
            authors="Salton, G., Wong, A., and Yang, C.S.",
            year=1975,
            doi="10.1145/361219.361220",
            relevance="Original vector space model paper that introduced term weighting for information retrieval.",
        ),
        ReferenceEntry(
            title="Term-weighting approaches in automated text retrieval",
            authors="Salton, G. and Buckley, C.",
            year=1988,
            doi="10.1080/101060201300347930",
            relevance="Comprehensive study of TF-IDF and its variants for document retrieval.",
        ),
        ReferenceEntry(
            title="Scikit-learn: Machine Learning in Python",
            authors="Pedregosa, F., et al.",
            year=2011,
            arxiv_id="1201.0490",
            relevance="Section 5.2.3 documents scikit-learn's TF-IDF implementation details.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="TF-IDF finds important words by checking: Is this word common in this document? Is it rare across all documents?",
            teaching_notes="Start with 3 simple documents. Show how 'the' gets a low score and unique words get high scores.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="TF-IDF = Term Frequency × Inverse Document Frequency. Formula: TF(t,d) × log(N/df(t)).",
            technical_detail="TF normalizes by document length. IDF uses log to dampen the effect of very rare terms. Smoothing: IDF = log((N+1)/(df+1)) + 1.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="TF-IDF assumes term independence and doesn't capture semantics. It's a bag-of-words approach. Research shows BM25 (a TF-IDF variant) often outperforms vanilla TF-IDF for retrieval.",
            technical_detail="Limitations: no term ordering, no semantic similarity, sensitive to document length. Variants: BM25, TF-IDF with cosine normalization, sublinear TF (log(1+tf)).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="TF-IDF is O(N×L) where N=docs and L=avg doc length. Sparse matrix storage (scipy.sparse) is essential for large vocabularies. Use sklearn.feature_extraction.text.TfidfVectorizer.",
            technical_detail="Complexity: fit O(NL), transform O(NL). Memory: sparse matrix with shape (N, vocab_size). API returns matrix as list of lists or sparse format.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="TF-IDF bridges text and math. Show how changing one document affects all IDF scores. Compare with simple word counts.",
            teaching_notes="Quiz: Why does 'the' get a low TF-IDF score? Exercise: Add a 4th document with only 'cat' - how do IDF scores change? Discuss when TF-IDF works well vs. poorly.",
        ),
    ],
    research_context="TF-IDF was introduced by Salton et al. (1975) as part of the vector space model for information retrieval. It remains a strong baseline for text classification and retrieval tasks, though neural embeddings have surpassed it for semantic understanding.",
    teaching_notes=TeachingNotes(
        summary="TF-IDF transforms text into numerical vectors by weighing term frequency against document rarity.",
        quiz_questions=[
            "Why does IDF use log? What would happen without it?",
            "Calculate TF-IDF for 'cat' in a 3-document corpus (hint: draw the table first)",
            "When might TF-IDF fail to capture document similarity?",
        ],
        classroom_demo_tips=[
            "Show TF-IDF heatmap with 3-5 documents",
            "Add a document with all common words - watch scores drop",
            "Compare TF-IDF vectors using cosine similarity",
        ],
        common_misconceptions=[
            "TF-IDF captures word order (false - it's bag-of-words)",
            "Higher TF-IDF always means more important (false - depends on context and task)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# Naive Bayes Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

naive_bayes_demo = DemoMetadata(
    demo_input={
        "documents": [
            {"id": "d1", "text": "Great movie, really enjoyed it!", "label": "positive"},
            {"id": "d2", "text": "Terrible film, wasted my time.", "label": "negative"},
            {"id": "d3", "text": "Amazing story and great acting.", "label": "positive"},
            {"id": "d4", "text": "Boring and poorly written.", "label": "negative"},
            {"id": "d5", "text": "Best movie I have ever seen!", "label": "positive"},
            {"id": "d6", "text": "Worst experience, avoid this film.", "label": "negative"},
        ],
        "labels": ["positive", "negative"],
    },
    auto_parameters={
        "alpha": 1.0,
        "fit_prior": True,
        "model_type": "multinomial",
    },
    expected_output_preview={
        "predicted_label": "positive",
        "probabilities": {"positive": 0.85, "negative": 0.15},
        "top_features": {"great": 0.3, "amazing": 0.25, "terrible": -0.2},
        "accuracy": 1.0,
    },
    beginner_explanation="Naive Bayes is like a spam filter for text. It learns which words are common in each category (like 'great' for positive reviews) and uses that to classify new text. It assumes words are independent - a 'naive' but surprisingly effective assumption.",
    advanced_explanation="Naive Bayes applies Bayes' theorem with the 'naive' assumption of feature independence. For text classification, Multinomial NB models word counts using a multinomial distribution. The classifier computes P(class|document) ∝ P(class) × Π P(word|class). Laplace smoothing (alpha=1) handles unseen words. Despite its simplicity, it often matches or beats more complex models.",
    formula_cards=[
        FormulaCard(
            title="Bayes' Theorem",
            formula="P(C|D) = P(D|C) × P(C) / P(D)",
            explanation="The probability of class C given document D equals the likelihood times the prior, divided by the evidence.",
            variables={"C": "class", "D": "document", "P(C)": "prior probability of class"},
            example="P(positive|'great movie') ∝ P('great movie'|positive) × P(positive)",
        ),
        FormulaCard(
            title="Naive Bayes Classifier",
            formula="P(C|D) ∝ P(C) × Πᵢ P(wᵢ|C)",
            explanation="With the naive assumption, document probability equals class prior times product of word probabilities.",
            variables={"wᵢ": "i-th word in document", "P(wᵢ|C)": "probability of word given class"},
            example="P(positive|'great movie') ∝ P(positive) × P('great'|positive) × P('movie'|positive)",
        ),
        FormulaCard(
            title="Laplace Smoothing",
            formula="P(wᵢ|C) = (count(wᵢ,C) + α) / (N_C + α×|V|)",
            explanation="Smoothing prevents zero probabilities for unseen words by adding α to all counts.",
            variables={"α": "smoothing parameter (typically 1)", "N_C": "total word count in class C", "|V|": "vocabulary size"},
            example="With α=1, even unseen words get probability 1/(N_C + |V|)",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="nb1",
            stage="input_validation",
            title="Validate Labeled Documents",
            description="Ensure documents have labels and there are at least 2 classes with sufficient examples.",
            input_preview={"document_count": 6, "classes": ["positive", "negative"]},
            output_preview={"valid": True, "class_distribution": {"positive": 3, "negative": 3}},
            why_it_matters="Naive Bayes is supervised - it needs labeled examples to learn class-conditional word probabilities.",
            visualization_type="bar",
        ),
        StepExplanation(
            step_id="nb2",
            stage="preprocessing",
            title="Extract Features (Bag of Words)",
            description="Convert text to word counts for each document, creating a feature matrix.",
            input_preview={"documents": ["..."], "labels": ["..."]},
            output_preview={"feature_matrix_shape": [6, 10], "vocabulary": ["great", "movie", "terrible", "..."]},
            why_it_matters="The feature matrix represents documents numerically, enabling probabilistic computation.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="nb3",
            stage="training",
            title="Compute Class Priors P(C)",
            description="Calculate the prior probability of each class from the training data.",
            input_preview={"class_counts": {"positive": 3, "negative": 3}},
            output_preview={"priors": {"positive": 0.5, "negative": 0.5}},
            formula="P(C) = count(C) / total_documents",
            why_it_matters="Priors encode the base rate of each class. Imbalanced data leads to skewed priors.",
            visualization_type="bar",
        ),
        StepExplanation(
            step_id="nb4",
            stage="training",
            title="Compute Word Likelihoods P(w|C) with Smoothing",
            description="For each class, count word frequencies and apply Laplace smoothing to handle unseen words.",
            input_preview={"class_word_counts": {}},
            output_preview={"word_probs": {"great|positive": 0.15, "terrible|negative": 0.12}},
            formula="P(w|C) = (count(w,C) + α) / (N_C + α×|V|)",
            why_it_matters="These likelihoods are the core of the model - they determine which words are characteristic of each class.",
            visualization_type="heatmap",
        ),
        StepExplanation(
            step_id="nb5",
            stage="prediction",
            title="Predict New Document",
            description="For a new document, compute P(C|document) for each class and pick the highest.",
            input_preview={"new_text": "Great movie, really enjoyed it!", "tokenized": ["great", "movie", "..."]},
            output_preview={"predicted": "positive", "probabilities": {"positive": 0.85, "negative": 0.15}},
            formula="P(C|D) ∝ P(C) × Π P(wᵢ|C)",
            why_it_matters="This is the actual classification step - the model applies what it learned to new text.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="P(C|D)",
            definition="Posterior probability: chance of class C given the document D.",
            formula_meaning="P(C|D) ∝ P(D|C) × P(C) / P(D) - but P(D) is constant across classes so we drop it",
            example="P(positive|'great movie') = 0.85 means 85% chance the review is positive",
            common_mistake="Forgetting that posterior is proportional, not equal (missing normalization)",
        ),
        HoverAnnotation(
            target="alpha",
            definition="Laplace smoothing parameter to avoid zero probabilities.",
            formula_meaning="Adding α to all word counts ensures no P(w|C) = 0",
            example="α=1 (default) is Laplace smoothing; α=0.01 is Lidstone smoothing",
            common_mistake="Setting α=0 which causes zero probabilities for unseen words",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Naive (Bayes) at Forty: The Independence Assumption in Information Retrieval",
            authors="Lewis, D.D.",
            year=1998,
            url="https://www.cs.utexas.edu/~ml/papers/lewis-98.pdf",
            relevance="Comprehensive analysis of Naive Bayes for text classification, including the independence assumption.",
        ),
        ReferenceEntry(
            title="A Comparison of Event Models for Naive Bayes Text Classification",
            authors="McCallum, A. and Nigam, K.",
            year=1998,
            url="https://www.cs.cmu.edu/~knigam/papers/multinomial-aaai.ps",
            relevance="Compares Multinomial, Bernoulli, and Gaussian Naive Bayes for text. Multinomial works best for word counts.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="Naive Bayes counts words in positive and negative reviews, then uses those counts to guess if a new review is positive or negative.",
            teaching_notes="Use movie reviews. Show how 'great' appears mostly in positive examples.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="Naive Bayes uses P(C|D) ∝ P(C) × Π P(w|C). It assumes words are independent (the 'naive' part). Laplace smoothing handles unseen words.",
            technical_detail="Multinomial NB for word counts, Bernoulli NB for binary occurrence. The independence assumption is wrong but often doesn't hurt performance much.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="Naive Bayes is optimal if the independence assumption holds. For text, it often works well despite violations. Research shows it's competitive with SVMs on many text tasks (Rennie et al., 2003).",
            technical_detail="Limitations: can't learn feature interactions, sensitive to correlated features. Variants: Complement NB (for imbalanced data), TAN (Tree-Augmented Naive Bayes).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="MultinomialNB in sklearn is O(N×L) training, O(L) prediction. Use log probabilities to avoid underflow. Alpha=1 is Laplace smoothing.",
            technical_detail="Complexity: train O(NL), predict O(L) per doc. Memory: O(|C|×|V|) for probability table. API: sklearn.naive_bayes.MultinomialNB.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="Naive Bayes introduces probabilistic ML. Show how the 'naive' assumption simplifies computation. Compare with logistic regression later.",
            teaching_notes="Quiz: Why 'naive'? Exercise: Manually compute P(positive|'great movie'). Discuss: When would NB fail?",
        ),
    ],
    research_context="Naive Bayes for text classification was popularized by Lewis (1998) and McCallum & Nigam (1998). Despite the unrealistic independence assumption, it remains competitive due to its simplicity, speed, and ability to handle high-dimensional sparse features.",
    teaching_notes=TeachingNotes(
        summary="Naive Bayes applies Bayes' theorem with feature independence to classify text.",
        quiz_questions=[
            "Why is the algorithm called 'naive'?",
            "What does Laplace smoothing do and why do we need it?",
            "Calculate P(positive|'great movie') manually with a 2-document training set.",
        ],
        classroom_demo_tips=[
            "Show the probability table as a heatmap",
            "Add a document with completely new words - show smoothing in action",
            "Compare with k-NN or SVM on the same data",
        ],
        common_misconceptions=[
            "Naive Bayes assumes features are uncorrelated (it assumes conditional independence given class, which is different)",
            "Higher P(C|D) always means correct classification (it's just a probability estimate)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# SVM Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

svm_demo = DemoMetadata(
    demo_input={
        "documents": [
            {"id": "d1", "text": "Happy joy love great wonderful", "label": "positive"},
            {"id": "d2", "text": "Sad bad terrible awful horrible", "label": "negative"},
            {"id": "d3", "text": "Amazing fantastic brilliant excellent", "label": "positive"},
            {"id": "d4", "text": "Poor worst disgusting miserable", "label": "negative"},
        ],
        "labels": ["positive", "negative"],
    },
    auto_parameters={
        "kernel": "linear",
        "C": 1.0,
        "max_iter": 1000,
    },
    expected_output_preview={
        "predicted_label": "positive",
        "decision_score": 1.25,
        "support_vectors": 3,
        "margin_width": 0.8,
        "accuracy": 1.0,
    },
    beginner_explanation="SVM finds the best line (or hyperplane) that separates positive and negative documents. It tries to make this line as far as possible from both groups, making it robust to new data.",
    advanced_explanation="Support Vector Machines find the maximum-margin hyperplane that separates classes in feature space. For text, linear SVMs are most common since text vectors are high-dimensional and sparse. The optimization minimizes ||w||² + C×Σξᵢ, where w is the weight vector, C controls regularization, and ξᵢ are slack variables for soft margin. The decision function is f(x) = w·x + b.",
    formula_cards=[
        FormulaCard(
            title="SVM Decision Function",
            formula="f(x) = sign(w·x + b)",
            explanation="The SVM predicts class based on the sign of the decision function, where w is the weight vector and b is the bias.",
            variables={"w": "weight vector (normal to hyperplane)", "x": "input feature vector", "b": "bias term"},
            example="f([tfidf_vector]) = 1.25 → positive class (since > 0)",
        ),
        FormulaCard(
            title="Maximum Margin Objective",
            formula="min ½||w||² + C×Σξᵢ",
            explanation="SVM minimizes weight magnitude (for large margin) plus a penalty for misclassified examples.",
            variables={"C": "regularization parameter (higher = less regularization)", "ξᵢ": "slack variable for sample i"},
            example="C=1.0 balances margin width and classification errors",
        ),
        FormulaCard(
            title="Kernel Trick",
            formula="K(xᵢ, xⱼ) = φ(xᵢ)·φ(xⱼ)",
            explanation="Kernels implicitly map features to higher-dimensional space where classes are separable.",
            variables={"φ": "feature map to higher dimension", "K": "kernel function"},
            example="RBF kernel: K(x,y) = exp(-γ||x-y||²) maps to infinite-dimensional space",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="sv1",
            stage="input_validation",
            title="Validate Training Data",
            description="Ensure labeled documents exist for at least 2 classes.",
            input_preview={"documents": 4, "classes": ["positive", "negative"]},
            output_preview={"valid": True},
            why_it_matters="SVM is a supervised classifier requiring labeled training data.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="sv2",
            stage="preprocessing",
            title="Vectorize Documents",
            description="Convert text to TF-IDF vectors, creating a numerical feature matrix.",
            input_preview={"texts": ["..."]},
            output_preview={"X_shape": [4, 8], "y": ["positive", "negative", "..."]},
            why_it_matters="SVM operates on numerical vectors, not raw text.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="sv3",
            stage="training",
            title="Find Maximum-Margin Hyperplane",
            description="Optimize the SVM objective to find the weight vector w and bias b that maximize the margin.",
            input_preview={"X": ["..."], "y": ["..."]},
            output_preview={"w": [0.5, -0.3, 0.8, "..."], "b": -0.2, "n_support": 3},
            formula="min ½||w||² + C×Σξᵢ",
            why_it_matters="The hyperplane defined by w and b is the actual classifier - it determines all future predictions.",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="sv4",
            stage="prediction",
            title="Predict New Document",
            description="Compute decision value f(x) = w·x + b and predict class based on sign.",
            input_preview={"new_vector": [0.2, 0.1, 0.3, "..."]},
            output_preview={"decision_value": 1.25, "predicted": "positive"},
            formula="f(x) = w·x + b",
            why_it_matters="This is the actual classification step used on new, unseen documents.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="C",
            definition="Regularization parameter - controls trade-off between margin width and classification errors.",
            formula_meaning="Larger C = less regularization = fewer training errors but potentially overfitting",
            example="C=1.0 is default; C=100 means almost no regularization",
            common_mistake="Thinking larger C always improves performance (it can cause overfitting)",
        ),
        HoverAnnotation(
            target="support_vectors",
            definition="Training samples that lie on or within the margin boundary - they define the decision boundary.",
            formula_meaning="Only support vectors affect the decision function f(x) = Σ αᵢyᵢK(xᵢ,x) + b",
            example="3 support vectors means only 3 training samples matter for predictions",
            common_mistake="Thinking all training samples are support vectors (most have αᵢ=0)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Support-Vector Networks",
            authors="Cortes, C. and Vapnik, V.",
            year=1995,
            doi="10.1007/BF00994018",
            relevance="Original SVM paper introducing the soft margin and kernel trick.",
        ),
        ReferenceEntry(
            title="A Tutorial on Support Vector Machines for Pattern Recognition",
            authors="Burges, C.J.C.",
            year=1998,
            doi="10.1023/A:1009715923555",
            relevance="Comprehensive tutorial on SVM theory, kernels, and applications to text classification.",
        ),
        ReferenceEntry(
            title="Text Classification using SVMs: Fast Training, Practical Application",
            authors="Joachims, T.",
            year=1998,
            url="https://www.cs.cornell.edu/people/tj/publications/joachims_98a.pdf",
            relevance="Shows linear SVMs with TF-IDF features are highly effective for text classification.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="SVM draws a line between positive and negative reviews, keeping it as far from both groups as possible.",
            teaching_notes="Visualize with 2D features first. Show how the margin works.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="SVM solves min ½||w||² + C×Σξᵢ to find the maximum-margin hyperplane. Prediction: f(x) = w·x + b.",
            technical_detail="Linear kernel is standard for text (high-dim sparse features). RBF kernel can model non-linear boundaries but is rarely needed for text.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="Linear SVMs are state-of-the-art for high-dimensional sparse text features. Research shows they often match or beat deep learning on small-to-medium text datasets (Wang & Manning, 2012).",
            technical_detail="Limitations: no probability output by default (use Platt scaling), sensitive to feature scaling. For text, scaling is less critical since TF-IDF is already normalized.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="LinearSVC in sklearn is O(n_samples × n_features) per iteration. Use hinge loss with SGD for large datasets. C=1.0 is a reasonable default.",
            technical_detail="Complexity: train O(n×d×iterations), predict O(d). Memory: O(d) for weight vector. API: sklearn.svm.LinearSVC or sklearn.svm.SVC(kernel='linear').",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="SVM introduces the concept of margins and support vectors. Great for teaching optimization in ML.",
            teaching_notes="Quiz: What's the effect of C? Exercise: Plot decision boundary with 2D features. Show support vectors vs. other points.",
        ),
    ],
    research_context="SVMs were introduced by Cortes & Vapnik (1995) and became the dominant ML algorithm in the 1990s-2000s. For text classification, linear SVMs with TF-IDF features consistently rank among the best methods, even in the deep learning era.",
    teaching_notes=TeachingNotes(
        summary="SVM finds the maximum-margin hyperplane to separate text classes in feature space.",
        quiz_questions=[
            "What does the C parameter control in SVM?",
            "Why are linear kernels preferred over RBF for text classification?",
            "What are support vectors and why do they matter?",
        ],
        classroom_demo_tips=[
            "Visualize the margin with 2D features (reduce TF-IDF to 2D with PCA for demo)",
            "Show how C affects the decision boundary",
            "Compare number of support vectors with training set size",
        ],
        common_misconceptions=[
            "SVM always needs a kernel trick (false - linear SVM is most common for text)",
            "More support vectors = better model (false - fewer is often better, indicating wider margin)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# RAKE Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

rake_demo = DemoMetadata(
    demo_input={
        "text": "Support Vector Machines are powerful classifiers for text. SVM algorithms build on statistical learning theory. The SVM classifier finds an optimal hyperplane."
    },
    auto_parameters={
        "min_phrase_length": 1,
        "max_phrase_length": 4,
        "min_word_frequency": 1,
        "use_pos_filtering": False,
    },
    expected_output_preview={
        "keywords": [
            {"phrase": "support vector machines", "score": 8.5},
            {"phrase": "powerful classifiers", "score": 6.2},
            {"phrase": "statistical learning theory", "score": 5.8},
        ],
        "top_keyword": "support vector machines",
    },
    beginner_explanation="RAKE (Rapid Automatic Keyword Extraction) finds important phrases in text by looking for words that appear together often and have high importance scores. It's like automatically underlining the key phrases in an article.",
    advanced_explanation="RAKE extracts keywords by splitting text into candidate phrases using stop words as delimiters, then scoring phrases using word frequency and co-occurrence. The score for a phrase is the sum of (word frequency × word degree) for each word. The degree of a word is its co-occurrence count with other words in the same candidate phrase. RAKE ignores stop words and produces phrases, not just single words.",
    formula_cards=[
        FormulaCard(
            title="Word Score in RAKE",
            formula="score(w) = freq(w) × degree(w)",
            explanation="A word's RAKE score is its frequency multiplied by its co-occurrence degree (number of times it appears with other candidate words).",
            variables={"freq(w)": "frequency of word w", "degree(w)": "co-occurrence count of w with other words"},
            example="If 'support' appears 2 times and co-occurs with 4 words, score = 2 × 4 = 8",
        ),
        FormulaCard(
            title="Phrase Score in RAKE",
            formula="score(phrase) = Σ score(wᵢ) for wᵢ in phrase",
            explanation="The phrase score is the sum of individual word scores in that phrase.",
            variables={"phrase": "candidate phrase", "wᵢ": "i-th word in the phrase"},
            example="'support vector machines' = score('support') + score('vector') + score('machines') = 8 + 5 + 6 = 19",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="rk1",
            stage="input_validation",
            title="Validate Input Text",
            description="Check that input text is non-empty and has sufficient content for keyword extraction.",
            input_preview={"text": "Support Vector Machines are powerful..."},
            output_preview={"valid": True, "word_count": 20},
            why_it_matters="RAKE needs enough text with multiple words to form meaningful candidate phrases.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="rk2",
            stage="preprocessing",
            title="Split into Candidate Phrases",
            description="Use stop words as delimiters to extract candidate keyword phrases.",
            input_preview={"text": "Support Vector Machines are powerful classifiers..."},
            output_preview={"candidates": ["Support Vector Machines", "powerful classifiers", "text", "..."]},
            why_it_matters="Stop words (the, is, are) naturally delimit meaningful phrases in English text.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="rk3",
            stage="computation",
            title="Compute Word Frequency and Degree",
            description="Count how often each word appears and how many times it co-occurs with other words in candidate phrases.",
            input_preview={"candidate_phrases": ["..."]},
            output_preview={"freq": {"support": 2, "vector": 1}, "degree": {"support": 4, "vector": 2}},
            formula="degree(w) = number of co-occurrences with other words in same phrase",
            why_it_matters="Words that appear with many other words (high degree) and frequently (high freq) are likely important keywords.",
            visualization_type="graph",
        ),
        StepExplanation(
            step_id="rk4",
            stage="computation",
            title="Score Phrases and Rank",
            description="Calculate phrase scores by summing word scores, then rank phrases by score.",
            input_preview={"word_scores": {}, "candidate_phrases": ["..."]},
            output_preview={"ranked_keywords": [("support vector machines", 19), ("powerful classifiers", 12), "..."]},
            formula="score(phrase) = Σ freq(w) × degree(w)",
            why_it_matters="Higher-scoring phrases are the most important keywords in the document.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="candidate_phrases",
            definition="Phrases extracted by splitting text on stop words. These are potential keywords.",
            formula_meaning="Text is split on stop words like 'the', 'is', 'are' to get phrases",
            example="'SVM algorithms build on theory' → ['SVM algorithms', 'build', 'theory']",
            common_mistake="Thinking RAKE only extracts single words (it extracts multi-word phrases)",
        ),
        HoverAnnotation(
            target="degree",
            definition="Co-occurrence count of a word with other words in the same candidate phrase.",
            formula_meaning="degree(w) = number of edges in the word co-occurrence graph",
            example="In phrase 'support vector machines', 'support' has degree 2 (co-occurs with 'vector' and 'machines')",
            common_mistake="Confusing degree with frequency (degree measures connections, freq measures occurrences)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Automatic Keyword Extraction from Individual Documents",
            authors="Rose, S., Engel, D., Cramer, N., and Cowley, W.",
            year=2010,
            url="https://www.researchgate.net/publication/227211395_Automatic_Keyword_Extraction_from_Individual_Documents",
            relevance="Original RAKE algorithm paper - describes the word degree and phrase scoring method.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="RAKE finds key phrases by looking at which words appear together and how often. It's like highlighting important phrases in an article.",
            teaching_notes="Use a short paragraph. Show how candidate phrases are extracted after removing 'the', 'is', etc.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="RAKE scores phrases using word frequency × word degree. Formula: score(phrase) = Σ freq(w) × degree(w). Stop words delimit phrases.",
            technical_detail="RAKE doesn't need a corpus - it works on single documents. It's unsupervised and language-agnostic (just needs stop word list).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="RAKE is simple but effective for single-document keyword extraction. Research shows it performs competitively with more complex methods like TextRank for short texts (Mihalcea & Tarau, 2004).",
            technical_detail="Limitations: no global statistics (unlike TF-IDF), sensitive to stop word list quality. Variants: RAKE with POS filtering, TopicRank, YAKE.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="RAKE is O(n) where n is word count. It's extremely fast and doesn't need training. Use nltk's stop word lists or customize for your domain.",
            technical_detail="Complexity: O(n). Memory: O(v) where v is vocabulary size. Easy to implement: split on stops → count freq/degree → score phrases.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="RAKE introduces keyword extraction without needing a corpus. Great for teaching unsupervised NLP.",
            teaching_notes="Quiz: Why use stop words as delimiters? Exercise: Manually compute RAKE scores for a 2-sentence text. Discuss: When would RAKE fail?",
        ),
    ],
    research_context="RAKE was introduced by Rose et al. (2010) as a simple, unsupervised keyword extraction method that works on individual documents without requiring a corpus. It's widely used in document summarization and content analysis.",
    teaching_notes=TeachingNotes(
        summary="RAKE extracts keywords by scoring phrases based on word frequency and co-occurrence degree.",
        quiz_questions=[
            "How does RAKE identify candidate phrases?",
            "What do 'frequency' and 'degree' mean in RAKE, and how are they combined?",
            "Why doesn't RAKE need a corpus of documents?",
        ],
        classroom_demo_tips=[
            "Show the word co-occurrence graph visually",
            "Compare RAKE keywords with TF-IDF top terms",
            "Try RAKE on different document types (news, academic, social media)",
        ],
        common_misconceptions=[
            "RAKE only works on English (false - it works on any language with stop words)",
            "RAKE needs training data (false - it's fully unsupervised)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# TextRank Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

textrank_demo = DemoMetadata(
    demo_input={
        "text": "Google was founded by Larry Page and Sergey Brin. The company is known for search algorithms. PageRank is the algorithm that started it all. Brin and Page developed PageRank at Stanford University."
    },
    auto_parameters={
        "max_iterations": 100,
        "damping_factor": 0.85,
        "min_word_length": 3,
        "top_n": 5,
    },
    expected_output_preview={
        "keywords": [
            {"word": "pagerank", "score": 0.95},
            {"word": "google", "score": 0.82},
            {"word": "brin", "score": 0.78},
            {"word": "page", "score": 0.75},
            {"word": "algorithm", "score": 0.68},
        ],
        "top_keyword": "pagerank",
    },
    beginner_explanation="TextRank is like a popularity contest for words. Words that appear near other important words become important themselves. It's based on Google's PageRank algorithm - the same one used to rank web pages.",
    advanced_explanation="TextRank applies the PageRank algorithm to a graph of words (or sentences). Words are nodes, and edges are created based on co-occurrence within a sliding window. The PageRank algorithm iteratively updates node scores: PR(v) = (1-d) + d × Σ PR(u)/out_degree(u) for all u linking to v. After convergence, top-scoring words are extracted as keywords. TextRank can also extract sentences for summarization.",
    formula_cards=[
        FormulaCard(
            title="PageRank Formula",
            formula="PR(v) = (1-d) + d × Σ_{u∈In(v)} PR(u) / |Out(u)|",
            explanation="The PageRank score of node v is a weighted sum of scores from nodes pointing to v, with damping factor d (typically 0.85).",
            variables={"d": "damping factor (probability of following links)", "In(v)": "nodes linking to v", "Out(u)": "nodes u links to"},
            example="If node A (PR=0.5) links to v, and A has 2 out-links: contribution = 0.85 × 0.5/2 = 0.2125",
        ),
        FormulaCard(
            title="Word Co-occurrence Graph",
            formula="edge(wᵢ, wⱼ) if co-occurrence(window, wᵢ, wⱼ) > 0",
            explanation="Words are connected if they appear within a sliding window (typically 2-5 words) of each other in the text.",
            variables={"window": "sliding window size (e.g., 2, 3, 5 words)", "co-occurrence": "number of times two words appear together in window"},
            example="Window=2: 'cat sat on' → edges: cat-sat, sat-on",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="tr1",
            stage="input_validation",
            title="Validate Input Text",
            description="Check text is non-empty and has enough content for graph construction.",
            input_preview={"text": "Google was founded by Larry Page..."},
            output_preview={"valid": True, "word_count": 28},
            why_it_matters="TextRank needs sufficient text to build a meaningful word co-occurrence graph.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="tr2",
            stage="preprocessing",
            title="Tokenize and Filter Words",
            description="Tokenize text, filter by length and stop words, then build vocabulary.",
            input_preview={"text": "Google was founded by Larry Page..."},
            output_preview={"filtered_words": ["google", "founded", "larry", "page", "..."]},
            why_it_matters="Filtering removes noise (stop words, short words) that would dilute the graph.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="tr3",
            stage="graph_construction",
            title="Build Word Co-occurrence Graph",
            description="Create a graph where nodes are words and edges connect words that co-occur within a sliding window.",
            input_preview={"words": ["..."], "window_size": 3},
            output_preview={"nodes": 12, "edges": 18, "graph_density": 0.27},
            why_it_matters="The graph captures which words appear together, encoding semantic relationships through co-occurrence.",
            visualization_type="graph",
        ),
        StepExplanation(
            step_id="tr4",
            stage="computation",
            title="Run PageRank Algorithm",
            description="Iteratively compute PageRank scores for each node until convergence or max iterations.",
            input_preview={"graph": {}, "damping": 0.85, "max_iter": 100},
            output_preview={"iterations": 23, "converged": True, "scores": {"pagerank": 0.95}},
            formula="PR(v) = (1-d) + d × Σ PR(u)/|Out(u)|",
            why_it_matters="PageRank identifies words that are central in the co-occurrence network - these are the key concepts in the text.",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="tr5",
            stage="output",
            title="Extract Top Keywords",
            description="Sort words by PageRank score and return the top N as keywords.",
            input_preview={"scores": {}, "top_n": 5},
            output_preview={"keywords": ["pagerank", "google", "brin", "page", "algorithm"]},
            why_it_matters="The top-scoring words represent the most important concepts in the document.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="PageRank",
            definition="Algorithm that ranks nodes in a graph based on the importance of their connections.",
            formula_meaning="PR(v) = (1-d) + d × Σ PR(u)/out_degree(u) - nodes with more/higher-quality links get higher scores",
            example="Google uses PageRank to rank web pages based on which pages link to them",
            common_mistake="Thinking PageRank counts only the number of links (it weights links by the source's own importance)",
        ),
        HoverAnnotation(
            target="damping_factor",
            definition="Probability (1-d) that a random surfer stops following links and jumps to a random page.",
            formula_meaning="d=0.85 means 85% chance of following links, 15% chance of random jump",
            example="d=0.85 is standard; lower d means more random jumps (faster mixing but less stable rankings)",
            common_mistake="Setting d too high (close to 1) can cause slow convergence; too low loses graph structure",
        ),
    ],
    references=[
        ReferenceEntry(
            title="TextRank: Bringing Order into Texts",
            authors="Mihalcea, R. and Tarau, P.",
            year=2004,
            url="https://aclanthology.org/W04-3252/",
            relevance="Original TextRank paper - applies PageRank to text for keyword extraction and summarization.",
        ),
        ReferenceEntry(
            title="The PageRank Citation Ranking: Bringing Order to the Web",
            authors="Page, L., Brin, S., Motwani, R., and Winograd, T.",
            year=1999,
            url="https://ilpubs.stanford.edu:8090/422/",
            relevance="Original PageRank paper from Stanford - the foundation for TextRank's graph algorithm.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="TextRank builds a network of words and finds the most 'popular' ones - like finding the most well-connected people at a party.",
            teaching_notes="Use a text about a well-known topic. Show the word graph with nodes and edges.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="TextRank builds a word co-occurrence graph and runs PageRank. Formula: PR(v) = (1-d) + d × Σ PR(u)/|Out(u)|. Top nodes = keywords.",
            technical_detail="Window size controls edge creation (2-5 words typical). Undirected graph is common. Convergence typically in 20-50 iterations.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="TextRank is unsupervised and domain-independent. Research shows it matches or beats RAKE for long texts but may underperform for very short texts (Wan & Xiao, 2008).",
            technical_detail="Limitations: no global statistics, sensitive to window size and preprocessing. Extensions: PositionRank (incorporates word positions), SingleRank (weighted co-occurrence), TopicRank (topic-based clustering).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="TextRank is O(V²) for graph construction (V = vocabulary size) and O(E) per PageRank iteration (E = edges). Use NetworkX for graph operations.",
            technical_detail="Complexity: build O(V²) or O(n×w) where n=words, w=window; PageRank O(E×iter). Memory: O(V²) for adjacency matrix or O(E) for sparse. API: networkx.pagerank.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="TextRank introduces graph-based NLP. Students learn how web search algorithms apply to text analysis.",
            teaching_notes="Quiz: Why does PageRank work for keywords? Exercise: Draw the word graph for a 2-sentence text. Compare TextRank vs. RAKE results.",
        ),
    ],
    research_context="TextRank (Mihalcea & Tarau, 2004) adapts Google's PageRank algorithm for NLP. It's a graph-based unsupervised method that can extract both keywords and summary sentences. It's particularly effective for longer texts where co-occurrence patterns are meaningful.",
    teaching_notes=TeachingNotes(
        summary="TextRank applies PageRank to a word co-occurrence graph to extract important keywords from text.",
        quiz_questions=[
            "How does TextRank build the word graph?",
            "What does the damping factor control in PageRank?",
            "Compare TextRank and RAKE: when would you use each?",
        ],
        classroom_demo_tips=[
            "Visualize the word graph with node sizes proportional to PageRank scores",
            "Show convergence of PageRank scores over iterations",
            "Compare keyword extraction with and without stop word removal",
        ],
        common_misconceptions=[
            "TextRank only works for keyword extraction (false - it also does sentence extraction for summarization)",
            "More iterations always means better results (false - PageRank typically converges in 20-50 iterations)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# Export all demo metadata as a dictionary
# ──────────────────────────────────────────────────────────────────────────────

CLASSICAL_DEMO_METADATA = {
    "tokenization": tokenization_demo,
    "tfidf": tfidf_demo,
    "naive_bayes": naive_bayes_demo,
    "svm": svm_demo,
    "rake": rake_demo,
    "textrank": textrank_demo,
}
