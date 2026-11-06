# Project explanation — learn it well enough to defend it

This note is deliberately written in plain language. Read it alongside the source files.

## 1. The problem

A normal product search often depends on exact keywords and filters. A shopper may describe a need in everyday language: "I need something formal for an interview, navy blue, size M, under ₹4,000."

The system tries to convert that sentence into useful product preferences and retrieve relevant catalogue records.

## 2. The request lifecycle

1. The browser collects the message and optional dropdown choices.
2. It sends a JSON request to FastAPI (`POST /api/chat`).
3. `SalesAssociatePipeline.run()` invokes the LangGraph graph.
4. Each graph node reads the current state and adds or updates fields.
5. The final state is converted into JSON by FastAPI.
6. The browser displays the pitch and product cards.

## 3. The five nodes

### Node 1 — `extract_intent`

**Question answered:** What is the shopper looking for?

Extracts or carries forward fields such as category, subcategory, product type, size, colour, occasion and constraints. Explicit dropdown values can complement text-based extraction.

**Be ready to explain:** intent is the goal; entities/slots are the details that describe the goal.

### Node 2 — `synthesize_query`

**Question answered:** How can we express the request in a retrieval-friendly sentence?

The Groq service can rewrite a short or fragmented request into a more descriptive sentence. If no API key is available or the call fails, a local fallback is used.

**Be ready to explain:** query synthesis changes the wording of the search query; it does not itself retrieve products.

### Node 3 — `embed_query`

**Question answered:** How can text be compared mathematically?

The embedding service maps the synthesized sentence to a vector. MPNet is intended to produce a 768-dimensional semantic representation. The implementation also has a fallback vectorization method; that fallback is not a transformer model.

**Be ready to explain:** an embedding is a numerical representation, not a product identifier.

### Node 4 — `retrieve_and_rank`

**Question answered:** Which catalogue items are the closest matches?

The pipeline compares the query vector with product vectors, applies supported metadata constraints, and selects the highest-ranked candidates.

**Be ready to explain:** hard filters remove ineligible products; similarity ranking orders the remaining candidates.

### Node 5 — `generate_pitch`

**Question answered:** How should the results be communicated?

The Groq service can generate a friendly explanation using the retrieved products. A fallback response is used when the LLM is unavailable.

**Be ready to explain:** the model should explain retrieved catalogue facts, not invent stock, discounts or product specifications.

## 4. Five terms you must know

- **LLM:** a language model that generates or transforms text.
- **Embedding:** a vector representation of text or an item.
- **Vector retrieval:** finding vectors close to a query vector.
- **Cosine similarity:** a measure of the angle between two non-zero vectors.
- **RAG:** retrieve relevant external information and use it as context for generation.

## 5. Interview questions to practise

1. What problem does the project solve?
2. Why is keyword search insufficient for conversational product discovery?
3. What is the difference between an LLM and an embedding model?
4. Why is the embedding dimension 768?
5. Explain cosine similarity and its formula.
6. Why should price and stock constraints be metadata filters?
7. What does LangGraph add over a single Python function?
8. What information is carried in the graph state?
9. What happens if the Groq API is unavailable?
10. What happens if Hugging Face embeddings are unavailable?
11. Why is the fallback vectorizer not equivalent to MPNet?
12. How would you scale retrieval from 103 products to millions?
13. How would you evaluate retrieval quality?
14. How would you prevent the LLM from inventing product facts?
15. What security changes are needed before public deployment?

## 6. Honest project description

A defensible description is:

"I built a conversational e-commerce recommendation demo using FastAPI and a five-stage LangGraph workflow. It extracts shopping preferences, synthesizes a retrieval query, creates 768-dimensional product/query vectors when the MPNet service is available, ranks a local 103-item catalogue using vector similarity and metadata constraints, and generates a consultative response using an optional Groq LLM. I also implemented fallback paths so the application can demonstrate its workflow without hosted credentials. The current catalogue and in-memory retrieval are demo-scale, not a production live-inventory system."

Only claim that you personally implemented, tested or deployed components you can substantiate.
