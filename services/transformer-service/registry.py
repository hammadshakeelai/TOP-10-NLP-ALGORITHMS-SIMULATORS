"""
Algorithm registry for the transformer NLP service.
Maps algorithm_id to simulator instances and catalog metadata.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../packages"))

from shared_schemas import AlgorithmEntry, AlgorithmID, ParameterSchema, SimulatorMode
from simulators import (
    BERTSimulator,
    FastTextSimulator,
    GPTSimulator,
    LSTMSimulator,
    T5Simulator,
    TransformerAttentionSimulator,
    WordEmbeddingsSimulator,
)
from simulators.base import BaseSimulator

SIMULATORS: dict[str, BaseSimulator] = {
    AlgorithmID.WORD_EMBEDDINGS: WordEmbeddingsSimulator(),
    AlgorithmID.LSTM: LSTMSimulator(),
    AlgorithmID.TRANSFORMER_ATTN: TransformerAttentionSimulator(),
    AlgorithmID.BERT: BERTSimulator(),
    AlgorithmID.GPT: GPTSimulator(),
    AlgorithmID.T5: T5Simulator(),
    AlgorithmID.FASTTEXT: FastTextSimulator(),
}

CATALOG: list[AlgorithmEntry] = [
    AlgorithmEntry(
        id=AlgorithmID.WORD_EMBEDDINGS,
        name="Word Embeddings",
        family="vectorization",
        description="Toy SVD and optional pretrained Word2Vec/GloVe embeddings with similarity, analogy, and 2D projection views.",
        use_cases=["semantic similarity", "nearest neighbors", "analogy exploration"],
        input_types=["text", "documents"],
        complexity="O(V^3) toy SVD",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="model_type", type="string", default="toy_svd", options=["toy_svd", "word2vec", "glove"], description="Embedding backend."),
            ParameterSchema(name="target_word", type="string", default="", description="Word to inspect."),
            ParameterSchema(name="context_window", type="int", default=2, min=1, max=10, description="Co-occurrence context window for toy mode."),
            ParameterSchema(name="vector_dim", type="int", default=50, min=2, max=300, description="Embedding dimensionality."),
            ParameterSchema(name="min_count", type="int", default=2, min=1, max=20, description="Minimum token frequency in toy vocabulary."),
            ParameterSchema(name="top_k_neighbors", type="int", default=10, min=1, max=50, description="Nearest neighbors to return."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.LSTM,
        name="LSTM",
        family="sequence",
        description="Traceable toy LSTM showing token steps, hidden/cell state, and gate activations.",
        use_cases=["sequence modeling education", "gate visualization", "padding and truncation demos"],
        input_types=["text"],
        complexity="O(T * H^2)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="max_seq_len", type="int", default=50, min=1, max=200, description="Maximum sequence length."),
            ParameterSchema(name="hidden_size", type="int", default=8, min=2, max=64, description="Hidden state size."),
            ParameterSchema(name="input_size", type="int", default=16, min=2, max=128, description="Toy embedding size."),
            ParameterSchema(name="random_seed", type="int", default=42, description="Seed for reproducible toy weights."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.TRANSFORMER_ATTN,
        name="Transformer Attention",
        family="transformer",
        description="From-scratch multi-head self-attention with Q/K/V matrices, positional encodings, and optional causal masks.",
        use_cases=["attention heatmaps", "masking demonstrations", "positional encoding demos"],
        input_types=["text"],
        complexity="O(H * T^2 * d)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="d_model", type="int", default=32, min=8, max=256, description="Model dimension."),
            ParameterSchema(name="num_heads", type="int", default=4, min=1, max=16, description="Number of attention heads."),
            ParameterSchema(name="causal_mask", type="bool", default=False, description="Apply left-to-right causal masking."),
            ParameterSchema(name="positional_encoding", type="bool", default=True, description="Add sinusoidal positional encodings."),
            ParameterSchema(name="seed", type="int", default=42, description="Seed for reproducible projection weights."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.BERT,
        name="BERT",
        family="transformer",
        description="HuggingFace-backed BERT-style simulator for masked language modeling and understanding tasks.",
        use_cases=["masked token prediction", "sentiment", "NER", "question answering"],
        input_types=["text"],
        complexity="Model-dependent",
        requires_gpu=False,
        is_async=True,
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="task", type="string", default="mlm", options=["mlm", "sentiment", "ner", "qa"], description="Pipeline task."),
            ParameterSchema(name="checkpoint", type="string", default="", description="Optional HuggingFace checkpoint override."),
            ParameterSchema(name="top_k", type="int", default=5, min=1, max=20, description="Top predictions to show."),
            ParameterSchema(name="question", type="string", default="", description="Question for QA task."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.GPT,
        name="GPT-Style Generation",
        family="transformer",
        description="Autoregressive text generation simulator with decoding parameters, stop sequences, and warnings for expensive runs.",
        use_cases=["prompting", "sampling controls", "generation traces"],
        input_types=["text"],
        complexity="Model-dependent",
        requires_gpu=False,
        is_async=True,
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="checkpoint", type="string", default="distilgpt2", description="HuggingFace generation checkpoint."),
            ParameterSchema(name="max_new_tokens", type="int", default=100, min=1, max=512, description="Maximum generated tokens."),
            ParameterSchema(name="temperature", type="float", default=0.8, min=0.0, max=2.0, description="Sampling temperature."),
            ParameterSchema(name="top_k", type="int", default=50, min=0, max=200, description="Top-k sampling cutoff."),
            ParameterSchema(name="top_p", type="float", default=0.95, min=0.0, max=1.0, description="Nucleus sampling cutoff."),
            ParameterSchema(name="stop_sequences", type="array", default=[], description="Sequences that stop generation."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.T5,
        name="T5 / Sequence-to-Sequence",
        family="transformer",
        description="Text-to-text sequence simulator for summarization, translation-style prompts, QA, and beam candidates.",
        use_cases=["summarization", "translation", "text-to-text task framing"],
        input_types=["text"],
        complexity="Model-dependent",
        requires_gpu=False,
        is_async=True,
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="task_prefix", type="string", default="summarize:", description="Text-to-text task prefix."),
            ParameterSchema(name="checkpoint", type="string", default="t5-small", description="HuggingFace checkpoint."),
            ParameterSchema(name="num_beams", type="int", default=4, min=1, max=8, description="Beam width."),
            ParameterSchema(name="max_new_tokens", type="int", default=80, min=1, max=256, description="Maximum decoded tokens."),
            ParameterSchema(name="length_penalty", type="float", default=1.0, min=0.1, max=4.0, description="Beam-search length penalty."),
        ],
    ),
    AlgorithmEntry(
        id=AlgorithmID.FASTTEXT,
        name="FastText",
        family="classification",
        description="Subword-aware text classification simulator with character n-gram breakdown and supervised classification.",
        use_cases=["fast text classification", "misspelling robustness", "subword visualization"],
        input_types=["documents", "text"],
        complexity="O(N * ngrams)",
        supported_modes=[SimulatorMode.LEARNING, SimulatorMode.EXPERIMENT],
        parameter_schema=[
            ParameterSchema(name="min_n", type="int", default=3, min=1, max=6, description="Minimum character n-gram length."),
            ParameterSchema(name="max_n", type="int", default=6, min=1, max=10, description="Maximum character n-gram length."),
            ParameterSchema(name="epochs", type="int", default=5, min=1, max=50, description="Training epochs when supervised mode is available."),
            ParameterSchema(name="lr", type="float", default=0.1, min=0.001, max=1.0, description="Learning rate."),
            ParameterSchema(name="word_ngrams", type="int", default=1, min=1, max=5, description="Word n-gram feature length."),
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
