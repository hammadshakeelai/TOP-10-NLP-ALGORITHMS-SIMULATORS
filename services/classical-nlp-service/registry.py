"""
Algorithm registry for the classical NLP service.
Maps algorithm_id → simulator instance + catalog metadata.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../packages"))
from shared_schemas import (
    AlgorithmEntry, AlgorithmID, SimulatorMode, ParameterSchema
)
from simulators import (
    TokenizationSimulator, TFIDFSimulator,
    NaiveBayesSimulator, SVMSimulator,
    RAKESimulator, TextRankSimulator,
)
from simulators.base import BaseSimulator

SIMULATORS: dict[str, BaseSimulator] = {
    AlgorithmID.TOKENIZATION:  TokenizationSimulator(),
    AlgorithmID.TFIDF:         TFIDFSimulator(),
    AlgorithmID.NAIVE_BAYES:   NaiveBayesSimulator(),
    AlgorithmID.SVM:           SVMSimulator(),
    AlgorithmID.RAKE:          RAKESimulator(),
    AlgorithmID.TEXTRANK:      TextRankSimulator(),
}

CATALOG: list[AlgorithmEntry] = [
    AlgorithmEntry(
        id=AlgorithmID.TOKENIZATION,
        name="Tokenization",
        family="preprocessing",
        description="Segment raw text into tokens with character offsets, normalization, and subword splitting.",
        use_cases=["preprocessing pipeline", "vocabulary analysis", "subword understanding"],
        input_types=["text"],
        complexity="O(n)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="tokenizer_type", type="string", default="whitespace",
                            options=["whitespace", "regex", "bpe_demo", "wordpiece"],
                            description="Tokenization strategy."),
            ParameterSchema(name="lowercase", type="bool", default=True, description="Lowercase all tokens."),
            ParameterSchema(name="remove_stopwords", type="bool", default=False, description="Filter common stopwords."),
            ParameterSchema(name="stemming", type="bool", default=False, description="Apply rule-based stemming."),
            ParameterSchema(name="remove_punctuation", type="bool", default=False, description="Drop punctuation tokens."),
            ParameterSchema(name="regex_pattern", type="string", default=r"\b\w+\b",
                            description="Regex pattern for regex tokenizer mode."),
            ParameterSchema(name="bpe_num_merges", type="int", default=10, min=1, max=50,
                            description="Number of BPE merge operations to demonstrate."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.TFIDF,
        name="TF-IDF",
        family="vectorization",
        description="Term Frequency-Inverse Document Frequency weighting with cosine similarity and query ranking.",
        use_cases=["document ranking", "keyword extraction", "text similarity"],
        input_types=["documents", "text"],
        complexity="O(N × V)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="ngram_range", type="array", default=[1, 1],
                            description="(min_n, max_n) for n-gram extraction."),
            ParameterSchema(name="smooth_idf", type="bool", default=True,
                            description="Apply scikit-learn-style IDF smoothing."),
            ParameterSchema(name="normalize", type="bool", default=True,
                            description="L2-normalize TF-IDF vectors."),
            ParameterSchema(name="tf_scheme", type="string", default="raw",
                            options=["raw", "freq", "log", "bool"],
                            description="Term frequency counting scheme."),
            ParameterSchema(name="top_n", type="int", default=10, min=1, max=100,
                            description="Top-N terms to show per document."),
            ParameterSchema(name="query", type="string", default=None,
                            description="Optional query text for document similarity ranking."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.NAIVE_BAYES,
        name="Naïve Bayes",
        family="classification",
        description="Multinomial Naïve Bayes text classifier with class priors, feature likelihoods, and Laplace smoothing.",
        use_cases=["spam detection", "sentiment analysis", "topic classification"],
        input_types=["documents"],
        complexity="O(N × V)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="smoothing_alpha", type="float", default=1.0, min=0.001, max=10.0,
                            description="Laplace smoothing parameter α. Higher = more smoothing."),
            ParameterSchema(name="ngram_range", type="array", default=[1, 1],
                            description="N-gram range for feature extraction."),
            ParameterSchema(name="test_size", type="float", default=0.2, min=0.1, max=0.5,
                            description="Fraction of data to hold out for evaluation."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.SVM,
        name="SVM",
        family="classification",
        description="Linear SVM text classifier with TF-IDF features, decision margins, and top-feature ranking.",
        use_cases=["text classification", "sentiment analysis", "intent detection"],
        input_types=["documents"],
        complexity="O(N × V)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="C", type="float", default=1.0, min=0.001, max=100.0,
                            description="Regularization parameter. Smaller = wider margin."),
            ParameterSchema(name="ngram_range", type="array", default=[1, 1],
                            description="N-gram range for TF-IDF features."),
            ParameterSchema(name="class_weight", type="string", default=None,
                            options=[None, "balanced"],
                            description="Adjust class weights for imbalanced datasets."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.RAKE,
        name="RAKE",
        family="extraction",
        description="Rapid Automatic Keyword Extraction — stopword-delimited phrase scoring via word co-occurrence.",
        use_cases=["keyword extraction", "tag generation", "document indexing"],
        input_types=["text"],
        complexity="O(n²)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="top_n", type="int", default=10, min=1, max=50,
                            description="Number of top-ranked keywords to return."),
            ParameterSchema(name="min_phrase_words", type="int", default=1, min=1, max=5,
                            description="Minimum words in a candidate phrase."),
            ParameterSchema(name="max_phrase_words", type="int", default=5, min=1, max=10,
                            description="Maximum words in a candidate phrase."),
            ParameterSchema(name="min_score", type="float", default=0.0, min=0.0,
                            description="Minimum RAKE score threshold."),
            ParameterSchema(name="stopwords", type="array", default=[],
                            description="Additional stopwords to add to the default list."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.TEXTRANK,
        name="TextRank",
        family="extraction",
        description="Graph-based ranking for keyword extraction and extractive summarization (Mihalcea & Tarau, 2004).",
        use_cases=["keyword extraction", "extractive summarization", "sentence ranking"],
        input_types=["text"],
        complexity="O(V² × iterations)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="mode", type="string", default="keyword",
                            options=["keyword", "summary"],
                            description="'keyword' for word-level ranking; 'summary' for sentence-level."),
            ParameterSchema(name="damping", type="float", default=0.85, min=0.1, max=0.99,
                            description="PageRank damping factor."),
            ParameterSchema(name="top_n", type="int", default=5, min=1, max=20,
                            description="Number of top-ranked keywords or sentences."),
            ParameterSchema(name="window_size", type="int", default=2, min=1, max=10,
                            description="Word co-occurrence window (keyword mode only)."),
            ParameterSchema(name="convergence_tol", type="float", default=0.0001,
                            description="PageRank convergence tolerance."),
        ],
    ),
]

def get_simulator(algorithm_id: str) -> BaseSimulator:
    sim = SIMULATORS.get(algorithm_id)
    if sim is None:
        raise ValueError(f"No simulator registered for algorithm_id='{algorithm_id}'.")
    return sim


def get_catalog() -> list[AlgorithmEntry]:
    return CATALOG
