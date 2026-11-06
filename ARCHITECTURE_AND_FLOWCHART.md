# ApnaMart AI Sales Associate: System Architecture & Data Flow

```mermaid
graph TD
    User([Customer on apnamarts.shop]) -->|Opens Storefront| Web[ApnaMart Storefront Backdrop]
    User -->|Clicks Floating Icon| Widget[ApnaMart Sahayak Widget (Bottom-Right)]
    Widget -->|Selects Choices| Wizard[Cascading Dropdown Wizard\n1. Category -> 2. Sub -> 3. Type -> 4. Spec -> 5. Size -> 6. Notes]
    
    Wizard -->|POST /api/chat| FastApi[FastAPI Server :8000]
    
    subgraph LangGraph StateGraph Pipeline
        FastApi --> N1[Node 1: extract_intent\nMulti-Category Slot Extraction]
        N1 --> N2[Node 2: synthesize_query\nGroq LPU llama-3.3-70b-versatile]
        N2 --> N3[Node 3: embed_query\nsentence-transformers/all-mpnet-base-v2 (768-D)]
        N3 --> N4[Node 4: retrieve_and_rank\nCosine Similarity Vector Search]
        N4 --> N5[Node 5: generate_pitch\nApnaMart Sahayak Consultative Pitch]
    end
    
    subgraph Scraped Live Database
        Supabase[(apnamarts.shop Supabase DB\n53 Products + 768-D Vectors)]
        Supabase -->|Catalog Vectors| N4
    end

    N5 -->|JSON Response| Widget
    Widget -->|Render| Cards[Top-5 Product Cards with Photos, INR Prices, Match % & Live Bag]
```
