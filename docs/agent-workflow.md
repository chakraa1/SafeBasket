# SafeBasket agent workflow

This is the end-to-end flow of the SafeBasket agent. Every node in the
**LangSmith-traced** subgraph is instrumented with `@traceable`, so each run is
observable in LangSmith — including the **free tier**, which uses the deterministic
rule-based engine and never calls an LLM.

```mermaid
flowchart TD
    subgraph client[Client]
      WEB[React website]
      APIUSER[Commercial API consumer]
    end
    WEB -->|HTTP + VITE_API_BASE_URL| ENTRY
    APIUSER -->|X-API-Key| ENTRY

    ENTRY{{Input type}}
    ENTRY -->|Brand / ingredient text| EP1[/POST /api/v1/analyze/]
    ENTRY -->|Ingredient label photo| EP2[/POST /api/v1/analyze-image/]
    ENTRY -->|Shopping-cart screenshot| EP3[/POST /api/v1/analyze-cart/]

    EP2 --> OCR1[Tesseract OCR]
    EP3 --> OCR2[Tesseract OCR + line split]
    OCR2 --> CART[Match each line to product catalogue]

    EP1 --> AGENT
    OCR1 --> AGENT
    CART -->|per item| AGENT

    AGENT[[run_agent]] --> ANALYZE[[analyze_text]]

    ANALYZE --> MATCH[match_harmful_ingredients<br/>curated regulatory KB]
    ANALYZE --> RAG[(FAISS RAG retrieve<br/>regulatory context)]
    MATCH --> SCORE[Safety score + rating]

    SCORE --> COND{carcinogen or<br/>high severity?}
    COND -->|yes| WEBR[web_research<br/>conditional, Tavily]
    COND -->|no| SKIP[skip web research]

    SCORE --> RECO[recommend_alternatives<br/>safer Indian products]

    ANALYZE --> LLMQ{OPENAI_API_KEY set?}
    LLMQ -->|yes| LLM[LLM narrative<br/>ChatOpenAI]
    LLMQ -->|no = free tier| RULES[Rule-based summary]

    LLM --> RESULT
    RULES --> RESULT
    RAG --> RESULT
    WEBR --> RESULT
    SKIP --> RESULT
    RECO --> RESULT
    RESULT[[AnalysisResult JSON<br/>score - flagged - recommendations]] --> OUT[Back to website / API consumer]

    DATA[(Regulatory data sources:<br/>RASFF, FDA CFSAN, FSSAI,<br/>Singapore SFA, HK CFS, IARC/WHO)] -.seeds.-> RAG
    DATA -.seeds.-> MATCH

    subgraph obs[LangSmith observability - all tiers, incl. free]
      AGENT
      ANALYZE
      MATCH
      RAG
      WEBR
      RECO
    end
```

## Traced spans

| Span (`@traceable`)        | Type        | Role |
|----------------------------|-------------|------|
| `safebasket_agent`         | `chain`     | Root run for one analysis request. |
| `analyze`                  | `chain`     | Orchestrates the grounded pipeline. |
| `match_harmful_ingredients`| `tool`      | Matches additives against the knowledge base. |
| `faiss_rag_retrieve`       | `retriever` | FAISS retrieval of regulatory context. |
| `web_research`             | `tool`      | Conditional global recalls/news lookup. |
| `recommend_alternatives`   | `tool`      | Suggests safer Indian products. |

When an OpenAI key is present, the `ChatOpenAI` narrative call is auto-traced by
LangChain and nests under `safebasket_agent` as well.

See `docs/observability.md` for how to turn on LangSmith (free tier).
