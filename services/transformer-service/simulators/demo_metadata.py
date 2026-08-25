"""
Demo initialization metadata for all transformer/neural NLP simulators.
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
# Word Embeddings Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

word_embeddings_demo = DemoMetadata(
    demo_input={
        "text": "king queen man woman royal palace throne",
        "mode": "similarity",
    },
    auto_parameters={
        "model_type": "toy_svd",
        "vector_dim": 5,
        "context_window": 2,
        "min_count": 1,
        "target_word": "king",
        "top_k_neighbors": 5,
        "analogy": {"a": "king", "b": "man", "c": "woman"},
    },
    expected_output_preview={
        "vocabulary_size": 6,
        "embedding_dim": 100,
        "similarity_pairs": [("king", "queen", 0.85), ("man", "woman", 0.82)],
        "analogy_top": [("king", "man", "woman")],
    },
    beginner_explanation="Word embeddings turn words into lists of numbers (vectors) so that similar words have similar number lists. 'King' and 'queen' will have close vectors, just like 'man' and 'woman'.",
    advanced_explanation="Word2Vec (Mikolov et al., 2013) learns dense vector representations where semantic relationships are encoded as geometric relationships in vector space. Skip-gram predicts context words given a center word: maximize Σ log P(w_context|w_center). Negative sampling approximates softmax: P(w|w_c) ≈ σ(v_w·v_wc) for positive pairs and 1-σ(·) for negative samples. Analogies emerge: king - man + woman ≈ queen.",
    formula_cards=[
        FormulaCard(
            title="Skip-gram Objective",
            formula="J(θ) = Σ log P(w_O|w_I)",
            explanation="Skip-gram maximizes the probability of context words w_O given input word w_I.",
            variables={"w_I": "input (center) word", "w_O": "output (context) word", "θ": "model parameters"},
            example="For 'king' with context ['queen', 'man', 'royal'], maximize P(queen|king) + P(man|king) + P(royal|king)",
        ),
        FormulaCard(
            title="Negative Sampling",
            formula="log σ(v_c·v_w) + Σ log σ(-v_c·v_n)",
            explanation="Instead of full softmax, use binary classification: positive for real context words, negative for sampled noise words.",
            variables={"v_c": "context word vector", "v_w": "center word vector", "v_n": "negative sample vector"},
            example="Positive: σ(v_queen·v_king) ≈ 0.85. Negative: σ(-v_car·v_king) ≈ 0.1",
        ),
        FormulaCard(
            title="Word Analogy",
            formula="v_queen ≈ v_king - v_man + v_woman",
            explanation="Semantic relationships appear as vector offsets. Analogy: king is to man as queen is to woman.",
            variables={"v_w": "vector representation of word w"},
            example="vector('king') - vector('man') + vector('woman') ≈ vector('queen')",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="we1",
            stage="input_validation",
            title="Validate Vocabulary",
            description="Check that input text has sufficient words to build meaningful embeddings.",
            input_preview={"words": 6, "text": "king queen man woman..."},
            output_preview={"valid": True, "vocab_size": 6},
            why_it_matters="Need enough words to learn meaningful relationships. Real training uses millions of words.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="we2",
            stage="preprocessing",
            title="Build Vocabulary and Word Frequencies",
            description="Count word frequencies and assign indices to each unique word.",
            input_preview={"words": ["king", "queen", "man", "..."]},
            output_preview={"vocab": {"king": 0, "queen": 1}, "freqs": {"king": 1, "queen": 1}},
            why_it_matters="Vocabulary mapping is needed to look up embedding vectors during training and inference.",
            visualization_type="bar",
        ),
        StepExplanation(
            step_id="we3",
            stage="training",
            title="Generate Training Pairs (Skip-gram)",
            description="For each word, create (center, context) pairs within the sliding window.",
            input_preview={"vocab": ["..."], "window": 5},
            output_preview={"pairs": [("king","queen"), ("king","man"), "..."], "pair_count": 12},
            why_it_matters="These pairs are the training data - the model learns to predict context words from center words.",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="we4",
            stage="training",
            title="Train Embeddings with Negative Sampling",
            description="Learn word vectors by maximizing similarity for positive pairs and minimizing it for negative samples.",
            input_preview={"training_pairs": ["..."], "negative_samples": 5},
            output_preview={"embedding_shape": [6, 100], "loss": 0.35},
            formula="log σ(v_c·v_w) + Σ log σ(-v_c·v_n)",
            why_it_matters="This is the core learning step - the model discovers semantic relationships encoded in vector geometry.",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="we5",
            stage="output",
            title="Compute Word Similarities & Analogies",
            description="Measure cosine similarity between word vectors and solve analogy tasks like king - man + woman ≈ queen.",
            input_preview={"embeddings": ["..."], "query": "king - man + woman"},
            output_preview={"similarities": [("queen", 0.85), ("royal", 0.72), "..."], "analogy": "queen"},
            formula="sim(w₁, w₂) = (v₁·v₂) / (||v₁|| × ||v₂||)",
            why_it_matters="High similarity between related words confirms the embeddings captured semantic meaning.",
            visualization_type="heatmap",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="embedding_vector",
            definition="A list of numbers (typically 50-300 dimensions) representing a word's meaning in vector space.",
            formula_meaning="v_w ∈ ℝ^d where d is embedding dimension (typically 100-300)",
            example="v_king might be [0.2, -0.5, 0.8, ...] in 100-dimensional space",
            common_mistake="Thinking each dimension has a human-interpretable meaning (they're distributed representations)",
        ),
        HoverAnnotation(
            target="cosine_similarity",
            definition="Measures how similar two vectors are, ignoring magnitude. Range: -1 (opposite) to 1 (identical).",
            formula_meaning="cos(θ) = (v₁·v₂) / (||v₁|| × ||v₂||) = dot product divided by product of magnitudes",
            example="cosine_sim('king', 'queen') ≈ 0.85 means they're very similar",
            common_mistake="Using Euclidean distance instead - cosine is better for high-dimensional sparse vectors",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Efficient Estimation of Word Representations in Vector Space",
            authors="Mikolov, T., Sutskever, I., Chen, K., Corrado, G., and Dean, J.",
            year=2013,
            arxiv_id="1301.3781",
            relevance="Original Word2Vec paper introducing Skip-gram and CBOW models with negative sampling.",
        ),
        ReferenceEntry(
            title="Distributed Representations of Words and Phrases and their Compositionality",
            authors="Mikolov, T., et al.",
            year=2013,
            arxiv_id="1310.4546",
            relevance="Extends Word2Vec with negative sampling, subsampling, and demonstrates word analogies.",
        ),
        ReferenceEntry(
            title="GloVe: Global Vectors for Word Representation",
            authors="Pennington, J., Socher, R., and Manning, C.D.",
            year=2014,
            arxiv_id="1405.4053",
            relevance="Alternative to Word2Vec that uses global word co-occurrence statistics instead of local context windows.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="Word embeddings turn words into number lists so that similar words have similar lists. Like giving each word a unique 'fingerprint'.",
            teaching_notes="Show 2D visualization of word vectors. Use colors to show related words clustering together.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="Word2Vec learns embeddings by predicting context words (Skip-gram) or center words (CBOW). Objective: maximize log P(w_context|w_center).",
            technical_detail="Skip-gram: predict context from center word. Negative sampling: train binary classifier to distinguish real from noise pairs. 100-300 dimensions typical.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="Word2Vec showed that semantic relationships are linear in embedding space (king - man + woman ≈ queen). Limitations: no polysemy handling, static embeddings. Research led to contextualized embeddings (BERT, ELMo).",
            technical_detail="Limitations: same word → same vector regardless of context (polysemy). Alternatives: GloVe (global stats), fastText (subword info), ELMo (contextual), BERT (deep contextual).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="Word2Vec training is O(corpus_size × window × dim). Use gensim or PyTorch. For inference, it's O(1) to look up a word vector. Typically 100-300 dimensions.",
            technical_detail="Complexity: train O(N×w×d), inference O(1). Memory: O(V×d) for embeddings. API: gensim.models.Word2Vec, or pre-trained: spaCy, torchtext.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="Word embeddings are the foundation of modern NLP. Show how analogies work geometrically in vector space.",
            teaching_notes="Quiz: Why does king - man + woman ≈ queen? Exercise: Visualize 3D embeddings with PCA/t-SNE. Discuss: Why are embeddings useful for downstream tasks?",
        ),
    ],
    research_context="Word2Vec (Mikolov et al., 2013) revolutionized NLP by showing that semantic meaning can be captured in dense vector representations learned from unlabeled text. It enabled transfer learning in NLP, paving the way for contextual embeddings (BERT, GPT).",
    teaching_notes=TeachingNotes(
        summary="Word embeddings map words to dense vectors where semantic similarity corresponds to vector similarity.",
        quiz_questions=[
            "What does the Skip-gram objective maximize?",
            "Why does cosine similarity work better than Euclidean distance for word embeddings?",
            "Solve: king - man + woman = ? Explain why this works.",
        ],
        classroom_demo_tips=[
            "Visualize embeddings in 2D/3D with PCA or t-SNE",
            "Show word analogy completion interactively",
            "Compare Word2Vec vs. GloVe vs. fastText embeddings",
        ],
        common_misconceptions=[
            "Each dimension has a clear meaning (false - they're distributed representations)",
            "Word2Vec understands language (false - it captures statistical patterns, not meaning)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# LSTM Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

lstm_demo = DemoMetadata(
    demo_input={
        "text": "I love this movie because the acting was amazing and the plot kept me engaged.",
        "task": "sentiment",
    },
    auto_parameters={
        "hidden_size": 128,
        "num_layers": 1,
        "dropout": 0.2,
        "bidirectional": False,
    },
    expected_output_preview={
        "predicted_sentiment": "positive",
        "confidence": 0.92,
        "sequence_length": 15,
        "hidden_states_shape": [15, 128],
    },
    beginner_explanation="LSTM is a type of neural network that reads text one word at a time and remembers important information while forgetting irrelevant details. It's like reading a story and remembering the main plot points while forgetting small details.",
    advanced_explanation="LSTM (Long Short-Term Memory) networks use gating mechanisms to control information flow and maintain long-term dependencies. The core LSTM cell has three gates: forget gate f_t = σ(W_f·[h_{t-1}, x_t] + b_f), input gate i_t = σ(W_i·[h_{t-1}, x_t] + b_i), and output gate o_t = σ(W_o·[h_{t-1}, x_t] + b_o). The cell state c_t = f_t ⊙ c_{t-1} + i_t ⊙ tanh(W_c·[h_{t-1}, x_t] + b_c), and hidden state h_t = o_t ⊙ tanh(c_t). LSTMs solve the vanishing gradient problem of standard RNNs.",
    formula_cards=[
        FormulaCard(
            title="Forget Gate",
            formula="f_t = σ(W_f·[h_{t-1}, x_t] + b_f)",
            explanation="Decides what information to discard from the cell state. σ is sigmoid (0=forget, 1=keep all).",
            variables={"f_t": "forget gate output", "h_{t-1}": "previous hidden state", "x_t": "current input"},
            example="f_t = [0.9, 0.1, 0.8, ...] means forget 10% of info in dimension 2",
        ),
        FormulaCard(
            title="Input Gate & Cell Update",
            formula="i_t = σ(W_i·[h_{t-1}, x_t] + b_i); c̃_t = tanh(W_c·[h_{t-1}, x_t] + b_c); c_t = f_t⊙c_{t-1} + i_t⊙c̃_t",
            explanation="Decides what new information to store in the cell state. i_t controls how much new info to add; c̃_t is the candidate value.",
            variables={"i_t": "input gate", "c̃_t": "candidate cell state", "c_t": "new cell state", "⊙": "Hadamard (element-wise) product"},
            example="If i_t=0.8 and c̃_t=0.5, add 0.4 to cell state in that dimension",
        ),
        FormulaCard(
            title="Output Gate & Hidden State",
            formula="o_t = σ(W_o·[h_{t-1}, x_t] + b_o); h_t = o_t ⊙ tanh(c_t)",
            explanation="Decides what parts of the cell state to output as the hidden state, which is passed to the next timestep and used for predictions.",
            variables={"o_t": "output gate", "h_t": "hidden state (output)"},
            example="o_t=0.7 means output 70% of the transformed cell state",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="ls1",
            stage="input_validation",
            title="Validate Input Sequence",
            description="Check that input text is non-empty and can be tokenized into a sequence.",
            input_preview={"text": "I love this movie because..."},
            output_preview={"valid": True, "sequence_length": 15},
            why_it_matters="LSTM processes sequences - needs valid text to convert to token/embedding sequence.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="ls2",
            stage="preprocessing",
            title="Embed Input Tokens",
            description="Convert tokens to dense embedding vectors that the LSTM can process.",
            input_preview={"tokens": ["i", "love", "this", "..."]},
            output_preview={"embeddings": "shape [15, 300]", "vocab_size": 10000},
            why_it_matters="LSTM operates on continuous vectors, not discrete tokens.",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="ls3",
            stage="forward_pass",
            title="LSTM Forward Pass (Timestep 1 to T)",
            description="Process each token sequentially: update forget/input/output gates and cell/hidden states.",
            input_preview={"embeddings": "[15, 300]", "h_0": "zeros", "c_0": "zeros"},
            output_preview={"h_t": "shape [15, 128]", "c_t": "shape [15, 128]"},
            formula="f_t, i_t, o_t, c_t, h_t computed at each timestep",
            why_it_matters="This is the core computation - the LSTM 'reads' the sequence and builds an internal representation.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="ls4",
            stage="prediction",
            title="Generate Prediction from Final Hidden State",
            description="Use the last hidden state h_T (or all hidden states) to predict sentiment or next word.",
            input_preview={"h_T": "[128]"},
            output_preview={"predicted": "positive", "confidence": 0.92},
            formula="y = softmax(W_y·h_T + b_y)",
            why_it_matters="The final hidden state summarizes the entire input sequence and is used for the downstream task.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="cell_state",
            definition="The LSTM's memory - a vector that carries information across timesteps, updated by gates.",
            formula_meaning="c_t = f_t⊙c_{t-1} + i_t⊙c̃_t - controls what's remembered vs. forgotten",
            example="c_t shape [128] - can remember info from 50+ timesteps ago",
            common_mistake="Confusing cell state (long-term memory) with hidden state (short-term output)",
        ),
        HoverAnnotation(
            target="hidden_state",
            definition="The LSTM's output at each timestep, used for predictions and passed to the next timestep.",
            formula_meaning="h_t = o_t ⊙ tanh(c_t) - filtered version of cell state",
            example="h_t shape [128] - encodes the 'current understanding' after reading token t",
            common_mistake="Thinking h_t is the same as c_t (it's a transformed subset of c_t, controlled by output gate)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Long Short-Term Memory",
            authors="Hochreiter, S. and Schmidhuber, J.",
            year=1997,
            doi="10.1162/neco.1997.9.8.1735",
            relevance="Original LSTM paper introducing the gating mechanism to solve vanishing gradients in RNNs.",
        ),
        ReferenceEntry(
            title="Deep Learning",
            authors="Goodfellow, I., Bengio, Y., and Courville, A.",
            year=2016,
            url="https://www.deeplearningbook.org/contents/rnn.html",
            relevance="Chapter 10 covers RNNs and LSTMs with clear diagrams of the gating mechanism.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="LSTM reads text word by word, remembering important things and forgetting unimportant details. Like remembering the main plot of a movie.",
            teaching_notes="Use a simple sentence. Show how the 'memory' (cell state) changes at each word.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="LSTM has three gates: forget (what to discard), input (what new info to add), output (what to output). Formulas: f_t = σ(W_f·[h_{t-1}, x_t]), etc.",
            technical_detail="Cell state c_t carries long-term info. Hidden state h_t is the output. Bidirectional LSTM reads both forward and backward. Stacked LSTM has multiple layers.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="LSTM solves vanishing gradients via additive cell updates (gradients flow unchanged through additions). Still widely used, though Transformers have largely replaced LSTMs for NLP. Research shows LSTMs can capture ~100-200 timesteps of dependency.",
            technical_detail="Limitations: sequential (can't parallelize), still struggles with very long dependencies. Variants: GRU (simpler, 2 gates), BiLSTM (bidirectional), Stacked LSTM (multiple layers).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="LSTM forward pass is O(T×H²) where T=timesteps, H=hidden size. Use PyTorch nn.LSTM. For NLP, embed tokens first (nn.Embedding). Bidirectional doubles parameters.",
            technical_detail="Complexity: O(T×H²) for hidden-hidden matmuls. Memory: O(L×T×H) for hidden states (L=layers). API: torch.nn.LSTM, tf.keras.layers.LSTM.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="LSTM introduces gating mechanisms in neural networks. Great for teaching why RNNs fail and how LSTMs fix it.",
            teaching_notes="Quiz: What does each gate do? Exercise: Trace an LSTM forward pass manually for a 3-word sentence. Compare RNN vs. LSTM vanishing gradient.",
        ),
    ],
    research_context="LSTM (Hochreiter & Schmidhuber, 1997) revolutionized sequence modeling by solving the vanishing gradient problem. It remained state-of-the-art for NLP until the Transformer (2017). LSTMs are still widely used for time series, speech, and resource-constrained applications.",
    teaching_notes=TeachingNotes(
        summary="LSTM uses gating mechanisms to maintain long-term dependencies in sequential data.",
        quiz_questions=[
            "What problem does LSTM solve that standard RNN cannot?",
            "What does each of the three gates (forget, input, output) control?",
            "What's the difference between cell state and hidden state?",
        ],
        classroom_demo_tips=[
            "Visualize gate activations as a heatmap over timesteps",
            "Show vanishing gradient in RNN vs. stable gradient in LSTM",
            "Compare unidirectional vs. bidirectional LSTM predictions",
        ],
        common_misconceptions=[
            "LSTM understands language (false - it models statistical patterns in sequences)",
            "More layers always improves performance (false - can overfit or be hard to train)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# Transformer Attention Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

transformer_attention_demo = DemoMetadata(
    demo_input={
        "text": "The cat sat on the mat because it was tired.",
        "highlight_word": "it",
    },
    auto_parameters={
        "num_heads": 1,
        "d_model": 64,
        "temperature": 1.0,
    },
    expected_output_preview={
        "attention_weights": {"it": {"the": 0.3, "cat": 0.45, "mat": 0.15, "tired": 0.1}},
        "most_attended": "cat",
        "num_heads": 1,
    },
    beginner_explanation="Transformer attention helps the model figure out which words are related to each other. When reading 'it was tired', the model learns that 'it' probably refers to 'cat' by paying more attention to that word.",
    advanced_explanation="Scaled Dot-Product Attention computes queries Q, keys K, and values V from inputs: Attention(Q,K,V) = softmax(QK^T/√d_k)V. Q, K, V are learned linear projections of the input. The softmax outputs (attention weights) sum to 1 and indicate how much each token should attend to every other token. Multi-head attention runs this h times in parallel with different projections, enabling the model to attend to different relationship types simultaneously.",
    formula_cards=[
        FormulaCard(
            title="Scaled Dot-Product Attention",
            formula="Attention(Q,K,V) = softmax(QK^T/√d_k)V",
            explanation="Compute similarity between queries and keys (QK^T), scale by √d_k, apply softmax to get weights, then weight the values V.",
            variables={"Q": "query matrix", "K": "key matrix", "V": "value matrix", "d_k": "dimension of keys"},
            example="For 'it', Q·K^T gives similarity to all words; softmax gives weights like [0.3, 0.45, 0.15, ...]",
        ),
        FormulaCard(
            title="Multi-Head Attention",
            formula="MultiHead(Q,K,V) = Concat(head₁, ..., head_h)W^O, where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)",
            explanation="Run attention h times in parallel with different learned projections, then concatenate and project.",
            variables={"h": "number of heads", "W_i^Q": "query projection for head i", "W^O": "output projection"},
            example="With 8 heads, the model can attend to 8 different relationship types simultaneously (syntax, semantics, coreference, etc.)",
        ),
        FormulaCard(
            title="Attention Weight Interpretation",
            formula="α_{ij} = softmax(Q_i·K_j/√d_k)",
            explanation="The attention weight α_{ij} represents how much token i attends to token j. Higher weight = stronger relationship.",
            variables={"α_{ij}": "attention weight from token i to token j"},
            example="α_{it,cat} = 0.45 means 'it' attends to 'cat' with weight 0.45 (the strongest connection)",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="ta1",
            stage="input_validation",
            title="Validate Input and Highlight Word",
            description="Check text is valid and the highlight word exists in the text.",
            input_preview={"text": "The cat sat on the mat because it was tired.", "highlight": "it"},
            output_preview={"valid": True, "sequence_length": 11},
            why_it_matters="Attention needs valid tokens to compute meaningful query-key-value interactions.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="ta2",
            stage="preprocessing",
            title="Generate Q, K, V Vectors",
            description="Apply learned linear projections to input embeddings to create Query, Key, and Value vectors for each token.",
            input_preview={"embeddings": "[11, 64]"},
            output_preview={"Q": "[11,64]", "K": "[11,64]", "V": "[11,64]"},
            formula="Q = XW^Q, K = XW^K, V = XW^V",
            why_it_matters="Q, K, V allow the model to compute different types of relationships (Q=what to look for, K=what to match against, V=what info to retrieve).",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="ta3",
            stage="computation",
            title="Compute Attention Scores (QK^T)",
            description="Calculate dot products between Query of each token and Keys of all tokens to measure similarity.",
            input_preview={"Q": "[11,64]", "K": "[11,64]"},
            output_preview={"scores": "[11,11]", "sample": "it→cat: 2.1, it→mat: 0.8, ..."},
            formula="scores_{ij} = Q_i·K_j / √d_k",
            why_it_matters="High QK^T scores mean strong relationship - the query token finds relevant info in the key token.",
            visualization_type="heatmap",
        ),
        StepExplanation(
            step_id="ta4",
            stage="computation",
            title="Apply Softmax to Get Attention Weights",
            description="Apply softmax to attention scores so weights sum to 1, making them interpretable as percentages.",
            input_preview={"scores": "[11,11]"},
            output_preview={"weights": "[11,11]", "it_row": [0.3, 0.45, 0.15, "..."]},
            formula="α_{ij} = softmax(scores_{ij}) = exp(scores_{ij}) / Σ_k exp(scores_{ik})",
            why_it_matters="These weights show exactly which words the model focuses on when processing each word.",
            visualization_type="heatmap",
        ),
        StepExplanation(
            step_id="ta5",
            stage="output",
            title="Weight Values to Get Output",
            description="Multiply attention weights by Value vectors to produce the final output representation for each token.",
            input_preview={"weights": "[11,11]", "V": "[11,64]"},
            output_preview={"output": "[11,64]", "it_understands": "cat is the subject"},
            formula="output_i = Σ_j α_{ij} × V_j",
            why_it_matters="The weighted sum creates a context-aware representation that incorporates relevant info from all tokens.",
            visualization_type="scatter",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="Q (Query)",
            definition="Vector representing what a token is looking for in other tokens.",
            formula_meaning="Q_i = X_i·W^Q - transformed input that expresses the 'query'",
            example="For 'it', Q might look for nouns that could be the referent (cat, mat, ...)",
            common_mistake="Thinking Q, K, V are the same as input embeddings (they're learned transformations)",
        ),
        HoverAnnotation(
            target="attention_weight",
            definition="A number between 0 and 1 showing how much token i focuses on token j. Row sums to 1.",
            formula_meaning="α_{ij} = softmax(Q_i·K_j/√d_k) - high score means strong attention",
            example="α_{it,cat} = 0.45 → 'it' attends to 'cat' with 45% of its attention",
            common_mistake="Thinking high attention always means correct interpretation (it's a statistical pattern, not true understanding)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Attention Is All You Need",
            authors="Vaswani, A., et al.",
            year=2017,
            arxiv_id="1706.03762",
            relevance="Original Transformer paper introducing Scaled Dot-Product Attention and Multi-Head Attention.",
        ),
        ReferenceEntry(
            title="The Illustrated Transformer",
            authors="Alammar, J.",
            year=2018,
            url="https://jalammar.github.io/illustrated-transformer/",
            relevance="Excellent visual explanation of attention mechanisms with intuitive diagrams.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="Attention is like highlighting text. When the model reads 'it', it highlights 'cat' because that's what 'it' refers to.",
            teaching_notes="Use a sentence with clear coreference. Show the attention heatmap with colors.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="Attention(Q,K,V) = softmax(QK^T/√d_k)V. Q, K, V are learned projections. Multi-head runs h attention mechanisms in parallel.",
            technical_detail="Scaling by √d_k prevents dot products from getting too large (which would push softmax into regions with tiny gradients).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="Attention enables global dependency modeling (any token can attend to any other, regardless of distance). Research shows attention patterns: some heads do syntax, some do coreference, some do position. Limitations: O(n²) complexity in sequence length.",
            technical_detail="Limitations: quadratic complexity O(n²·d) in sequence length n. Efficient variants: Sparse Attention, Linformer, Reformer. Interpretability: attention weights are post-hoc explanations, not always faithful (Jain & Wallace, 2019).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="Attention is O(n²·d) where n=sequence length, d=model dimension. Use torch.nn.MultiheadAttention. Temperature=1.0 is standard; lower = sharper weights.",
            technical_detail="Complexity: O(n²·d) self-attention. Memory: O(n²) for attention matrix. API: torch.nn.MultiheadAttention, tf.keras.layers.MultiHeadAttention.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="Attention is the core innovation of Transformers. Show how it solves the sequential bottleneck of RNNs.",
            teaching_notes="Quiz: What do Q, K, V represent? Exercise: Compute attention manually for a 3-word sentence. Discuss: Why scale by √d_k?",
        ),
    ],
    research_context="The Transformer (Vaswani et al., 2017) replaced recurrence with attention, enabling parallelization and better long-range dependency modeling. Attention mechanisms have become the foundation of modern NLP, with applications beyond NLP (vision, multimodal).",
    teaching_notes=TeachingNotes(
        summary="Scaled Dot-Product Attention allows tokens to attend to all other tokens, creating context-aware representations.",
        quiz_questions=[
            "What do Q, K, and V represent in attention?",
            "Why do we scale by √d_k in the attention formula?",
            "Compute attention weights manually for a 3-token sentence with d_k=2.",
        ],
        classroom_demo_tips=[
            "Visualize attention as a heatmap with token labels",
            "Show how attention changes for different heads",
            "Compare attention patterns for syntax vs. coreference",
        ],
        common_misconceptions=[
            "Attention weights always show true model reasoning (false - they're correlational, not causal)",
            "More heads always better (false - diminishing returns, more compute)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# BERT Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

bert_demo = DemoMetadata(
    demo_input={
        "text": "The scientist [MASK] the experiment carefully and recorded the results.",
        "masked_tokens": ["conducted", "designed", "observed"],
    },
    auto_parameters={
        "model_name": "bert-base-uncased",
        "num_layers": 12,
        "hidden_size": 768,
        "num_heads": 12,
    },
    expected_output_preview={
        "predicted_token": "conducted",
        "top_predictions": [("conducted", 0.65), ("designed", 0.18), ("observed", 0.12)],
        "attention_pattern": "focused on 'scientist' and 'experiment'",
    },
    beginner_explanation="BERT reads text in both directions (left-to-right and right-to-left at the same time) and fills in missing words. It's like a fill-in-the-blank test that understands the full context around the blank.",
    advanced_explanation="BERT (Bidirectional Encoder Representations from Transformers) uses a deep Transformer encoder (12-24 layers) to create contextualized word representations. Pre-training uses Masked Language Modeling (MLM): randomly mask 15% of tokens and predict them using bidirectional context, and Next Sentence Prediction (NSP): predict if sentence B follows sentence A. The input is [CLS] + tokens + [SEP] with segment embeddings and position embeddings. Fine-tuning adds a task-specific head on top of the [CLS] token or token outputs.",
    formula_cards=[
        FormulaCard(
            title="BERT Input Representation",
            formula="E = TokenEmbed + SegmentEmbed + PositionEmbed",
            explanation="BERT combines three embeddings: wordpiece token embeddings, segment (sentence A/B) embeddings, and position embeddings.",
            variables={"TokenEmbed": "wordpiece embedding", "SegmentEmbed": "sentence A/B embedding", "PositionEmbed": "position in sequence"},
            example="Input: [CLS] The scientist [MASK] ... → sum of token + segment + position embeddings",
        ),
        FormulaCard(
            title="Masked Language Modeling (MLM) Loss",
            formula="L_MLM = -Σ log P(masked_token | context)",
            explanation="Pre-training objective: maximize probability of correct masked tokens given bidirectional context.",
            variables={"P(masked_token|context)": "predicted probability from BERT output"},
            example="For 'The scientist [MASK]...', model predicts 'conducted' with P=0.65",
        ),
        FormulaCard(
            title="Self-Attention in BERT",
            formula="head_i = Attention(XW_i^Q, XW_i^K, XW_i^V); MultiHead = Concat(all heads)W^O",
            explanation="Each of BERT's 12 layers has 12 attention heads. Each head learns different relationships (syntax, semantics, coreference).",
            variables={"X": "input to the layer", "W_i^*": "learned projection for head i"},
            example="Layer 6, Head 8 might focus on subject-verb agreement; Head 3 might track coreference",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="bt1",
            stage="input_validation",
            title="Validate Input with [MASK] Token",
            description="Check that input text contains [MASK] token for MLM prediction.",
            input_preview={"text": "The scientist [MASK] the experiment...", "mask_count": 1},
            output_preview={"valid": True, "sequence_length": 14},
            why_it_matters="BERT's MLM pre-training requires masked tokens to predict. Without [MASK], it's just encoding.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="bt2",
            stage="preprocessing",
            title="Tokenize with WordPiece & Add Special Tokens",
            description="Split text into WordPiece subwords, add [CLS] at start, [SEP] between sentences, and convert to token IDs.",
            input_preview={"text": "The scientist [MASK] ..."},
            output_preview={"tokens": ["[CLS]", "the", "scientist", "[MASK]", "..."], "token_ids": [101, 1996, 2925, 103, "..."]},
            why_it_matters="WordPiece handles out-of-vocabulary words by splitting into subwords. Special tokens provide structure.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="bt3",
            stage="forward_pass",
            title="BERT Encoder (12 Layers of Transformer)",
            description="Pass input through 12 Transformer layers, each with multi-head self-attention and feed-forward networks.",
            input_preview={"input_ids": "[14]", "token_embeddings": "[14, 768]"},
            output_preview={"last_hidden": "[14, 768]", "cls_output": "[768]"},
            formula="Each layer: MultiHeadAttention → Add&Norm → FeedForward → Add&Norm",
            why_it_matters="Each layer refines representations by attending to different contextual relationships. Deep layers capture high-level semantics.",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="bt4",
            stage="prediction",
            title="Predict Masked Token",
            description="Take the [MASK] position's output, apply the MLM head (linear + softmax), and get top predictions.",
            input_preview={"mask_position_output": "[768]"},
            output_preview={"predicted": "conducted", "top_5": [("conducted", 0.65), ("designed", 0.18), "..."]},
            formula="P(token|context) = softmax(MLM_head(h_{[MASK]}))",
            why_it_matters="This shows BERT's contextual understanding - it predicts tokens based on full bidirectional context.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="[MASK]",
            definition="Special token that BERT learns to predict during pre-training. During fine-tuning, it can be used for fill-in-the-blank tasks.",
            formula_meaning="P(masked_token|context) = softmax(W·h_{mask} + b)",
            example="'The scientist [MASK]...' → BERT predicts 'conducted' with highest probability",
            common_mistake="Using [MASK] during inference on tasks it wasn't trained for (it's specifically for MLM pre-training)",
        ),
        HoverAnnotation(
            target="[CLS] token",
            definition="Special token at the start of every BERT input. The final layer's [CLS] output is used for classification tasks.",
            formula_meaning="h_{[CLS]}^{final} encodes the entire input sequence for classification",
            example="For sentiment analysis, a linear classifier takes h_{[CLS]}^{final} (768-dim) → positive/negative",
            common_mistake="Using [CLS] for token-level tasks (use token outputs instead)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            authors="Devlin, J., Chang, M.W., Lee, K., and Toutanova, K.",
            year=2019,
            arxiv_id="1810.04805",
            relevance="Original BERT paper introducing bidirectional pre-training with MLM and NSP objectives.",
        ),
        ReferenceEntry(
            title="Visualizing and Understanding the BERT Modelf",
            authors="Rogers, A., Kovaleva, O., and Rumshisky, A.",
            year=2020,
            arxiv_id="1904.13579",
            relevance="Comprehensive analysis of what BERT learns across its layers and attention heads.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="BERT reads text in both directions and fills in blanks. It understands context from both left and right sides of a word.",
            teaching_notes="Use a simple fill-in-the-blank sentence. Show top predictions with probabilities.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="BERT uses 12-24 Transformer encoder layers with MLM pre-training: randomly mask 15% of tokens and predict them using bidirectional context.",
            technical_detail="Input: [CLS] + tokens + [SEP]. Representations: Token + Segment + Position embeddings. Output: contextualized embeddings for each token.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="BERT's bidirectional pre-training was a breakthrough, achieving SOTA on 11 NLP tasks. Research shows lower layers capture syntax, upper layers capture semantics. Limitations: fixed input length (512 tokens), compute cost. Led to RoBERTa, ALBERT, ELECTRA improvements.",
            technical_detail="Limitations: quadratic attention O(n²), not generative (encoder-only). Alternatives: RoBERTa (better pre-training), ALBERT (parameter sharing), ELECTRA (discriminator-based pre-training).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="BERT-base: 12 layers, 768 hidden, 12 heads, 110M params. Use HuggingFace transformers. Inference: O(L×n²×d) where L=layers, n=seq_len, d=hidden.",
            technical_detail="Complexity: O(L×n²×d). Memory: O(L×n×d) for activations. API: transformers.AutoModelForMaskedLM, transformers.pipeline('fill-mask').",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="BERT introduced bidirectional pre-training. Show how context from both sides improves predictions vs. left-to-right only.",
            teaching_notes="Quiz: Why is bidirectional better than left-to-right? Exercise: Compare BERT predictions with/without right context. Discuss: Why 15% masking?",
        ),
    ],
    research_context="BERT (Devlin et al., 2019) revolutionized NLP by introducing deep bidirectional pre-training. It achieved state-of-the-art on 11 NLP tasks and spawned an entire family of models (RoBERTa, ALBERT, ELECTRA, DeBERTa). Its success demonstrated the power of transfer learning in NLP.",
    teaching_notes=TeachingNotes(
        summary="BERT uses bidirectional Transformer encoders pre-trained with masked language modeling to create contextualized word representations.",
        quiz_questions=[
            "Why is bidirectional context better than left-to-right for understanding 'The scientist [MASK]...'?",
            "What does the [CLS] token represent, and when do we use it?",
            "Why was the 15% masking rate chosen for MLM pre-training?",
        ],
        classroom_demo_tips=[
            "Visualize attention weights across layers and heads",
            "Show how predictions change as you add more context",
            "Compare BERT-base vs. BERT-large predictions",
        ],
        common_misconceptions=[
            "BERT understands language (false - it models statistical patterns, not meaning)",
            "BERT can generate text (false - it's encoder-only, not autoregressive)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# GPT Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

gpt_demo = DemoMetadata(
    demo_input={
        "text": "The secret to a happy life is",
        "max_new_tokens": 20,
        "temperature": 0.7,
    },
    auto_parameters={
        "model_name": "gpt2",
        "num_layers": 12,
        "hidden_size": 768,
        "num_heads": 12,
        "temperature": 0.7,
    },
    expected_output_preview={
        "generated_text": "The secret to a happy life is finding balance, surrounding yourself with positive people, and pursuing your passions.",
        "tokens_generated": 15,
        "perplexity": 25.3,
    },
    beginner_explanation="GPT is like an auto-complete on steroids. You give it the beginning of a sentence, and it predicts what comes next, one word at a time, writing entire paragraphs that sound human-like.",
    advanced_explanation="GPT (Generative Pre-trained Transformer) uses a Transformer decoder architecture with autoregressive language modeling: predict next token given all previous tokens. It uses masked self-attention (causal attention) where each token can only attend to previous tokens, not future ones. Pre-training maximizes L = Σ log P(t_i | t_{<i}). GPT-2 has 1.5B parameters; GPT-3 has 175B. Temperature controls randomness: P_softmax = softmax(logits / T). Lower T = more deterministic; higher T = more random.",
    formula_cards=[
        FormulaCard(
            title="Autoregressive Language Modeling",
            formula="L = Σ_{i=1}^n log P(t_i | t_1, ..., t_{i-1})",
            explanation="GPT maximizes the log-likelihood of each token given all previous tokens. This is causal (left-to-right) modeling.",
            variables={"t_i": "i-th token", "n": "sequence length"},
            example="For 'happy life is', model computes P('happy'|'The'), P('life'|'The happy'), P('is'|'The happy life')",
        ),
        FormulaCard(
            title="Causal Self-Attention (Masked)",
            formula="Attention(Q,K,V) = softmax((QK^T + M)/√d_k)V, where M_{ij} = -∞ if j > i",
            explanation="Causal masking M prevents attention to future tokens. Each token only attends to itself and previous tokens.",
            variables={"M": "causal mask (upper triangular = -∞)", "i": "query position", "j": "key position"},
            example="When processing 'life' (position 3), it can attend to 'The', 'happy', 'life' but NOT 'is' (future)",
        ),
        FormulaCard(
            title="Temperature Sampling",
            formula="P_i = softmax(logits_i / T)",
            explanation="Temperature T controls randomness. T=1 is standard softmax; T<1 is sharper (more confident); T>1 is flatter (more random).",
            variables={"T": "temperature (typically 0.1 to 2.0)", "logits_i": "raw model output for token i"},
            example="T=0.7: 'happy' with logit 3.0 → P=0.6; T=2.0: same logit → P=0.35 (more random)",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="gp1",
            stage="input_validation",
            title="Validate Prompt",
            description="Check that the input prompt is non-empty and within model's context window.",
            input_preview={"text": "The secret to a happy life is", "prompt_tokens": 7},
            output_preview={"valid": True, "prompt_length": 7},
            why_it_matters="GPT needs a valid prompt to start generation. Context window limit is typically 1024-4096 tokens.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="gp2",
            stage="preprocessing",
            title="Tokenize with Byte-Pair Encoding (BPE)",
            description="Split prompt into BPE subword tokens and convert to token IDs for the model.",
            input_preview={"text": "The secret to a happy life is"},
            output_preview={"tokens": ["The", "secret", "to", "a", "happy", "life", "is"], "token_ids": [464, 13067, 284, 257, 3139, 7966, 318]},
            why_it_matters="BPE handles out-of-vocabulary words. Token IDs are the actual input to the model.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="gp3",
            stage="generation_loop",
            title="Autoregressive Generation (Step 1 to T)",
            description="At each step, run the Transformer decoder on all previous tokens, predict next token distribution, sample using temperature, and append to sequence.",
            input_preview={"current_seq": "[464, 13067, ...]", "step": 1},
            output_preview={"new_token": " finding", "updated_seq": "[..., 1216]"},
            formula="P(t_new | t_1, ..., t_current) = softmax(Transformer(t_1...t_current) / T)",
            why_it_matters="This is the core generation loop - the model builds the output one token at a time, each prediction conditioned on all previous tokens.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="gp4",
            stage="output",
            title="Decode Generated Tokens to Text",
            description="Convert generated token IDs back to text using the BPE decoder.",
            input_preview={"generated_token_ids": [1216, 11735, 4, "..."]},
            output_preview={"generated_text": "finding balance, surrounding yourself...", "total_tokens": 20},
            why_it_matters="This is the final output that users see - the model's generated continuation of the prompt.",
            visualization_type="text",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="causal_mask",
            definition="A mask that prevents the model from attending to future tokens, ensuring autoregressive generation.",
            formula_meaning="M_{ij} = -∞ if j > i (future positions get -∞ → softmax gives 0 probability)",
            example="When generating token 5, positions 6, 7, 8, ... are masked out (attention = 0)",
            common_mistake="Thinking GPT can see future tokens (it can't - causal mask prevents this by design)",
        ),
        HoverAnnotation(
            target="temperature",
            definition="Parameter that controls randomness in sampling. Lower = more deterministic; higher = more random/creative.",
            formula_meaning="softmax(logits / T): T<1 sharpens distribution; T>1 flattens it",
            example="T=0.1: almost greedy (always picks highest logit); T=2.0: very random output",
            common_mistake="Setting T=0 (not actually 0, use argmax instead; T→0 in softmax approaches argmax)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Language Models are Unsupervised Multitask Learners",
            authors="Radford, A., et al.",
            year=2019,
            arxiv_id="1901.07291",
            relevance="GPT-2 paper showing that large-scale generative pre-training enables zero-shot task performance.",
        ),
        ReferenceEntry(
            title="Language Models are Few-Shot Learners",
            authors="Brown, T., et al.",
            year=2020,
            arxiv_id="2005.14165",
            relevance="GPT-3 paper demonstrating in-context learning with 175B parameters.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="GPT writes text one word at a time, always looking at what it already wrote to decide what comes next. Like predictive text on your phone, but much smarter.",
            teaching_notes="Use a simple prompt. Show how changing temperature affects creativity vs. coherence.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="GPT uses a Transformer decoder with causal (masked) self-attention. It predicts next token: P(t_i|t_{<i}). Temperature T controls sampling randomness.",
            technical_detail="Causal mask ensures token i only attends to positions ≤ i. BPE tokenization handles OOV. Autoregressive: generate one token at a time.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="GPT demonstrated that scaling autoregressive LMs enables few-shot in-context learning (Brown et al., 2020). Limitations: no bidirectional context, expensive inference (autoregressive can't parallelize). Led to GPT-3, GPT-4, and the modern LLM era.",
            technical_detail="Limitations: quadratic attention, no bidirectional context (worse for understanding tasks), autoregressive bottleneck. Alternatives: encoder-decoder (T5), non-autoregressive generation.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="GPT-2: 1.5B params, O(n²·d) per generation step. Use HuggingFace. For faster inference, use caching (KV cache) to avoid recomputing past keys/values.",
            technical_detail="Complexity: O(L×n²×d) without cache; O(L×n×d) with KV cache. API: transformers.GPT2LMHeadModel, transformers.pipeline('text-generation').",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="GPT introduced the modern LLM paradigm. Show how autoregressive generation differs from bidirectional encoding (BERT).",
            teaching_notes="Quiz: Why can't GPT see future tokens? Exercise: Compare greedy (T→0) vs. creative (T=1.0) generation. Discuss: Why is GPT good for generation but not understanding?",
        ),
    ],
    research_context="GPT-2 (Radford et al., 2019) showed that large-scale generative pre-training enables zero-shot generalization. GPT-3 (Brown et al., 2020) demonstrated few-shot in-context learning with 175B parameters, launching the modern LLM era. These models use purely autoregressive (left-to-right) generation.",
    teaching_notes=TeachingNotes(
        summary="GPT uses a Transformer decoder with causal attention to generate text autoregressively, one token at a time.",
        quiz_questions=[
            "Why does GPT use causal (masked) attention instead of bidirectional?",
            "What does temperature control in sampling, and how do you set it for greedy vs. creative generation?",
            "Why can't GPT do bidirectional understanding like BERT?",
        ],
        classroom_demo_tips=[
            "Show generation step-by-step with token predictions at each step",
            "Compare outputs at different temperatures (0.1, 0.7, 1.5)",
            "Visualize causal attention mask as a lower-triangular matrix",
        ],
        common_misconceptions=[
            "GPT understands what it's writing (false - it models statistical patterns, not meaning)",
            "More parameters always means better generation (false - can lead to repetition or hallucination without proper tuning)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# T5 Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

t5_demo = DemoMetadata(
    demo_input={
        "text": "translate English to German: The house is beautiful.",
        "task": "translation",
    },
    auto_parameters={
        "model_name": "t5-small",
        "num_layers": 6,
        "hidden_size": 512,
        "num_heads": 8,
    },
    expected_output_preview={
        "output_text": "Das Haus ist wunderschön.",
        "task": "translation",
        "input_tokens": 10,
        "output_tokens": 5,
    },
    beginner_explanation="T5 turns every NLP task into a text-to-text problem. You give it text with a task prefix (like 'translate:' or 'summarize:'), and it generates the answer as text. It's like a universal NLP machine that can do translation, summarization, Q&A, and more.",
    advanced_explanation="T5 (Text-to-Text Transfer Transformer) unifies NLP tasks by converting all inputs and outputs to text strings. Architecture: encoder-decoder Transformer (like the original Transformer). Pre-training: masked span corruption (mask random spans of text and predict the masked tokens). Input format: 'task_prefix: input_text'. Output: target text. Tasks include translation, summarization, Q&A, classification (convert labels to strings). T5 uses relative position biases instead of absolute position embeddings.",
    formula_cards=[
        FormulaCard(
            title="T5 Input Format (Text-to-Text)",
            formula="input = 'task_prefix: original_input'; output = 'target_text'",
            explanation="Every task is cast as text-to-text. The model learns to map input text (with task prefix) to output text.",
            variables={"task_prefix": "e.g., 'translate English to German', 'summarize', 'cola sentence'"},
            example="Input: 'translate English to German: The house is beautiful.' → Output: 'Das Haus ist wunderschön.'",
        ),
        FormulaCard(
            title="Masked Span Corruption (Pre-training)",
            formula="Input: 'The <X> is <Y>.'; Output: '<X> house <Y> beautiful'",
            explanation="T5 masks random spans (not just single tokens) and predicts the masked spans as a sequence. This teaches the model to understand and generate text.",
            variables={"<X>, <Y>": "masked spans (1-3 tokens each)"},
            example="Original: 'The house is beautiful.' → Masked: 'The <X> is <Y>.' → Target: '<X> house <Y> beautiful'",
        ),
        FormulaCard(
            title="Encoder-Decoder Attention",
            formula="DecoderAttention(Q_d, K_e, V_e) = softmax(Q_d K_e^T / √d_k) V_e",
            explanation="The decoder attends to the encoder's output (all input tokens), not just previous decoder tokens. This is cross-attention.",
            variables={"Q_d": "decoder query", "K_e, V_e": "encoder key/value (from input processing)"},
            example="When generating 'wunderschön', the decoder looks at all encoder outputs for 'The house is beautiful.'",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="t5_1",
            stage="input_validation",
            title="Validate Input with Task Prefix",
            description="Check that input has a valid task prefix (translate, summarize, etc.) and text.",
            input_preview={"text": "translate English to German: The house is beautiful."},
            output_preview={"valid": True, "task": "translation", "input_tokens": 10},
            why_it_matters="T5 requires a task prefix to know what to do. Without it, the model doesn't know the expected output format.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="t5_2",
            stage="preprocessing",
            title="Tokenize with SentencePiece & Encode",
            description="Use SentencePiece to tokenize input text and convert to token IDs for the encoder.",
            input_preview={"text": "translate English to German: The house is beautiful."},
            output_preview={"encoder_tokens": ["translate", "English", "to", "German", ":", "The", "house", "..."]},
            why_it_matters="SentencePiece is language-agnostic (no dependency on English tokenization). Works for all languages.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="t5_3",
            stage="encoder_forward",
            title="T5 Encoder (6 Layers)",
            description="Process input through the encoder's 6 Transformer layers to create contextualized representations of the input.",
            input_preview={"encoder_input": "[10]", "encoder_layers": 6},
            output_preview={"encoder_output": "[10, 512]", "last_hidden_states": "[10, 512]"},
            formula="Encoder: SelfAttention → Add&Norm → FeedForward → Add&Norm (×6 layers)",
            why_it_matters="The encoder creates a rich representation of the input that the decoder will use for generation.",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="t5_4",
            stage="decoder_generation",
            title="T5 Decoder (Autoregressive Generation)",
            description="The decoder generates output tokens autoregressively, using cross-attention to attend to encoder outputs.",
            input_preview={"decoder_input": "start token", "encoder_output": "[10, 512]"},
            output_preview={"generated_tokens": ["Das", "Haus", "ist", "wunderschön", "."]},
            formula="Decoder: SelfAttention → CrossAttention(encoder_output) → FeedForward (×6 layers)",
            why_it_matters="This is where the actual translation/summarization happens. The decoder uses both its own history and the encoder's input representation.",
            visualization_type="timeline",
        ),
        StepExplanation(
            step_id="t5_5",
            stage="output",
            title="Decode Output Tokens to Text",
            description="Convert generated token IDs back to text using SentencePiece decoder.",
            input_preview={"decoder_token_ids": [123, 456, 789, "..."]},
            output_preview={"output_text": "Das Haus ist wunderschön.", "output_tokens": 5},
            why_it_matters="Final output that users see - the result of the text-to-text transformation.",
            visualization_type="text",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="task_prefix",
            definition="A text string at the start of input that tells T5 what task to perform (e.g., 'translate:', 'summarize:').",
            formula_meaning="input = prefix + ': ' + text; model learns to condition on prefix",
            example="'translate English to German: Hello.' → model knows to translate to German",
            common_mistake="Forgetting the colon after the task prefix (T5 expects 'prefix: text' format)",
        ),
        HoverAnnotation(
            target="cross-attention",
            definition="Attention mechanism in the decoder that allows it to attend to encoder outputs (the input text representation).",
            formula_meaning="CrossAttention(Q_d, K_e, V_e) - Q comes from decoder, K/V come from encoder",
            example="When generating 'wunderschön', decoder cross-attention focuses on 'beautiful' in the encoder output",
            common_mistake="Thinking decoder only attends to its own previous tokens (it also attends to all encoder outputs via cross-attention)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer",
            authors="Raffel, C., et al.",
            year=2019,
            arxiv_id="1910.10683",
            relevance="T5 paper introducing the text-to-text framework that unifies all NLP tasks.",
        ),
        ReferenceEntry(
            title="T5: Text-To-Text Transfer Transformer (Official Blog)",
            authors="Google AI Blog",
            year=2020,
            url="https://ai.googleblog.com/2020/02/exploring-transfer-learning-with-t5.html",
            relevance="Accessible overview of T5's text-to-text framework and pre-training objectives.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="T5 can do any NLP task if you tell it what to do in words. Say 'translate:' and it translates. Say 'summarize:' and it summarizes.",
            teaching_notes="Demo translation and summarization with simple examples. Show how task prefix changes the output.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="T5 uses an encoder-decoder Transformer. All tasks are text-to-text: 'task: input' → 'output'. Pre-training: masked span corruption (predict masked spans).",
            technical_detail="Encoder processes input, decoder generates output with cross-attention to encoder. Uses relative position biases instead of absolute positions.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="T5's text-to-text framework is elegant and unified. Research shows span corruption is more sample-efficient than token-level MLM. T5-XXL (11B) was SOTA on many benchmarks. Limitations: slower inference (encoder-decoder), larger than encoder-only models.",
            technical_detail="Limitations: encoder-decoder is slower than encoder-only for understanding tasks. Variants: mT5 (multilingual), ByT5 (byte-level), UL2 (unified pre-training with different corruption strategies).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="T5-small: 60M params, 6 layers each for encoder/decoder. Use HuggingFace. For inference, it's O((n_enc² + n_dec²)×d) per generation step.",
            technical_detail="Complexity: O(L×n²×d) for both encoder and decoder. API: transformers.T5ForConditionalGeneration, transformers.pipeline('translation', model='t5-small').",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="T5 unifies NLP tasks under one framework. Great for teaching transfer learning and multi-task learning.",
            teaching_notes="Quiz: Why is text-to-text elegant? Exercise: Convert classification, NER, and summarization to text-to-text format. Discuss: When would you use T5 vs. BERT vs. GPT?",
        ),
    ],
    research_context="T5 (Raffel et al., 2019) unified all NLP tasks into a text-to-text framework, showing that a single model can perform translation, summarization, Q&A, and classification by framing them as text input → text output. This simplified multi-task learning and transfer learning.",
    teaching_notes=TeachingNotes(
        summary="T5 casts all NLP tasks as text-to-text, using an encoder-decoder Transformer pre-trained with masked span corruption.",
        quiz_questions=[
            "How does T5 unify different NLP tasks into a single framework?",
            "What is masked span corruption, and how does it differ from BERT's MLM?",
            "When would you use T5 vs. BERT vs. GPT? Give examples.",
        ],
        classroom_demo_tips=[
            "Demo 3+ tasks (translation, summarization, Q&A) with the same model",
            "Show encoder-decoder attention visualization",
            "Compare T5-small, T5-base, T5-large outputs",
        ],
        common_misconceptions=[
            "T5 is just like BERT (false - it's encoder-decoder, not encoder-only)",
            "T5 can only do one task (false - it's multi-task via text-to-text framing)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# FastText Demo Metadata
# ──────────────────────────────────────────────────────────────────────────────

fasttext_demo = DemoMetadata(
    demo_input={
        "text": "banana apple orange fruit tropical sweet",
        "mode": "similarity",
    },
    auto_parameters={
        "embedding_dim": 100,
        "window_size": 5,
        "min_count": 1,
        "subword_minn": 3,
        "subword_maxn": 6,
    },
    expected_output_preview={
        "vocabulary_size": 6,
        "embedding_dim": 100,
        "similarity_pairs": [("banana", "apple", 0.78), ("orange", "fruit", 0.82)],
        "oov_word": "bananarama",
        "oov_similarity": 0.65,
    },
    beginner_explanation="FastText is like Word2Vec but smarter - it looks at small pieces of words (subwords) too. This means it can guess the meaning of new words it's never seen before by looking at their pieces, like 'bananarama' contains 'banana'.",
    advanced_explanation="FastText (Bojanowski et al., 2017) extends Word2Vec by representing each word as a bag of character n-grams (3-6 characters). The word embedding is the sum of its subword embeddings plus the whole-word embedding. This allows handling out-of-vocabulary (OOV) words: 'bananarama' gets embeddings from 'ban', 'ana', 'rama', etc., even if the model never saw 'bananarama' during training. FastText typically uses Skip-gram with negative sampling, same as Word2Vec, but with subword information.",
    formula_cards=[
        FormulaCard(
            title="FastText Word Representation",
            formula="v_w = sum of (subword_n-gram embeddings for w) + whole_word_embedding",
            explanation="Each word is represented by summing embeddings of all its character n-grams (typically 3-6 chars) plus the whole-word embedding.",
            variables={"v_w": "embedding vector for word w", "n-grams": "character sequences like 'ban', 'ana', 'nan', ..."},
            example="'banana' → n-grams: '<ba', 'ban', 'ana', 'nan', 'ana', 'na>' + whole-word 'banana' → sum = v_banana",
        ),
        FormulaCard(
            title="FastText Skip-gram Objective",
            formula="J(θ) = Σ log P(w_O|w_I) = Σ log σ(v_{w_O}·v_{w_I}) + Σ log σ(-v_{neg}·v_{w_I})",
            explanation="Same as Word2Vec Skip-gram with negative sampling, but v_w now includes subword information.",
            variables={"v_{w_I}": "center word (with subwords)", "v_{w_O}": "context word (with subwords)"},
            example="For 'banana', v_{banana} = sum of '<ba', 'ban', 'ana', ..., 'na>' embeddings",
        ),
        FormulaCard(
            title="OOV Handling",
            formula="v_oov = Σ embeddings(n-grams in oov)",
            explanation="Out-of-vocabulary words get embeddings from their character n-grams, even if not seen during training.",
            variables={"oov": "out-of-vocabulary word"},
            example="'bananarama' → n-grams include 'banana' overlap with known word 'banana' → meaningful embedding!",
        ),
    ],
    step_explanations=[
        StepExplanation(
            step_id="ft1",
            stage="input_validation",
            title="Validate Input Text",
            description="Check that input has sufficient words to learn subword patterns.",
            input_preview={"text": "banana apple orange fruit...", "word_count": 6},
            output_preview={"valid": True, "vocab_size": 6},
            why_it_matters="Need enough words to learn meaningful subword representations. More data = better OOV handling.",
            visualization_type="table",
        ),
        StepExplanation(
            step_id="ft2",
            stage="preprocessing",
            title="Extract Character N-grams",
            description="For each word, extract all character n-grams (typically 3-6 chars) and add word boundaries (<, >).",
            input_preview={"words": ["banana", "apple", "..."]},
            output_preview={"n-grams": {"banana": ["<ba","ban","ana","na>"]}, "unique_ngrams": 28},
            why_it_matters="Subword n-grams capture morphological information (prefixes, suffixes, roots) that help with OOV and rare words.",
            visualization_type="graph",
        ),
        StepExplanation(
            step_id="ft3",
            stage="training",
            title="Train with Skip-gram + Negative Sampling",
            description="Learn embeddings for each n-gram and whole word, optimizing the Skip-gram objective with negative sampling.",
            input_preview={"n-grams": ["..."], "training_pairs": ["..."]},
            output_preview={"embedding_shape": [34, 100], "loss": 0.28},
            formula="v_w = sum(subword_embeddings) + whole_word_embedding",
            why_it_matters="This is the core learning - the model discovers that subwords carry meaning (e.g., '-ing' = verb, '-tion' = noun).",
            visualization_type="scatter",
        ),
        StepExplanation(
            step_id="ft4",
            stage="output",
            title="Compute Similarities & Handle OOV",
            description="Measure cosine similarity between word vectors. Demonstrate OOV handling by computing embedding for an unseen word using its n-grams.",
            input_preview={"embeddings": "[34, 100]", "oov_word": "bananarama"},
            output_preview={"similarities": [("apple", 0.78), "..."], "oov_embedding": "computed from n-grams!", "oov_sim": 0.65},
            formula="sim(w₁, w₂) = (v₁·v₂) / (||v₁|| × ||v₂||)",
            why_it_matters="OOV handling is FastText's key advantage over Word2Vec - it can embed any word, even never seen during training.",
            visualization_type="bar",
        ),
    ],
    hover_annotations=[
        HoverAnnotation(
            target="character_n-grams",
            definition="Substrings of length n (typically 3-6) extracted from words with boundary symbols (<, >).",
            formula_meaning="For 'banana' with n=3: <ba, ban, ana, nan, ana, na> (note: < and > are boundaries)",
            example="'apple' n-grams (n=3): <ap, app, ppl, ple, le>",
            common_mistake="Forgetting word boundaries (<, >) which help distinguish prefixes/suffixes from middle n-grams",
        ),
        HoverAnnotation(
            target="OOV (Out-of-Vocabulary)",
            definition="Words not seen during training. FastText can embed them using character n-grams; Word2Vec cannot.",
            formula_meaning="v_oov = Σ embeddings(n-grams in oov) - composes embedding from known subword parts",
            example="'bananarama' → n-grams overlap with 'banana' → gets meaningful embedding despite never being trained",
            common_mistake="Thinking FastText eliminates OOV entirely (it reduces the problem but very rare n-grams may still be unknown)",
        ),
    ],
    references=[
        ReferenceEntry(
            title="Enriching Word Vectors with Subword Information",
            authors="Bojanowski, P., Grave, E., Joulin, A., and Mikolov, T.",
            year=2017,
            arxiv_id="1607.04606",
            relevance="FastText paper introducing character n-gram embeddings to handle OOV and improve morphologically rich languages.",
        ),
        ReferenceEntry(
            title="Bag of Tricks for Efficient Text Classification",
            authors="Joulin, A., Grave, E., Bojanowski, P., and Mikolov, T.",
            year=2017,
            arxiv_id="1607.01759",
            relevance="FastText for text classification - shows how subword info improves performance on rare words and morphologically rich languages.",
        ),
    ],
    receiver_mode_explanations=[
        ReceiverModeExplanation(
            mode=ReceiverMode.BEGINNER,
            explanation="FastText looks at pieces of words (like 'ban', 'ana') to understand meaning. This helps it understand new words it hasn't seen before!",
            teaching_notes="Show OOV word prediction. Compare with Word2Vec which can't handle OOV.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.STUDENT,
            explanation="FastText = Word2Vec + subword info. Each word = sum of character n-gram (3-6) embeddings + whole-word embedding. Handles OOV via n-grams.",
            technical_detail="N-gram range: minn=3, maxn=6 typical. Skip-gram with negative sampling. For OOV 'bananarama', sum embeddings of '<ba', 'ban', ..., 'rama', 'ma>' (if seen during training).",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.RESEARCHER,
            explanation="FastText's subword approach is especially beneficial for morphologically rich languages (Turkish, Finnish, Arabic) and rare words. Research shows 10-20% improvement on rare words vs. Word2Vec. Limitations: more parameters, slower training. Led to subword-based models like BPE in BERT/GPT.",
            technical_detail="Limitations: more memory (need n-gram embeddings), slower training. Comparison: BPE (used in BERT/GPT) is another subword approach but merges frequent pairs instead of using character n-grams.",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.ENGINEER,
            explanation="FastText trains slower than Word2Vec (more parameters for n-grams). Use gensim or Facebook's original implementation. OOV is automatic - just pass any word.",
            technical_detail="Complexity: O(N×w×(V+Ngrams)×d). Memory: O((V+Ngrams)×d). API: gensim.models.FastText, or load pre-trained: fasttext.util.load_model('cc.en.300.bin').",
        ),
        ReceiverModeExplanation(
            mode=ReceiverMode.INSTRUCTOR,
            explanation="FastText introduces subword linguistics to embeddings. Show how morphology (prefixes, suffixes) helps with rare and OOV words.",
            teaching_notes="Quiz: How does FastText handle OOV? Exercise: Manually compute n-grams for 'running'. Compare Word2Vec vs. FastText on rare words.",
        ),
    ],
    research_context="FastText (Bojanowski et al., 2017) addressed Word2Vec's OOV limitation by incorporating character n-gram information. It's particularly effective for morphologically rich languages and rare words. The subword idea influenced modern tokenization in BERT (WordPiece) and GPT (BPE).",
    teaching_notes=TeachingNotes(
        summary="FastText extends Word2Vec with character n-gram embeddings, enabling out-of-vocabulary word handling and better rare word representations.",
        quiz_questions=[
            "How does FastText represent a word using subwords?",
            "Why can FastText handle OOV words while Word2Vec cannot?",
            "What are the typical n-gram sizes used in FastText, and why?",
        ],
        classroom_demo_tips=[
            "Visualize subword n-grams for a morphologically complex word",
            "Compare OOV handling: FastText succeeds, Word2Vec fails",
            "Show similarity improvements on rare words vs. Word2Vec",
        ],
        common_misconceptions=[
            "FastText eliminates OOV entirely (false - very rare n-grams may still be unknown)",
            "FastText is always better than Word2Vec (false - for common words, they're similar; FastText is slower to train)",
        ],
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# Export all demo metadata as a dictionary
# ──────────────────────────────────────────────────────────────────────────────

TRANSFORMER_DEMO_METADATA = {
    "word_embeddings": word_embeddings_demo,
    "lstm": lstm_demo,
    "transformer_attention": transformer_attention_demo,
    "bert": bert_demo,
    "gpt": gpt_demo,
    "t5": t5_demo,
    "fasttext": fasttext_demo,
}
