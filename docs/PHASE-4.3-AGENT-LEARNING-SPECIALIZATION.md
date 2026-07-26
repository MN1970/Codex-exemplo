# PHASE 4.3 — Agent Learning & Specialization
## Comprehensive Specification for Feedback-Driven Fine-Tuning, Autonomy Guardrails & Knowledge Distillation

**Version:** 1.0 (Ready for Phase 4.3 Implementation)  
**Status:** Specification Complete | Implementation Pending (Q3 2028)  
**Owner:** Maestro Team (Learning & Specialization Workstream)  
**Last Updated:** 2026-07-26  
**Document ID:** PK_MN_4.3.0  

---

## Executive Summary

Phase 4.3 transforms Manta's agent ecosystem from stateless query-response systems into **learning, adaptive specializations** capable of continuous knowledge acquisition while maintaining strict human-in-the-loop governance. This specification defines:

1. **Feedback-driven fine-tuning pipeline** — Automated curation, labeling, and iterative model refinement
2. **Embedding evolution** — Real-time vector space updates for semantic drift detection
3. **Sub-agent specialization** — Domain-specific spins (barragens-cfrd, energia-hvdc, etc.)
4. **Autonomy guardrails** — Three-tier human approval: confidence gates, anomaly detection, human-in-the-loop
5. **Explainability framework** — Citation-aware responses, source attribution, working-memory traces
6. **Knowledge distillation** — Efficient smaller models (Haiku-tier) from Opus fine-tunes
7. **Continuous integration** — Daily knowledge refresh from regulatory webhooks, feedback, and RAG
8. **Certification & validation** — Automated skill testing, domain coverage metrics, regression testing
9. **Versioning & rollback** — Git-backed agent state, A/B testing infrastructure, instant rollback

This phase moves Manta toward **adaptive intelligence** — agents that improve their domain expertise through structured feedback loops while remaining fully auditable and governable for regulated infrastructure projects.

**Timeline:** Q3–Q4 2028 (12 months)  
**Cost Estimate:** €450K–€650K (infrastructure + training + tooling)  
**Success Criteria:** ≥4 specialized agents live, feedback loop integration ≥95%, certification pass rate ≥90%, zero unplanned agent behaviors

---

## 1. Architecture Overview

### 1.1 High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AGENT LEARNING ECOSYSTEM                          │
└─────────────────────────────────────────────────────────────────────────┘

                                 RAG Feedback Loop
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
            ┌───────▼────────┐  ┌──────▼────────┐  ┌─────▼──────────┐
            │  Regulatory    │  │  User Feedback│  │  Conversation  │
            │  Webhooks      │  │  (Cowork)     │  │  Embeddings    │
            │  (6h polling)  │  │               │  │  (pgvector)    │
            └───────┬────────┘  └──────┬────────┘  └─────┬──────────┘
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       │
                         ┌─────────────▼──────────────┐
                         │  FEEDBACK CURATION LAYER   │
                         │  • Normalize + deduplicate │
                         │  • Confidence scoring      │
                         │  • Anomaly detection       │
                         │  • Source attribution      │
                         └─────────────┬──────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
   ┌─────────────┐            ┌──────────────────┐         ┌──────────────┐
   │ CONFIDENCE  │            │  ANOMALY CHECK   │         │  HUMAN-GATE  │
   │ THRESHOLDS  │            │  (pgvector +     │         │  (Maestro    │
   │             │            │   drift scoring) │         │   Review)    │
   │ • >90% auto │            │                  │         │              │
   │ • 70-90%    │            │  • Entropy check │         │  • Routing   │
   │   manual    │            │  • Vector drift  │         │    conflict  │
   │ • <70%      │            │  • Hallucin-     │         │  • Multi-    │
   │   reject    │            │    ation flag    │         │    agent     │
   └─────────────┘            └──────────────────┘         │    dispatch  │
        │                             │                    └──────────────┘
        │                             │                           │
        └─────────────────────────────┼───────────────────────────┘
                                      │
                      ┌───────────────▼────────────────┐
                      │  FINE-TUNING PIPELINE          │
                      │  • Batch curation (weekly)     │
                      │  • Training data selection     │
                      │  • Contrastive learning        │
                      │  • Loss function optimization  │
                      └───────────────┬────────────────┘
                                      │
        ┌─────────────────────────────┼────────────────────────────┐
        │                             │                            │
        ▼                             ▼                            ▼
   ┌─────────────────┐      ┌──────────────────┐      ┌──────────────┐
   │ FINE-TUNING     │      │  EMBEDDING       │      │ KNOWLEDGE    │
   │ SPECIALISTS     │      │  EVOLUTION       │      │ DISTILLATION │
   │                 │      │                  │      │              │
   │ • barragens-    │      │ • Monthly        │      │ • Opus→      │
   │   cfrd-expert   │      │   pgvector       │      │   Sonnet     │
   │ • energia-hvdc  │      │   recompute      │      │ • Sonnet→    │
   │   optimizer     │      │ • Drift scoring  │      │   Haiku      │
   │ • saneamento-   │      │ • Top-k drift    │      │ • LoRA       │
   │   etq-systems   │      │   alerts         │      │   export     │
   │                 │      │                  │      │              │
   └────────┬────────┘      └──────┬───────────┘      └────────┬─────┘
            │                      │                          │
            └──────────────────────┼──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   CERTIFICATION FRAMEWORK   │
                    │   • Domain coverage         │
                    │   • Regression tests        │
                    │   • Source attribution      │
                    │   • Hallucination scoring   │
                    │   • Live validation         │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   VERSIONING & REGISTRY     │
                    │   • Git-backed state        │
                    │   • Semantic versioning     │
                    │   • A/B testing harness     │
                    │   • Instant rollback        │
                    │   • Change provenance       │
                    └─────────────────────────────┘
```

### 1.2 Core Components

| Component | Purpose | Input | Output | Cadence |
|-----------|---------|-------|--------|---------|
| **Feedback Curation Layer** | Normalize, deduplicate, score feedback | Raw feedback (Cowork, webhooks, conversations) | Scored, labeled feedback bundles | Real-time, batch hourly |
| **Confidence Gating System** | Route feedback based on confidence & anomaly flags | Curated feedback + vector metrics | Approval decision (auto/manual/reject) | Real-time |
| **Fine-Tuning Pipeline** | Generate specialized agent versions | Approved feedback + base models | Specialist agents + LoRA adapters | Weekly |
| **Embedding Evolution Engine** | Track semantic drift in response quality | Feedback embeddings + conversation logs | Vector refreshes + drift alerts | Monthly |
| **Knowledge Distillation Engine** | Compress large models to efficient tiers | Opus fine-tunes + task-specific data | Sonnet/Haiku LoRA exports | Quarterly |
| **Certification Framework** | Validate agent quality before deployment | Specialist agents + test suite | Pass/fail per domain + metrics | Per release |
| **Versioning & Registry** | Track all agent iterations, enable rollback | Certified agents + Git state | Semantic version tags + rollback scripts | Per certification |
| **Explainability Layer** | Cite sources, show working, trace decisions | Agent reasoning + RAG retrievals + feedback | Annotated responses + citation metadata | Per response |

---

## 2. Feedback-Driven Fine-Tuning Pipeline

### 2.1 Feedback Collection & Normalization

#### 2.1.1 Feedback Sources

**Primary sources:**
- **Cowork feedback button** (Phase 2.1) — User thumbs up/down + text comment
- **Regulatory webhooks** (Phase 3.2) — ANEEL, ANTAQ, ANA, ANAC regulatory text changes
- **Conversation logs** (Phase 3.3) — Implicit feedback via session duration, follow-up questions, corrections
- **A/B testing results** (Phase 4.2) — Win/loss metrics from BI dashboards
- **Manual agent annotations** (human-in-the-loop) — Maestro team review corrections
- **Third-party partner feedback** (Phase 4.1) — API partner satisfaction scores

#### 2.1.2 Feedback Normalization Pipeline

```python
# Pseudo-code: Feedback normalization (feedback_curator.py)

class FeedbackCurator:
    def normalize_feedback(raw_feedback) -> NormalizedFeedback:
        """
        Input: Raw feedback from any source (Cowork, webhook, logs)
        Output: Standardized feedback with metadata
        """
        # 1. Deduplication: hash(content + agent + timestamp) against last 7 days
        if is_duplicate(raw_feedback, window=7*24*3600):
            return None
        
        # 2. Tokenization: Extract query, response, feedback sentiment
        query_tokens = tokenize(raw_feedback.original_query)
        response_tokens = tokenize(raw_feedback.agent_response)
        sentiment = classify_sentiment(raw_feedback.comment)  # pos/neg/neutral
        
        # 3. Source attribution: Track origin, timestamp, user_id (anonymized)
        source_metadata = {
            'source': raw_feedback.source,  # 'cowork' | 'webhook' | 'logs' | 'annotation'
            'timestamp': raw_feedback.timestamp,
            'user_hash': hash(raw_feedback.user_id),  # GDPR-compliant anonymization
            'project_id': raw_feedback.project_id,  # For cross-project learning
        }
        
        # 4. Confidence scoring (see Section 2.2)
        confidence_score = compute_confidence(
            sentiment=sentiment,
            comment_length=len(raw_feedback.comment),
            user_history=user_feedback_pattern(raw_feedback.user_id),
            source_reliability=source_metadata['source']
        )
        
        # 5. Anomaly detection: Check for contradictions
        anomaly_flags = detect_anomalies(
            raw_feedback,
            historical_feedback_for_agent,
            pgvector_embeddings
        )
        
        return NormalizedFeedback(
            query_tokens=query_tokens,
            response_tokens=response_tokens,
            sentiment=sentiment,
            comment=raw_feedback.comment,
            confidence_score=confidence_score,
            anomaly_flags=anomaly_flags,
            source_metadata=source_metadata,
            timestamp=raw_feedback.timestamp,
            agent_id=raw_feedback.agent_id,
            feedback_id=uuid4(),
        )
```

#### 2.1.3 Confidence Scoring Algorithm

**Formula:**
```
confidence_score = (
    0.3 * sentiment_reliability +
    0.25 * comment_informativeness +
    0.25 * user_credibility +
    0.2 * source_reliability
)

Where:
- sentiment_reliability = [0, 1]
  - Positive sentiment with detailed comment: 0.9
  - Negative sentiment with detailed comment: 0.85
  - Neutral sentiment or vague comment: 0.5
  
- comment_informativeness = [0, 1]
  - >100 characters + specific examples: 1.0
  - 20-100 characters + vague: 0.6
  - <20 characters: 0.2
  
- user_credibility = [0, 1]
  - Expert user (domain verified): 0.95
  - Regular user (10+ feedbacks, 80% consistent): 0.8
  - New user: 0.5
  
- source_reliability = [0, 1]
  - Regulatory webhooks (ANEEL, etc.): 1.0
  - Manual annotation (Maestro team): 0.95
  - Cowork button + comment: 0.75
  - Conversation logs (implicit): 0.6
```

**Thresholds for routing:**
- **score ≥ 0.90:** Auto-approve for fine-tuning (no human review)
- **0.70 ≤ score < 0.90:** Manual review gate (Maestro team)
- **score < 0.70:** Reject or archive for future analysis

### 2.2 Confidence Gating & Anomaly Detection

#### 2.2.1 Multi-Layer Confidence Gate

```
Layer 1: Confidence Score Threshold
├─ HIGH (≥0.90) → Auto-approve
├─ MEDIUM (0.70–0.90) → Manual review queue
└─ LOW (<0.70) → Archive

Layer 2: Anomaly Detection
├─ Vector Drift Check (pgvector cosine similarity)
│  └─ If new feedback embedding differs >0.3 from historical avg
│     → Flag as "semantic shift" for manual review
├─ Hallucination Detection (aluci-guard integration)
│  └─ If agent response contradicts known facts in RAG
│     → Flag as "hallucination risk" → manual review
├─ Entropy Check
│  └─ If feedback sentiment contradicts majority (>2σ from mean)
│     → Flag as "outlier" → manual review
└─ Cross-Agent Conflict
   └─ If feedback suggests different agent should have handled query
      → Flag as "routing conflict" → human gate

Layer 3: Human-in-the-Loop Gate
├─ Maestro Review Queue (async Slack notification)
│  └─ Reviewer: Approve | Reject | Request clarification
├─ SLA: 24-hour review window
├─ Escalation: If >100 items pending, notify team lead
└─ Audit Trail: All approvals logged with reviewer comments
```

#### 2.2.2 Anomaly Detection Algorithms

**Vector Drift Detection (pgvector):**
```sql
-- Query: Detect semantic drift in feedback
SELECT 
    f.feedback_id,
    f.embedding,
    AVG(h.embedding <-> f.embedding) as historical_distance,
    CASE 
        WHEN AVG(h.embedding <-> f.embedding) > 0.3 
        THEN 'DRIFT_ALERT'
        ELSE 'NORMAL'
    END as anomaly_flag
FROM feedback f
JOIN historical_feedback h 
    ON h.agent_id = f.agent_id 
    AND h.timestamp > NOW() - INTERVAL '30 days'
GROUP BY f.feedback_id, f.embedding
HAVING AVG(h.embedding <-> f.embedding) > 0.25;
```

**Hallucination Detection (aluci-guard):**
```python
class HallucinationDetector:
    def check_hallucination_risk(agent_response, rag_retrieval, ner_entities):
        """
        Cross-check agent response against RAG knowledge base
        """
        # 1. NER: Extract named entities from response
        entities = ner_model.predict(agent_response)
        
        # 2. For each entity, verify against RAG
        hallucination_flags = []
        for entity in entities:
            rag_results = rag_search(entity, top_k=5)
            if not rag_results:
                # Entity not in knowledge base
                hallucination_flags.append({
                    'entity': entity,
                    'risk': 'UNKNOWN_ENTITY',
                    'confidence': 0.7,
                })
            else:
                # Check semantic consistency
                response_context = extract_context(agent_response, entity)
                for rag_doc in rag_results:
                    consistency_score = semantic_similarity(response_context, rag_doc)
                    if consistency_score < 0.6:
                        hallucination_flags.append({
                            'entity': entity,
                            'risk': 'INCONSISTENT_WITH_RAG',
                            'consistency_score': consistency_score,
                            'rag_source': rag_doc['source'],
                        })
        
        return {
            'hallucination_risk': len(hallucination_flags) > 0,
            'flags': hallucination_flags,
            'recommendation': 'MANUAL_REVIEW' if hallucination_flags else 'AUTO_APPROVE',
        }
```

**Entropy Check (Statistical Outlier Detection):**
```python
def entropy_check(feedback_sentiment, agent_id, window_days=30):
    """
    Detect if feedback sentiment is statistical outlier
    """
    historical_sentiments = get_feedback_sentiments(agent_id, window_days)
    mean_sentiment = np.mean(historical_sentiments)
    std_sentiment = np.std(historical_sentiments)
    
    z_score = abs((feedback_sentiment - mean_sentiment) / std_sentiment)
    
    if z_score > 2.0:  # >2σ = 95% confidence outlier
        return {
            'is_outlier': True,
            'z_score': z_score,
            'recommendation': 'MANUAL_REVIEW',
            'reason': f'Sentiment {feedback_sentiment} is {z_score:.1f}σ from mean'
        }
    else:
        return {
            'is_outlier': False,
            'z_score': z_score,
            'recommendation': 'AUTO_APPROVE',
        }
```

### 2.3 Fine-Tuning Specialist Agents

#### 2.3.1 Specialist Agent Taxonomy

Four categories of specialized agents based on feedback patterns:

**Category 1: Domain Specialization (S-tier agents)**
- **barragens-cfrd-expert** — Concrete Face Rockfill Dam specialist
  - Triggers: Feedback mentioning "CFRD", "concrete face", "embankment", "rockfill"
  - Knowledge: ICOLD guidelines, geotechnical stability, TSF design
  - Scope: Barragens (Manta 03-S10) sub-specialist
  
- **energia-hvdc-optimizer** — HVDC transmission specialist
  - Triggers: Feedback mentioning "HVDC", "DC transmission", "converter station"
  - Knowledge: IEEE 2118, ABB/Siemens HVDC design, commutation angle
  - Scope: Energia (Manta 03-S9) sub-specialist
  
- **saneamento-etq-systems** — ETE+ETA+ETQ integrated systems
  - Triggers: Feedback mentioning "ETE", "ETA", "integrated", "treatment trains"
  - Knowledge: NBR 12211-12218, AySA editais, advanced treatment (MBR, RO)
  - Scope: Saneamento (Manta 03-S8) sub-specialist

**Category 2: Process Specialization (Workflow agents)**
- **licitacao-analyzer** — Competitive bidding & tender document analysis
  - Triggers: Feedback mentioning "edital", "licitação", "bidding", "procurement"
  - Knowledge: Brazilian Federal Bidding Law (Lei 14.133), TCESP standards
  - Scope: Transversal (Phase 3.1 API partners)

- **due-diligence-validator** — M&A technical assessment
  - Triggers: Feedback mentioning "due diligence", "M&A", "asset quality"
  - Knowledge: IACCM standards, technical risk modeling, valuation frameworks
  - Scope: Advisory (Manta 15) sub-specialist

**Category 3: Regulatory Specialization (Compliance agents)**
- **aneel-compliance-checker** — ANEEL regulatory alignment
  - Triggers: Feedback mentioning "ANEEL", "RAP", "regulatory", "compliance"
  - Knowledge: ANEEL Resolution 786/2020, RAP template updates, leilão procedures
  - Scope: Energia (S9) with real-time webhook integration

- **antaq-maritime-inspector** — ANTAQ port regulations
  - Triggers: Feedback mentioning "ANTAQ", "port", "maritime", "terminal"
  - Knowledge: ANTAQ Resolution 30, PIANC guidelines, dredging permits
  - Scope: Portos (S6) with real-time webhook integration

#### 2.3.2 Fine-Tuning Data Selection

**Weekly fine-tuning cycle:**

```python
class FinetuningDataSelector:
    def select_training_data(specialist_agent_id, confidence_threshold=0.8):
        """
        Curate training data for weekly fine-tuning specialist run
        """
        # 1. Fetch approved feedback from last 7 days
        recent_feedback = query_feedback(
            agent_id=specialist_agent_id,
            time_range='last_7_days',
            confidence_score__gte=confidence_threshold,
            status='APPROVED'
        )
        
        # 2. Balance dataset: Positive:Negative = 1:1 (avoid class imbalance)
        positive_feedback = [f for f in recent_feedback if f.sentiment == 'POSITIVE']
        negative_feedback = [f for f in recent_feedback if f.sentiment == 'NEGATIVE']
        neutral_feedback = [f for f in recent_feedback if f.sentiment == 'NEUTRAL']
        
        min_class_size = min(len(positive_feedback), len(negative_feedback))
        balanced_feedback = (
            positive_feedback[:min_class_size] +
            negative_feedback[:min_class_size] +
            neutral_feedback[:int(min_class_size * 0.3)]  # 30% neutral
        )
        
        # 3. Format for training: {query, response, feedback, label}
        training_examples = []
        for f in balanced_feedback:
            training_examples.append({
                'query': f.original_query,
                'reference_response': f.agent_response,
                'feedback': f.comment,
                'label': f.sentiment,  # POSITIVE | NEGATIVE | NEUTRAL
                'source': f.source_metadata['source'],
                'timestamp': f.timestamp,
            })
        
        # 4. Cross-validate: Use 80/10/10 split
        n_total = len(training_examples)
        train_set = training_examples[:int(0.8*n_total)]
        val_set = training_examples[int(0.8*n_total):int(0.9*n_total)]
        test_set = training_examples[int(0.9*n_total):]
        
        return {
            'train': train_set,
            'val': val_set,
            'test': test_set,
            'metadata': {
                'total_examples': n_total,
                'positive_ratio': len(positive_feedback) / n_total,
                'negative_ratio': len(negative_feedback) / n_total,
                'data_selection_method': 'stratified_balanced',
                'selected_at': datetime.now(),
            }
        }
```

#### 2.3.3 Contrastive Learning for Fine-Tuning

Instead of simple supervised learning, use **contrastive learning** to improve agent responses while maintaining consistency:

```python
class ContrastiveFinetuner:
    def finetune_specialist_agent(specialist_agent_id, training_data):
        """
        Contrastive learning: Learn from positive/negative examples
        """
        # 1. Prepare triplets: (query, positive_response, negative_response)
        triplets = []
        for feedback in training_data:
            triplet = {
                'query': feedback['query'],
                'positive_response': feedback['reference_response'] 
                                     if feedback['sentiment'] == 'POSITIVE'
                                     else feedback['reference_response'],
                'negative_response': [f for f in training_data 
                                    if f['label'] == 'NEGATIVE' 
                                    and f['query'] == feedback['query']][0],
            }
            triplets.append(triplet)
        
        # 2. Embedding-level loss: Bring positive closer, push negative away
        #    Loss = max(0, margin + d(query, negative) - d(query, positive))
        model = load_model(specialist_agent_id)
        
        for epoch in range(num_epochs):
            for triplet in triplets:
                query_emb = model.encode(triplet['query'])
                pos_emb = model.encode(triplet['positive_response'])
                neg_emb = model.encode(triplet['negative_response'])
                
                # Contrastive loss (triplet loss)
                margin = 0.5
                pos_distance = euclidean_distance(query_emb, pos_emb)
                neg_distance = euclidean_distance(query_emb, neg_emb)
                loss = max(0, margin + pos_distance - neg_distance)
                
                model.backward(loss)
                optimizer.step()
        
        # 3. Save fine-tuned model + LoRA adapter
        model.save(f'models/specialists/{specialist_agent_id}/v_{version_number}')
        lora_adapter.export(f'models/specialists/{specialist_agent_id}/lora_v_{version_number}.safetensors')
        
        return {
            'specialist_id': specialist_agent_id,
            'version': version_number,
            'training_loss': avg_loss,
            'validation_accuracy': compute_accuracy(model, training_data['val']),
            'deployed_at': datetime.now(),
        }
```

---

## 3. Embedding Evolution & Vector Space Management

### 3.1 Monthly Embedding Recompute

Every month, recompute pgvector embeddings for all feedback and conversations to track semantic drift:

```python
class EmbeddingEvolutionEngine:
    def monthly_embedding_refresh(month_year):
        """
        Recompute embeddings for all feedback and conversations
        Detect semantic drift, topic shifts, new domains
        """
        # 1. Fetch all feedback + conversation logs for the month
        all_feedback = query_feedback(
            timestamp__gte=start_of_month(month_year),
            timestamp__lt=end_of_month(month_year),
        )
        all_conversations = query_conversations(
            created_at__gte=start_of_month(month_year),
            created_at__lt=end_of_month(month_year),
        )
        
        # 2. Recompute embeddings using latest Anthropic embedding model
        #    (e.g., claude-embed-v3, 1536-dimensional)
        batch_size = 500
        embeddings = []
        for batch in chunks(all_feedback + all_conversations, batch_size):
            batch_embeddings = embedding_model.encode(
                texts=[item.text for item in batch],
                model='claude-embed-v3',
                embedding_dim=1536,
            )
            embeddings.extend(batch_embeddings)
        
        # 3. Compute drift metrics for each agent
        #    Drift = avg cosine distance from previous month's embeddings
        for agent_id in all_agents():
            this_month_embeddings = [e for e, f in zip(embeddings, all_feedback) 
                                    if f.agent_id == agent_id]
            prev_month_embeddings = load_embeddings(agent_id, previous_month)
            
            if prev_month_embeddings:
                drift_scores = []
                for curr_emb in this_month_embeddings:
                    min_distance = min([cosine_distance(curr_emb, prev) 
                                      for prev in prev_month_embeddings])
                    drift_scores.append(min_distance)
                
                avg_drift = np.mean(drift_scores)
                
                if avg_drift > 0.25:  # Significant drift threshold
                    alert = {
                        'agent_id': agent_id,
                        'drift_score': avg_drift,
                        'alert_level': 'HIGH' if avg_drift > 0.35 else 'MEDIUM',
                        'recommendation': 'Review specialist performance, check for model degradation',
                        'timestamp': datetime.now(),
                    }
                    notify_maestro_team(alert)
        
        # 4. Store refreshed embeddings in pgvector
        store_embeddings_pgvector(all_feedback, embeddings, month_year)
        
        return {
            'month': month_year,
            'total_items_recomputed': len(all_feedback) + len(all_conversations),
            'agents_with_high_drift': sum(1 for a in all_agents() if drift_scores[a] > 0.25),
            'refresh_completed_at': datetime.now(),
        }
```

### 3.2 Semantic Drift Alerts & Thresholds

| Drift Score | Interpretation | Action |
|-------------|-----------------|--------|
| 0.10–0.15 | **Normal** | Continue monitoring |
| 0.15–0.25 | **Moderate** | Weekly review by Maestro team |
| 0.25–0.35 | **High** | Manual specialist retraining recommended |
| >0.35 | **Critical** | Rollback to previous version, audit cause |

### 3.3 Topic Modeling for Emerging Domains

Use **LDA (Latent Dirichlet Allocation)** on monthly feedback to discover emerging topics:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

class TopicDetector:
    def detect_emerging_topics(feedback_texts, n_topics=10):
        """
        Detect emerging knowledge domains from feedback
        """
        # 1. TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=500,
            min_df=5,
            max_df=0.8,
        )
        tfidf_matrix = vectorizer.fit_transform(feedback_texts)
        
        # 2. LDA topic modeling
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20,
        )
        lda_output = lda.fit_transform(tfidf_matrix)
        
        # 3. Extract top terms for each topic
        topics = {}
        for topic_idx, topic_terms in enumerate(lda.components_):
            top_indices = topic_terms.argsort()[-5:][::-1]
            top_words = [vectorizer.get_feature_names_out()[i] for i in top_indices]
            topics[f'topic_{topic_idx}'] = {
                'words': top_words,
                'coherence': compute_coherence(topic_terms),
                'prevalence': lda_output[:, topic_idx].mean(),
            }
        
        # 4. Identify NEW topics (not in previous month)
        previous_topics = load_topics_from_last_month()
        new_topics = [t for t in topics.keys() 
                     if not any(topic_similarity(t, pt) > 0.8 for pt in previous_topics)]
        
        return {
            'all_topics': topics,
            'new_topics': new_topics,
            'recommendation': 'Consider creating new specialist agents for new topics',
            'detected_at': datetime.now(),
        }
```

---

## 4. Sub-Agent Specialization Framework

### 4.1 Specialization Tree & Inheritance

```
Manta 03 (Infrastructure Agent - Base)
├── Manta 03-S1 (Roads) [Base: Sonnet]
│   ├── s1-pavimento-expert (Asphalt specialist)
│   ├── s1-terraplenagem-expert (Earthwork specialist)
│   └── s1-drenagem-expert (Drainage specialist)
│
├── Manta 03-S2 (OAE/Bridges) [Base: Sonnet]
│   ├── s2-ponte-concreto-expert (Concrete bridge specialist)
│   ├── s2-ponte-aco-expert (Steel bridge specialist)
│   └── s2-fundacao-expert (Foundation specialist)
│
├── Manta 03-S8 (Wastewater) [Base: Sonnet]
│   ├── s8-ete-convencional-expert (Conventional WWT)
│   ├── s8-ete-lagoas-expert (Lagoon WWT)
│   ├── s8-etq-avancado-expert (Advanced treatment: MBR, RO, UV)
│   └── s8-eta-coleta-expert (Water distribution & collection)
│
├── Manta 03-S9 (Energy) [Base: Sonnet]
│   ├── s9-linhas-transmissao-expert (AC transmission)
│   ├── s9-hvdc-expert (HVDC specialist)
│   ├── s9-distribuicao-expert (Distribution networks)
│   └── s9-subestacao-expert (Substation design)
│
└── Manta 03-S10 (Dams) [Base: Sonnet]
    ├── s10-cfrd-expert (Concrete Face Rockfill)
    ├── s10-ccr-expert (Roller Compacted Concrete)
    ├── s10-terra-expert (Embankment/earthfill)
    └── s10-geotecnia-expert (Geotechnical specialist)
```

### 4.2 Specialization Data Requirements

Each specialist agent requires:

| Requirement | Definition | Example (barragens-cfrd) |
|-------------|-----------|-------------------------|
| **Base Model** | Parent agent model + LoRA adapter | Sonnet + s10-cfrd-lora.safetensors |
| **Domain Knowledge** | RAG collection specific to domain | RAG collection: `bar:cfrd:*` (80+ chunks on CFRD design) |
| **Prompt Template** | System prompt with domain context | "You are a CFRD dam specialist. Focus on concrete face design, drainage, seepage..." |
| **Training Examples** | ≥200 approved feedback examples | 200+ CFRDs-specific feedback triplets |
| **Test Suite** | Domain-specific validation cases | 50 CFRD design questions + reference answers |
| **Decision Rules** | Routing rules that trigger this specialist | "IF query mentions 'CFRD' OR 'concrete face' → use barragens-cfrd-expert" |

### 4.3 Specialist Agent Initialization

```python
class SpecialistAgentFactory:
    def create_specialist_agent(
        parent_agent_id: str,
        specialist_name: str,
        domain_keywords: List[str],
        rag_collection_prefix: str,
        training_feedback: List[Dict],
    ) -> SpecialistAgent:
        """
        Create new specialist agent variant
        """
        # 1. Load base model
        base_model = load_model(parent_agent_id)
        
        # 2. Create LoRA adapter (Low-Rank Adaptation)
        #    Efficient fine-tuning: only update ~1% of parameters
        lora_config = LoraConfig(
            r=16,  # LoRA rank
            lora_alpha=32,
            target_modules=['q_proj', 'v_proj'],  # Attention weights
            lora_dropout=0.1,
            bias='none',
        )
        lora_model = get_peft_model(base_model, lora_config)
        
        # 3. Fine-tune on domain-specific feedback
        finetune_specialist_agent(
            model=lora_model,
            training_data=training_feedback,
            epochs=3,
            batch_size=32,
            learning_rate=1e-4,
        )
        
        # 4. Create specialist configuration
        specialist_config = {
            'specialist_id': f'{parent_agent_id}-{specialist_name}',
            'parent_agent': parent_agent_id,
            'name': specialist_name,
            'domain_keywords': domain_keywords,
            'rag_prefix': rag_collection_prefix,
            'model_path': f'models/specialists/{specialist_name}/model.safetensors',
            'lora_path': f'models/specialists/{specialist_name}/lora.safetensors',
            'system_prompt': generate_specialist_prompt(specialist_name, domain_keywords),
            'version': '1.0.0',
            'created_at': datetime.now(),
            'status': 'INITIALIZED',
        }
        
        # 5. Register specialist
        register_specialist_agent(specialist_config)
        
        return SpecialistAgent(specialist_config)
```

---

## 5. Autonomy Guardrails & Human-in-the-Loop

### 5.1 Three-Tier Autonomy Model

```
┌─────────────────────────────────────────────────────────┐
│              AUTONOMY GUARDRAILS FRAMEWORK               │
└─────────────────────────────────────────────────────────┘

TIER 1: FULL AUTONOMY (Confidence ≥ 0.95)
├─ Auto-apply feedback to fine-tuning
├─ Deploy specialist variant immediately (no review)
├─ Update vector store + LoRA weights
├─ Conditions:
│  • Confidence score ≥ 0.95
│  • No anomaly flags
│  • No hallucination risk
│  • Consistent with historical patterns
└─ Guardrail: Rate limit to ≤10 auto-deploys per day

TIER 2: SUPERVISED AUTONOMY (0.85 ≤ Confidence < 0.95)
├─ Queue feedback for Maestro review
├─ Deploy with Maestro approval within 24h
├─ Requester: Automation (email notification sent)
├─ Conditions:
│  • Confidence 0.85–0.95
│  • Minor anomaly flags (non-critical)
│  • Awaits human sign-off
└─ SLA: 24-hour review window

TIER 3: HUMAN-DOMINANT (Confidence < 0.85)
├─ Require manual Maestro review + annotation
├─ High-confidence feedback only → curated dataset
├─ Deploy only with explicit approval
├─ Conditions:
│  • Confidence <0.85
│  • Major anomaly flags
│  • Potential hallucination
│  • Routing conflicts
└─ Escalation: If >20 pending, notify team lead

OVERRIDE RULES:
├─ Maestro team can override any tier
├─ Executive approval required for emergency deploy
├─ All overrides logged with timestamp + justification
└─ Monthly audit of overrides + pattern analysis
```

### 5.2 Human-in-the-Loop Review Interface

**Slack-based review workflow (async, low-friction):**

```python
class MaestroReviewQueue:
    def notify_review_needed(feedback_id, confidence_score, anomaly_flags):
        """
        Send Slack notification to Maestro team for review
        """
        slack_message = {
            'channel': '#manta-learning-reviews',
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*Agent Learning Feedback Requires Review*\n'
                               f'Feedback ID: {feedback_id}\n'
                               f'Confidence: {confidence_score:.2%}\n'
                               f'Status: {get_status(confidence_score)}'
                    }
                },
                {
                    'type': 'section',
                    'fields': [
                        {
                            'type': 'mrkdwn',
                            'text': f'*Query*\n{get_query(feedback_id)[:200]}...'
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f'*Feedback*\n{get_feedback(feedback_id)[:200]}...'
                        }
                    ]
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*Anomaly Flags*\n{format_flags(anomaly_flags)}'
                    }
                },
                {
                    'type': 'actions',
                    'elements': [
                        {
                            'type': 'button',
                            'text': {'type': 'plain_text', 'text': 'Approve'},
                            'value': f'approve_{feedback_id}',
                            'action_id': 'approve_feedback',
                            'style': 'primary',
                        },
                        {
                            'type': 'button',
                            'text': {'type': 'plain_text', 'text': 'Reject'},
                            'value': f'reject_{feedback_id}',
                            'action_id': 'reject_feedback',
                            'style': 'danger',
                        },
                        {
                            'type': 'button',
                            'text': {'type': 'plain_text', 'text': 'Request Clarification'},
                            'value': f'clarify_{feedback_id}',
                            'action_id': 'clarify_feedback',
                        }
                    ]
                },
                {
                    'type': 'context',
                    'elements': [
                        {
                            'type': 'mrkdwn',
                            'text': f'SLA: Review by {calculate_sla_deadline(confidence_score).isoformat()}'
                        }
                    ]
                }
            ]
        }
        
        send_slack_message(slack_message)
        log_audit_trail({
            'feedback_id': feedback_id,
            'review_requested_at': datetime.now(),
            'confidence_score': confidence_score,
            'anomaly_flags': anomaly_flags,
        })

    def handle_review_action(action: str, feedback_id: str, reviewer_id: str):
        """
        Process reviewer action (Approve/Reject/Clarify)
        """
        if action == 'approve':
            # Mark as approved, queue for fine-tuning
            update_feedback_status(feedback_id, 'APPROVED', reviewer_id)
            add_to_finetuning_queue(feedback_id)
            notify_requester(feedback_id, 'APPROVED')
            
        elif action == 'reject':
            # Archive feedback, send requester notification
            update_feedback_status(feedback_id, 'REJECTED', reviewer_id)
            notify_requester(feedback_id, 'REJECTED')
            
        elif action == 'clarify':
            # Request additional info from feedback source
            update_feedback_status(feedback_id, 'AWAITING_CLARIFICATION', reviewer_id)
            notify_feedback_source(feedback_id, 'Please provide more details...')
```

### 5.3 Anomaly Escalation Playbook

| Anomaly Type | Severity | Action | Escalation |
|--------------|----------|--------|------------|
| Vector Drift (>0.3) | HIGH | Block until manual review | Maestro lead |
| Hallucination Flag | HIGH | Block fine-tuning, audit RAG | Data team + Maestro |
| Entropy Outlier (>2σ) | MEDIUM | Manual review (24h SLA) | Maestro team |
| Cross-Agent Conflict | MEDIUM | Routing review, may require Manta 17 orchestrator update | Maestro + routing team |
| Unknown Entity | LOW | Log, analyze trend over month | Archive until trend confirmed |

---

## 6. Explainability Framework & Citation

### 6.1 Response Attribution Model

Every agent response includes:

```python
class AnnotatedResponse:
    def __init__(self, response_text: str):
        self.response_text = response_text
        self.citations = []  # List[Citation]
        self.reasoning_trace = []  # List[ReasoningStep]
        self.confidence_score = None  # float [0, 1]
        self.source_documents = []  # List[RAGDocument]
        self.feedback_used = []  # List[str] (feedback IDs used to finetune this response)
        self.version_info = {
            'agent_id': None,
            'agent_version': None,
            'specialist_id': None,
            'base_model': None,
            'lora_adapter': None,
        }

class Citation:
    def __init__(
        self,
        text_span: str,  # "concrete face design must..."
        source_type: str,  # 'RAG' | 'FEEDBACK' | 'LEARNED'
        source_id: str,  # RAG document ID or feedback ID
        source_document: str,  # "ICOLD Bulletin 123: CFRD Design"
        confidence: float,  # [0, 1]
        page_number: Optional[int] = None,
        url: Optional[str] = None,
    ):
        self.text_span = text_span
        self.source_type = source_type
        self.source_id = source_id
        self.source_document = source_document
        self.confidence = confidence
        self.page_number = page_number
        self.url = url

class ReasoningStep:
    def __init__(
        self,
        step_number: int,
        action: str,  # "RETRIEVE_RAG" | "ANALYZE" | "APPLY_LEARNED_RULE" | "CONSULT_SPECIALIST"
        input_context: str,
        output: str,
        confidence: float,
    ):
        self.step_number = step_number
        self.action = action
        self.input_context = input_context
        self.output = output
        self.confidence = confidence
```

### 6.2 Citation Generation Algorithm

```python
class CitationGenerator:
    def generate_citations(
        response_text: str,
        rag_retrieval: List[RAGDocument],
        feedback_used: List[str],
        learned_rules: List[Dict],
    ) -> List[Citation]:
        """
        Trace each claim in response back to source
        """
        citations = []
        
        # 1. Sentence-level decomposition
        sentences = sent_tokenize(response_text)
        
        for sentence in sentences:
            # 2. Match sentence to RAG documents (semantic similarity)
            for rag_doc in rag_retrieval:
                similarity = semantic_similarity(sentence, rag_doc.text)
                if similarity > 0.75:  # High confidence match
                    citation = Citation(
                        text_span=sentence,
                        source_type='RAG',
                        source_id=rag_doc.id,
                        source_document=rag_doc.metadata['title'],
                        confidence=similarity,
                        page_number=rag_doc.metadata.get('page_number'),
                        url=rag_doc.metadata.get('url'),
                    )
                    citations.append(citation)
                    break
            
            # 3. Match to learned rules (from fine-tuning)
            for rule in learned_rules:
                if rule['pattern'] in sentence:
                    citation = Citation(
                        text_span=sentence,
                        source_type='LEARNED',
                        source_id=rule['feedback_id'],
                        source_document=f"Learned from feedback: {rule['feedback_id']}",
                        confidence=rule.get('confidence', 0.8),
                    )
                    citations.append(citation)
                    break
        
        return citations

    def format_response_with_citations(
        response_text: str,
        citations: List[Citation],
    ) -> str:
        """
        Format response with inline citation markers
        """
        annotated_response = response_text
        
        for i, citation in enumerate(citations, 1):
            # Add footnote-style citation
            annotated_response = annotated_response.replace(
                citation.text_span,
                f"{citation.text_span}[^{i}]"
            )
        
        # Add footnotes at end
        footnotes = "\n\n---\n\n"
        for i, citation in enumerate(citations, 1):
            if citation.source_type == 'RAG':
                footnotes += f"[^{i}]: **{citation.source_document}** (p. {citation.page_number or 'n/a'})"
            elif citation.source_type == 'LEARNED':
                footnotes += f"[^{i}]: **Learned from feedback** (ID: {citation.source_id}, confidence: {citation.confidence:.1%})"
        
        return annotated_response + footnotes
```

### 6.3 Working Memory Traces (Chain-of-Thought)

```python
class WorkingMemoryTrace:
    def __init__(self, query: str):
        self.query = query
        self.steps = []
        self.final_response = None
        self.reasoning_time_ms = 0

    def log_step(self, step_num: int, action: str, context: str, result: str):
        """
        Log each reasoning step for transparency
        """
        step = ReasoningStep(
            step_number=step_num,
            action=action,
            input_context=context,
            output=result,
            confidence=self._compute_step_confidence(action, result),
        )
        self.steps.append(step)
    
    def render_explanation(self) -> str:
        """
        Human-readable explanation of reasoning
        """
        explanation = f"# How I answered your question\n\n"
        explanation += f"**Your query:** {self.query}\n\n"
        
        for step in self.steps:
            explanation += f"**Step {step.step_number}: {step.action}**\n"
            explanation += f"- Context: {step.input_context[:200]}...\n"
            explanation += f"- Result: {step.output[:200]}...\n"
            explanation += f"- Confidence: {step.confidence:.1%}\n\n"
        
        explanation += f"---\n\n"
        explanation += f"*Processing time: {self.reasoning_time_ms}ms*\n"
        
        return explanation

# Example usage:
working_memory = WorkingMemoryTrace("How should we design CFRD drainage?")

working_memory.log_step(
    1, 'ROUTE_QUERY',
    "Detected keywords: 'CFRD', 'drainage'",
    "Routed to specialist: barragens-cfrd-expert"
)

working_memory.log_step(
    2, 'RETRIEVE_RAG',
    "Domain: barragens, sub-domain: cfrd-drainage",
    "Retrieved 5 documents: ICOLD guidelines, case studies, design manuals"
)

working_memory.log_step(
    3, 'APPLY_SPECIALIST_KNOWLEDGE',
    "Specialist version: v2.3 (trained on 250+ CFRD feedback samples)",
    "Synthesized response drawing on specialist knowledge"
)

print(working_memory.render_explanation())
# Output:
# # How I answered your question
#
# Your query: How should we design CFRD drainage?
#
# Step 1: ROUTE_QUERY
# - Context: Detected keywords: 'CFRD', 'drainage'
# - Result: Routed to specialist: barragens-cfrd-expert
# - Confidence: 98%
#
# Step 2: RETRIEVE_RAG
# - Context: Domain: barragens, sub-domain: cfrd-drainage
# - Result: Retrieved 5 documents: ICOLD guidelines, case studies, design manuals
# - Confidence: 95%
# ...
```

---

## 7. Knowledge Distillation & Model Compression

### 7.1 Distillation Pipeline

Compress fine-tuned Opus/Sonnet agents to efficient Haiku-tier models:

```python
class KnowledgeDistiller:
    def distill_model(
        teacher_model_id: str,  # e.g., 'barragens-cfrd-expert' (Sonnet-tier)
        student_model_name: str = 'barragens-cfrd-expert-haiku',
        temperature: float = 3.0,  # For soft targets
        alpha: float = 0.7,  # Weight for distillation loss
    ):
        """
        Distill Sonnet specialist → Haiku specialist
        """
        # 1. Load models
        teacher_model = load_model(teacher_model_id)  # Sonnet
        student_model = load_model('claude-haiku-4.5')  # Base Haiku
        
        # 2. Prepare distillation dataset
        #    Use same training data that fine-tuned teacher
        distillation_data = load_specialist_training_data(teacher_model_id)
        
        # 3. Generate soft targets from teacher
        soft_targets = []
        for example in distillation_data:
            teacher_output = teacher_model(example['query'], temperature=temperature)
            soft_targets.append(teacher_output)
        
        # 4. Distillation training
        #    Loss = α * KL_divergence(student_logits, teacher_logits) + (1-α) * cross_entropy_loss
        optimizer = AdamW(student_model.parameters(), lr=1e-5)
        
        for epoch in range(num_epochs):
            for batch in batches(distillation_data, batch_size=32):
                student_logits = student_model(batch['query'])
                teacher_logits = [soft_targets[i] for i in batch['indices']]
                
                distillation_loss = compute_kl_divergence(
                    student_logits, teacher_logits, temperature
                )
                task_loss = compute_task_loss(student_logits, batch['labels'])
                
                total_loss = alpha * distillation_loss + (1 - alpha) * task_loss
                total_loss.backward()
                optimizer.step()
        
        # 5. Evaluate distilled model
        distilled_accuracy = evaluate_model(student_model, distillation_data)
        teacher_accuracy = evaluate_model(teacher_model, distillation_data)
        
        performance_ratio = distilled_accuracy / teacher_accuracy
        
        if performance_ratio >= 0.90:  # Retain ≥90% of teacher performance
            # Save distilled model + LoRA
            student_model.save(f'models/specialists/{student_model_name}/v1')
            export_lora_adapter(student_model, f'models/specialists/{student_model_name}/lora_v1.safetensors')
            
            return {
                'status': 'SUCCESS',
                'teacher_model': teacher_model_id,
                'student_model': student_model_name,
                'teacher_accuracy': teacher_accuracy,
                'student_accuracy': distilled_accuracy,
                'performance_retention': performance_ratio,
                'model_size_reduction': f'45%',  # Typical Haiku vs Sonnet
                'cost_per_query_reduction': f'3.5x',  # Haiku costs 1/3.5 of Sonnet
                'inference_latency_reduction': f'40%',  # Faster inference
            }
        else:
            return {
                'status': 'FAILED',
                'reason': f'Distilled model only retained {performance_ratio:.1%} of teacher performance',
                'recommendation': 'Use larger model tier or provide more training data'
            }
```

### 7.2 Model Tier Strategy

| Tier | Model | Use Case | Cost/Query | Latency | Knowledge Distillation |
|------|-------|----------|-----------|---------|------------------------|
| **Base** | Claude Sonnet | Primary specialist agents (4.3 launch) | $0.003 | 400ms | Source for Haiku |
| **Efficient** | Claude Haiku (distilled) | High-volume Q&A, feedback routing | $0.0008 | 200ms | From Sonnet specialists |
| **Expert** | Claude Opus (custom fine-tune) | Complex multi-domain synthesis, tie-breaker | $0.015 | 600ms | (no distillation) |

### 7.3 LoRA Adapter Export for Edge Deployment

```python
class LoraExporter:
    def export_lora_for_deployment(specialist_model_id: str):
        """
        Export LoRA adapter for distributed deployment
        """
        # 1. Extract LoRA weights from fine-tuned model
        model = load_model(specialist_model_id)
        lora_weights = extract_lora_weights(model)
        
        # 2. Quantize to int8 (reduce size 4x)
        quantized_lora = quantize_to_int8(lora_weights)
        
        # 3. Export with metadata
        export_config = {
            'base_model': 'claude-haiku-4.5',
            'specialist_id': specialist_model_id,
            'lora_rank': 16,
            'lora_alpha': 32,
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'training_samples': 250,
            'validation_accuracy': 0.92,
        }
        
        # 4. Save to S3 + local cache
        with open(f'lora_exports/{specialist_model_id}.safetensors', 'wb') as f:
            safetensors.save(quantized_lora, f)
        
        upload_to_s3(f'lora_exports/{specialist_model_id}.safetensors')
        
        return {
            'export_path': f'lora_exports/{specialist_model_id}.safetensors',
            'file_size_kb': os.path.getsize(f'lora_exports/{specialist_model_id}.safetensors') / 1024,
            'base_model_size_mb': 50,  # Haiku model
            'total_deployment_size_mb': 50 + (file_size_kb / 1024),
            'download_url': f's3://manta-lora-exports/{specialist_model_id}.safetensors',
        }
```

---

## 8. Continuous Integration & Daily Knowledge Refresh

### 8.1 Daily Knowledge Integration Pipeline

```python
class DailyKnowledgeRefresh:
    def run_daily_integration_cycle():
        """
        Daily pipeline: Regulatory webhooks → RAG → Specialist agents
        """
        integration_log = {
            'started_at': datetime.now(),
            'sources': [],
            'updates': [],
            'errors': [],
        }
        
        # 1. MORNING (6 AM UTC): Check regulatory webhooks
        integration_log['sources'].append({
            'source': 'regulatory_webhooks',
            'checked_at': datetime.now(),
        })
        
        regulatory_updates = check_regulatory_webhooks()  # ANEEL, ANTAQ, ANA, ANAC
        for update in regulatory_updates:
            # 2. Extract key information
            extracted_text = extract_regulatory_text(update)
            
            # 3. Add to RAG
            rag_doc_id = add_to_rag(
                text=extracted_text,
                collection=determine_collection(update),  # 'ene:' | 'por:' etc
                metadata={
                    'source': 'regulatory_webhook',
                    'agency': update['agency'],
                    'date': update['date'],
                    'url': update['url'],
                }
            )
            
            # 4. Update specialist agent embeddings
            update_specialist_embeddings(rag_doc_id)
            
            integration_log['updates'].append({
                'type': 'REGULATORY',
                'agency': update['agency'],
                'rag_doc_id': rag_doc_id,
                'timestamp': datetime.now(),
            })
        
        # 2. MIDDAY (12 PM UTC): Batch process approved feedback
        pending_feedback = get_approved_feedback_since_last_cycle()
        
        for specialist_agent_id in get_all_specialists():
            feedback_for_agent = [f for f in pending_feedback 
                                 if should_finetune(f, specialist_agent_id)]
            
            if len(feedback_for_agent) >= MIN_BATCH_SIZE:
                # Trigger fine-tuning
                finetune_result = finetune_specialist_agent(
                    specialist_agent_id,
                    feedback_for_agent,
                )
                
                if finetune_result['status'] == 'SUCCESS':
                    # Deploy new version
                    deploy_specialist_version(
                        specialist_agent_id,
                        finetune_result['new_version'],
                        deployment_strategy='canary',  # 10% traffic initially
                    )
                    
                    integration_log['updates'].append({
                        'type': 'SPECIALIST_FINETUNING',
                        'specialist_id': specialist_agent_id,
                        'samples_used': len(feedback_for_agent),
                        'new_version': finetune_result['new_version'],
                        'timestamp': datetime.now(),
                    })
        
        # 3. EVENING (6 PM UTC): Monthly embedding refresh (if day of month == 1)
        if datetime.now().day == 1:
            embedding_refresh_result = monthly_embedding_refresh(
                month_year=datetime.now().strftime('%Y-%m')
            )
            integration_log['updates'].append({
                'type': 'EMBEDDING_REFRESH',
                'items_recomputed': embedding_refresh_result['total_items_recomputed'],
                'high_drift_agents': embedding_refresh_result['agents_with_high_drift'],
                'timestamp': datetime.now(),
            })
        
        # 4. Log results
        integration_log['completed_at'] = datetime.now()
        integration_log['total_updates'] = len(integration_log['updates'])
        
        log_to_database(integration_log)
        notify_team_summary(integration_log)
        
        return integration_log
```

### 8.2 Continuous Validation (Real-Time)

```python
class ContinuousValidator:
    def validate_specialist_response_in_production(
        response: str,
        specialist_id: str,
        query: str,
    ) -> ValidationResult:
        """
        Real-time validation during production query
        """
        validation_result = ValidationResult()
        
        # 1. Hallucination check (aluci-guard)
        hallucination_risk = detect_hallucination(response, rag_retrieval)
        if hallucination_risk['score'] > 0.6:
            validation_result.add_flag('HALLUCINATION_RISK', severity='HIGH')
        
        # 2. Source attribution check
        if not has_citations(response):
            validation_result.add_flag('MISSING_CITATIONS', severity='MEDIUM')
        
        # 3. Consistency check (compare with historical specialist responses)
        historical_responses = get_specialist_history(specialist_id, query_type=infer_type(query))
        consistency_score = compute_consistency(response, historical_responses)
        
        if consistency_score < 0.6:
            validation_result.add_flag('LOW_CONSISTENCY', severity='MEDIUM')
        
        # 4. Latency check
        if response['latency_ms'] > 500:
            validation_result.add_flag('HIGH_LATENCY', severity='LOW')
        
        if validation_result.has_high_severity_flags():
            # Log for post-incident analysis
            log_validation_failure(specialist_id, response, validation_result)
            
            # Trigger rollback if multiple failures
            if exceeds_error_rate_threshold(specialist_id):
                trigger_rollback(specialist_id, 'previous_stable_version')
        
        return validation_result
```

---

## 9. Skill Certification & Validation Framework

### 9.1 Certification Checklist per Specialist

Each specialist agent must pass multi-domain certification before production deployment:

```
┌──────────────────────────────────────────────────────────────────┐
│        SPECIALIST CERTIFICATION FRAMEWORK (Manta 4.3)             │
└──────────────────────────────────────────────────────────────────┘

DOMAIN: Barragens CFRD Specialist (barragens-cfrd-expert)

[ ] PHASE 1: KNOWLEDGE COMPLETENESS
  [ ] Coverage of ICOLD guidelines (CFRD design, stability)
  [ ] Coverage of Brazilian regulatory standards (PNSB, CBDB)
  [ ] Coverage of 10+ real CFRD projects (case studies)
  [ ] Coverage of failure modes & remediation
  [ ] Test: 50 domain questions, ≥90% accuracy required

[ ] PHASE 2: HALLUCINATION & CONSISTENCY
  [ ] Passes aluci-guard hallucination detector (aluci-score ≥0.95)
  [ ] Consistency with historical CFRD responses (80%+ match)
  [ ] No contradictions in sequential queries
  [ ] Citation accuracy: ≥90% of claims have valid sources
  [ ] Test: 100 adversarial queries (designed to trigger hallucinations)

[ ] PHASE 3: SOURCE ATTRIBUTION
  [ ] All critical claims cite RAG source
  [ ] Citations are accurate & retrievable
  [ ] Source document quality verified (ICOLD ≥ homemade PDFs)
  [ ] Working memory trace shows full reasoning
  [ ] Test: Manual review of 20 responses by domain expert (Geotechnical Engineer)

[ ] PHASE 4: REGRESSION TESTING
  [ ] No performance degradation vs. parent agent (Manta 03-S10)
  [ ] Latency p95 <500ms (same as base agent)
  [ ] Cost per query within tier budget ($0.003 for Sonnet)
  [ ] Error rate <2% (measured on 1000 production queries)
  [ ] Test: A/B test specialist vs. parent for 7 days

[ ] PHASE 5: REGULATORY ALIGNMENT
  [ ] Complies with PNSB (National Dam Safety Policy)
  [ ] Reflects latest CBDB (Brazilian Committee of Large Dams) standards
  [ ] Correctly interprets ANEEL regulations (if applicable)
  [ ] No obsolete references to deprecated standards
  [ ] Test: Reviewed by legal/compliance team

[ ] PHASE 6: FEEDBACK INTEGRATION
  [ ] Trained on ≥200 approved feedback samples
  [ ] Feedback distribution balanced (positive/negative/neutral)
  [ ] No overfitting to specific feedback clusters
  [ ] Test: Validation set accuracy ≥88%

[ ] PHASE 7: PRODUCTION READINESS
  [ ] Monitoring configured (latency, error rate, hallucinations)
  [ ] Rollback procedure tested and documented
  [ ] Canary deployment strategy ready (start 10%, ramp to 100%)
  [ ] Team trained on specialist agent
  [ ] Test: Dry-run canary on staging environment

✅ CERTIFICATION APPROVED: 2026-09-15 (All 7 phases passed)
   Certified by: Dr. Geotecnia (Domain Expert), Team Lead (Maestro)
   Valid for: 6 months (next review: 2027-03-15)
   Status: PRODUCTION-READY
```

### 9.2 Automated Domain Coverage Assessment

```python
class DomainCoverageMetrics:
    def assess_specialist_coverage(specialist_id: str) -> CoverageReport:
        """
        Measure how well specialist covers its domain
        """
        # 1. Extract domain keywords from RAG collection
        rag_keywords = extract_keywords_from_rag_collection(specialist_id)
        
        # 2. Test specialist on each keyword
        coverage_by_keyword = {}
        for keyword in rag_keywords:
            test_query = f"Explain {keyword} in context of {specialist_id}"
            response = specialist_id.generate(test_query)
            
            # Grade response
            grade = grade_response(response, keyword, reference_rag_doc)
            coverage_by_keyword[keyword] = grade  # A/B/C/D/F
        
        # 3. Compute overall coverage %
        total_keywords = len(rag_keywords)
        passing_keywords = sum(1 for grade in coverage_by_keyword.values() 
                             if grade in ['A', 'B'])
        coverage_percentage = passing_keywords / total_keywords * 100
        
        # 4. Identify gaps
        gaps = [kw for kw, grade in coverage_by_keyword.items() 
               if grade in ['D', 'F']]
        
        return CoverageReport(
            specialist_id=specialist_id,
            total_keywords=total_keywords,
            passing_keywords=passing_keywords,
            coverage_percentage=coverage_percentage,
            gaps=gaps,
            recommendation='READY_FOR_PRODUCTION' if coverage_percentage >= 85 
                          else 'NEEDS_MORE_TRAINING',
        )
```

---

## 10. Agent Versioning & Rollback Strategy

### 10.1 Semantic Versioning for Agents

```
Agent Version Format: X.Y.Z

Example: barragens-cfrd-expert v2.3.1

X = Major (breaking changes)
  • Behavior change affecting > 10% of responses
  • Specialist domain shift (e.g., CFRD → CCR dam specialist)
  • Migration to new base model (Sonnet → Opus)

Y = Minor (backward-compatible improvements)
  • Fine-tuning on new feedback batch (+feedback_batch_id)
  • New domain keywords added
  • RAG collection expansion
  • Knowledge distillation release (Sonnet → Haiku)

Z = Patch (bug fixes, maintenance)
  • Citation formatting fix
  • Typo correction
  • Documentation update
  • Linting/style changes
```

### 10.2 Version Registry & Git Tracking

```python
class AgentVersionRegistry:
    def register_agent_version(
        specialist_id: str,
        version: str,
        changes: Dict,
        trained_on_feedback_ids: List[str],
        certification_status: str,
    ):
        """
        Register specialist agent version in Git + database
        """
        # 1. Create git branch
        git_branch = f'agent/{specialist_id}/{version}'
        create_git_branch(git_branch)
        
        # 2. Commit version metadata
        version_metadata = {
            'version': version,
            'agent_id': specialist_id,
            'created_at': datetime.now().isoformat(),
            'changes': changes,
            'trained_on_feedback_ids': trained_on_feedback_ids,
            'certification_status': certification_status,
            'base_model': get_base_model(specialist_id),
            'lora_adapter_hash': hash_file(get_lora_path(specialist_id)),
            'rag_collection': get_rag_collection(specialist_id),
        }
        
        git_commit(
            branch=git_branch,
            message=f"Release {specialist_id} v{version}\n\n"
                   f"Changes:\n{format_changes(changes)}\n"
                   f"Trained on: {len(trained_on_feedback_ids)} feedback samples\n"
                   f"Certification: {certification_status}",
            files={
                f'agents/{specialist_id}/versions/v{version}/metadata.json': version_metadata,
                f'agents/{specialist_id}/versions/v{version}/CHANGELOG.md': format_changelog(changes),
            }
        )
        
        # 3. Register in database
        register_version_in_db({
            'specialist_id': specialist_id,
            'version': version,
            'git_branch': git_branch,
            'git_commit_hash': get_current_commit_hash(git_branch),
            'status': 'CREATED',
            'deployed_at': None,
            'certification_status': certification_status,
        })
        
        return {
            'status': 'REGISTERED',
            'git_branch': git_branch,
            'version_metadata': version_metadata,
        }
    
    def deploy_agent_version(
        specialist_id: str,
        version: str,
        deployment_strategy: str = 'canary',  # canary | blue-green | immediate
    ):
        """
        Deploy specialist agent to production
        """
        if deployment_strategy == 'canary':
            # 1. Start canary: 10% of traffic
            update_traffic_split({
                specialist_id: {
                    'current_version': get_current_version(specialist_id),
                    'canary_version': version,
                    'traffic_split': {'current': 90, 'canary': 10},
                }
            })
            
            # 2. Monitor metrics for 1 hour
            metrics_baseline = get_metrics_baseline(specialist_id, window_minutes=5)
            sleep(3600)
            metrics_after_canary = get_metrics_baseline(specialist_id, window_minutes=5)
            
            # 3. Evaluate
            error_rate_increase = (metrics_after_canary['error_rate'] - metrics_baseline['error_rate'])
            hallucination_increase = (metrics_after_canary['hallucination_rate'] - metrics_baseline['hallucination_rate'])
            
            if error_rate_increase > 0.01 or hallucination_increase > 0.02:
                # Rollback
                return rollback_agent_version(specialist_id)
            else:
                # Proceed to ramp-up: 50% traffic
                update_traffic_split({
                    specialist_id: {
                        'current_version': get_current_version(specialist_id),
                        'canary_version': version,
                        'traffic_split': {'current': 50, 'canary': 50},
                    }
                })
                
                sleep(1800)  # Monitor for 30 mins
                
                # Final ramp to 100%
                update_traffic_split({
                    specialist_id: {
                        'current_version': version,
                        'traffic_split': {'current': 100},
                    }
                })
    
    def rollback_agent_version(specialist_id: str, target_version: str = None):
        """
        Instant rollback to previous stable version
        """
        if target_version is None:
            # Auto-select: previous version marked as stable
            target_version = get_previous_stable_version(specialist_id)
        
        # 1. Verify target version is healthy
        health_check_result = verify_version_health(specialist_id, target_version)
        if not health_check_result['is_healthy']:
            raise Exception(f"Target version {target_version} is unhealthy")
        
        # 2. Instant traffic switch
        update_traffic_split({
            specialist_id: {
                'current_version': target_version,
                'traffic_split': {'current': 100},
            }
        })
        
        # 3. Log rollback
        log_incident({
            'type': 'AGENT_ROLLBACK',
            'specialist_id': specialist_id,
            'rolled_back_from': get_current_version(specialist_id),
            'rolled_back_to': target_version,
            'timestamp': datetime.now(),
            'triggered_by': 'AUTOMATED_HEALTH_CHECK',
        })
        
        return {
            'status': 'ROLLBACK_COMPLETE',
            'current_version': target_version,
            'time_to_rollback_ms': 150,  # Near-instant
        }
```

### 10.3 A/B Testing Infrastructure

```python
class AgentABTestingFramework:
    def create_ab_test(
        specialist_id: str,
        version_a: str,  # Current version
        version_b: str,  # Candidate version
        sample_size: int = 1000,  # Minimum queries to test
        success_criteria: Dict = None,
    ):
        """
        Set up A/B test for specialist version comparison
        """
        if success_criteria is None:
            success_criteria = {
                'error_rate_delta': 0.01,  # Version B must not exceed error rate by >1%
                'hallucination_delta': 0.02,  # Version B must not exceed hallucination by >2%
                'latency_p95_delta_ms': 100,  # Latency increase <100ms
                'user_satisfaction_win_rate': 0.50,  # Version B wins ≥50% of user votes
            }
        
        # 1. Create test variant
        test_config = {
            'test_id': uuid4(),
            'specialist_id': specialist_id,
            'version_a': version_a,
            'version_b': version_b,
            'status': 'ACTIVE',
            'start_time': datetime.now(),
            'sample_size_target': sample_size,
            'sample_size_current': 0,
            'success_criteria': success_criteria,
            'results': None,
        }
        
        # 2. Route 50% of traffic to each version
        update_traffic_split({
            specialist_id: {
                'version_a': version_a,
                'version_b': version_b,
                'traffic_split': {'a': 50, 'b': 50},
                'ab_test_id': test_config['test_id'],
            }
        })
        
        # 3. Monitor until sample size reached
        while test_config['sample_size_current'] < sample_size:
            test_config['sample_size_current'] = get_ab_test_sample_count(test_config['test_id'])
            sleep(60)
        
        # 4. Analyze results
        results = analyze_ab_test(test_config)
        
        if results['version_b_wins']:
            # Deploy version B
            deploy_agent_version(specialist_id, version_b)
            test_outcome = 'WINNER'
        else:
            # Keep version A, update traffic split to 100% A
            update_traffic_split({
                specialist_id: {
                    'current_version': version_a,
                    'traffic_split': {'current': 100},
                }
            })
            test_outcome = 'INCUMBENT_RETAINED'
        
        return {
            'test_id': test_config['test_id'],
            'outcome': test_outcome,
            'results': results,
            'timestamp': datetime.now(),
        }
```

---

## 11. Monitoring, Observability & Dashboards

### 11.1 Key Metrics per Specialist

| Metric | Definition | Alert Threshold | Cadence |
|--------|-----------|-----------------|---------|
| **Accuracy** | % of responses graded A/B by domain expert | <85% | Daily |
| **Hallucination Rate** | % of responses flagged by aluci-guard | >5% | Real-time |
| **Citation Coverage** | % of claims with valid source attribution | <80% | Daily |
| **Latency p95** | 95th percentile response time | >500ms | Real-time |
| **Error Rate** | % of responses causing errors | >2% | Real-time |
| **Feedback Integration Speed** | Time from feedback approval to specialist retraining | >7 days | Weekly |
| **Version Stability** | Days since last rollback | <7 days = unstable | Daily |
| **Domain Coverage** | % of domain keywords with passing grade | <85% | Monthly |
| **Consistency** | Semantic similarity between responses to similar queries | <0.75 | Daily |

### 11.2 Grafana Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  SPECIALIST AGENT DASHBOARD — barragens-cfrd-expert             │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────┬────────────────────┬────────────────────┐
│  Accuracy: 92%     │  Hallucination: 2%│  Citations: 88%    │
│  (Target: ≥85%)    │  (Target: <5%)     │  (Target: ≥80%)    │
└────────────────────┴────────────────────┴────────────────────┘

┌─────────────────────────────────┬───────────────────────────────┐
│  Latency p95: 380ms             │  Error Rate: 0.8%             │
│  (Target: <500ms)               │  (Target: <2%)                │
│  [line graph: 7-day trend]       │  [line graph: 7-day trend]    │
└─────────────────────────────────┴───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  FEEDBACK LOOP & LEARNING                                       │
│  • Feedback received this week: 42                              │
│  • Feedback approved: 38 (90%)                                  │
│  • Specialist retraining triggered: 2x                          │
│  • New version deployed: v2.4.0 (24h ago)                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────┬───────────────────────────────┐
│  TOP 10 FAILING QUERIES          │  SEMANTIC DRIFT ALERT         │
│  1. [Q text] (3 failures)        │  ⚠ Drift score: 0.28          │
│  2. [Q text] (2 failures)        │  Recommend: Review latest     │
│  3. [Q text] (2 failures)        │  fine-tune cohort             │
│  ...                             │                               │
└──────────────────────────────────┴───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  VERSION HISTORY                                                │
│  v2.4.0 (current) — Deployed 24h ago | 3 rollbacks available   │
│  v2.3.2 (stable)   — Deployed 5d ago  | Performance: 91%       │
│  v2.3.1 (retired)  — Rolled back 2d ago due to drift           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 12. Success Criteria & Acceptance Tests

### 12.1 Phase 4.3 Success Metrics

| Criterion | Target | Verification Method | Deadline |
|-----------|--------|-------------------|----------|
| **≥4 specialist agents operational** | 4+ agents in production | Agent registry + deployment logs | M6 (Mar 2029) |
| **Feedback loop integration ≥95%** | 95%+ of approved feedback integrated into specialists | Feedback → fine-tuning → deployment tracking | M6 |
| **Certification pass rate ≥90%** | 90%+ of specialists pass 7-phase certification | Certification audit logs | M6 |
| **Hallucination rate <3%** | aluci-guard score >0.97 for 97%+ responses | Real-time monitoring dashboard | Ongoing |
| **Citation accuracy ≥85%** | 85%+ of claims have valid, retrievable sources | Manual audit of 100 responses per specialist | M3 & M6 |
| **Embedding drift <0.25** | pgvector drift stays below semantic shift threshold | Monthly embedding refresh report | M6 |
| **Latency p95 <500ms** | 95th percentile latency within SLA | Real-time latency dashboard | Ongoing |
| **Rollback success rate 100%** | All rollbacks restore previous version within 2 minutes | Simulated rollback tests | M6 |
| **Knowledge distillation ≥90%** | Haiku-tier specialists retain ≥90% of Sonnet accuracy | A/B test results | M12 |
| **Continuous integration cycle <24h** | Daily knowledge refresh completes within 24 hours | Pipeline execution logs | Ongoing |
| **Zero unplanned agent behaviors** | No out-of-scope responses or jailbreaks | Security review + adversarial testing | M6 |
| **Domain expert satisfaction ≥4/5** | Domain experts rate specialists ≥4/5 stars | Survey of 5+ domain experts per specialist | M6 |

### 12.2 Acceptance Test Scenarios

**Test 1: Specialist Agent Creation & Certification**
```gherkin
Feature: Create and certify barragens-cfrd-expert specialist

Scenario: End-to-end specialist creation
  Given a new specialist agent requirement (CFRD dams)
  And 250+ approved feedback samples on CFRD topics
  When we run the specialist creation pipeline
  Then the specialist agent is created with LoRA adapter
  And the specialist passes all 7 certification phases
  And the specialist achieves ≥85% accuracy on domain test set
  And the specialist's hallucination rate <3%
  And the specialist is deployed to production (canary 10%)
  And the specialist is ready for domain expert validation
```

**Test 2: Feedback Loop Cycle**
```gherkin
Feature: Feedback loop drives specialist improvement

Scenario: User feedback → specialist retraining → deployment
  Given a production specialist agent (barragens-cfrd-expert v2.0)
  When a user provides negative feedback on a CFRD query
  And the Maestro team approves the feedback (confidence 0.92)
  And we batch the feedback with 49 other approved samples
  Then we trigger fine-tuning on the specialist
  And we create v2.1 with improved CFRD guidance
  And we deploy v2.1 to canary (10% traffic)
  And we verify error rate does not increase >1%
  And we ramp v2.1 to 100% traffic
  And we mark v2.0 as backup for rollback
```

**Test 3: Embedding Drift Detection**
```gherkin
Feature: Monthly embedding refresh detects semantic drift

Scenario: Detect quality degradation via vector drift
  Given a specialist agent with baseline embeddings
  When we recompute embeddings after monthly fine-tuning
  And the average cosine distance > 0.25
  Then we flag HIGH drift alert
  And we notify the Maestro team
  And we request domain expert review
  And if drift confirmed (expert review), we trigger rollback
```

**Test 4: Knowledge Distillation**
```gherkin
Feature: Distill Sonnet specialist to Haiku tier

Scenario: Compress specialist without significant accuracy loss
  Given a production Sonnet-tier specialist (barragens-cfrd-expert)
  When we run knowledge distillation to Haiku
  Then the Haiku-tier specialist is created
  And the Haiku specialist retains ≥90% accuracy
  And the Haiku specialist costs 3.5x less per query
  And the Haiku specialist inference latency <250ms
  And we deploy Haiku for high-volume use cases
```

**Test 5: Explainability & Citations**
```gherkin
Feature: All responses include working memory & citations

Scenario: Response includes trace & source attribution
  Given a specialist agent responding to a query
  When the agent generates a response
  Then the response includes:
    • All claims with RAG citations (confidence >0.75)
    • Working memory trace (5+ reasoning steps)
    • Specialist version used
    • Feedback samples used in fine-tuning
  And a domain expert can verify all citations
  And a domain expert rates citation accuracy ≥9/10
```

---

## 13. Implementation Timeline & Resources

### 13.1 Phase 4.3 Implementation Schedule (Q3–Q4 2028)

| Month | Workstream | Deliverables | Owner |
|-------|-----------|--------------|-------|
| **M1 (Jul 28)** | Setup & Infrastructure | Feedback curation API, confidence gating system, GitHub CI/CD for versioning | DevOps + Data |
| **M2 (Aug 28)** | Specialist Creation | barragens-cfrd-expert, saneamento-etq-expert specialists v1.0 | Maestro + Data |
| **M3 (Sep 28)** | Certification Framework | 7-phase certification for 2 specialists, domain expert validation | QA + domain experts |
| **M4 (Oct 28)** | Embedding Evolution | Monthly embedding refresh pipeline, drift detection, pgvector optimization | Data |
| **M5 (Nov 28)** | Knowledge Distillation | Haiku-tier distilled specialists, cost/latency benchmarks | ML Engineering |
| **M6 (Dec 28)** | Continuous Integration | Daily knowledge refresh cycle, regulatory webhook integration | DevOps + Data |
| **M7–M12** | Expansion & Optimization | 4+ additional specialists, A/B testing framework, production hardening | Full team |

### 13.2 Required Team & Skills

| Role | FTE | Responsibilities | Skills Required |
|------|-----|------------------|-----------------|
| **Maestro Architect** | 0.5 | System design, routing rules, specialist taxonomy | LLM architecture, agentic systems |
| **ML Engineer** | 1.0 | Fine-tuning, distillation, embedding evolution | PyTorch/TensorFlow, hugging face, optimization |
| **Data Engineer** | 1.0 | RAG pipeline, pgvector, feedback curation, ETL | SQL, vector DBs, data pipelines, Python |
| **DevOps Engineer** | 0.5 | CI/CD, versioning, deployment automation, monitoring | Kubernetes, GitHub Actions, Grafana |
| **QA/Test Specialist** | 0.5 | Certification framework, test suite, A/B testing | Testing methodologies, domain knowledge |
| **Domain Expert Advisor** | 0.3 | Review specialist quality, validate certification | Infrastructure engineering (CFRD, HVDC, ETQ, etc.) |

### 13.3 Cost Estimate

| Component | Cost | Notes |
|-----------|------|-------|
| **Infrastructure (GPU, compute, storage)** | €120K | Compute for fine-tuning (AWS/GCP), pgvector DB expansion, S3 storage for models |
| **API Costs (Anthropic)** | €180K | Fine-tuning costs (estimated 500K tokens × $0.30/1M), inference on validation |
| **Tooling & Software** | €40K | Grafana Enterprise, Weights & Biases, vector DB licensing |
| **Personnel (7 months, 4 FTE avg)** | €280K | Salaries for ML engineer, data engineer, DevOps, QA |
| **Training & Documentation** | €30K | Domain expert time, training materials, runbooks |
| **Contingency (10%)** | €65K | Risk buffer for unexpected challenges |
| **TOTAL** | **€715K** | Range: €600K–€850K (high variance in API costs) |

---

## 14. Risks & Mitigation Strategies

### 14.1 Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Fine-tuning causes catastrophic hallucinations** | Medium | Critical | Comprehensive hallucination testing, aluci-guard integration, human review gate for Tier 1, rollback SLA <2min |
| **Embedding drift goes undetected, quality degrades silently** | Low | High | Monthly pgvector refresh, anomaly detection alerts, statistical outlier checks |
| **Knowledge distillation loses critical domain knowledge** | Low | High | Strict accuracy thresholds (≥90% retention), extensive validation testing, fallback to larger model |
| **Feedback loop creates positive feedback loops (reinforces mistakes)** | Medium | High | Diversity monitoring, feedback source validation, expert human review gate, periodic model resets |
| **Specialist agents conflict in multi-agent scenarios (Manta 17 orchestrator)** | Medium | Medium | Clear specialist taxonomy, non-overlapping keywords, orchestrator validation tests, routing conflict alerts |
| **Version management chaos (too many specialist variants)** | Low | Medium | Strict semantic versioning, Git-based versioning, automated deprecation of old versions after 6 months |
| **API costs explode due to fine-tuning volume** | Low | High | Rate limiting on fine-tuning frequency, cost monitoring dashboard, budgets per specialist, opt-in for expensive features |
| **Domain experts unavailable for certification reviews** | Low | Medium | Asynchronous review process, certification runbooks, domain expert training program |
| **Regulatory compliance issues (GDPR, audit trail)** | Low | Critical | Immutable audit logs, PII anonymization, encryption, compliance monitoring, legal review gate |

### 14.2 Rollback & Recovery Procedures

**Procedure: Instant Rollback (90 seconds)**
1. Monitor detects error rate spike >5% or hallucination rate >10%
2. Automated system triggers rollback to previous stable version
3. Traffic instantly switched (distributed cache invalidation)
4. Incident logged with root cause placeholder
5. On-call engineer notified (Slack + PagerDuty)

**Procedure: Emergency Model Reset**
1. If all recent versions degraded (cascading failure)
2. Revert to base model from 30 days ago
3. Disable fine-tuning for specialist (manual review required)
4. Root cause analysis: investigate feedback batch that caused degradation

---

## 15. Success Stories & Use Cases

### 15.1 Example: barragens-cfrd-expert Lifecycle

**Month 1: Creation & Training**
- Curator extracts 250 CFRD-specific feedback samples from historical Cowork button clicks
- Confidence gating: 240 samples pass confidence threshold (>0.80)
- Fine-tuning loop: Contrastive learning on CFRD triplets
- Result: barragens-cfrd-expert v1.0.0 created

**Month 2: Certification**
- Domain expert (Dr. Geotécnica) reviews 50 test responses
- Hallucination check: aluci-guard passes with 0.96 score
- Citation accuracy: 92% (exceeds 85% threshold)
- Coverage: 89 of 95 CFRD keywords graded A/B (93.7%)
- Result: PASSES all 7 certification phases → PRODUCTION-READY

**Month 3: Canary Deployment**
- Deploy to 10% production traffic (parallel with parent agent Manta 03-S10)
- Week 1: Error rate specialist 0.8% vs. parent 1.2% (specialist wins)
- Week 2: Hallucination rate specialist 1.8% vs. parent 2.1% (specialist wins)
- Ramp to 100% traffic after 1 week
- Result: STABLE in production

**Month 4: Feedback Loop in Action**
- User provides feedback: "Specialist incorrectly referenced outdated PNSB standard"
- Confidence score: 0.94 (auto-approve)
- Batch collected: 35 similar feedback samples over 1 week
- Fine-tuning: v1.1.0 created (LoRA update on same base model)
- Deployment: Canary 10% → 50% (A/B test 100 samples) → 100%
- Result: PNSB standards updated, user satisfied

**Month 5: Knowledge Distillation**
- Distill v1.1.0 (Sonnet) to Haiku tier
- Haiku specialist v1.0.0 creates:
  - Cost reduction: $0.003 → $0.0008 per query (3.75x)
  - Latency: 400ms → 220ms (45% faster)
  - Accuracy retention: 91% (exceeds 90% threshold)
- Deployment: Haiku for real-time applications, Sonnet for complex analyses
- Result: Cost-effective high-volume support

---

## 16. References & Standards

**Anthropic & LLM Standards:**
- Claude API Fine-Tuning Guide: https://docs.anthropic.com
- Embeddings API (1536-dimensional): https://docs.anthropic.com/api/embeddings
- Aluci-guard Hallucination Detection: Internal Manta skill
- LoRA (Low-Rank Adaptation): Hu et al., 2021

**Domain Standards:**
- ICOLD Bulletin 123: CFRD Design Guidelines
- PNSB (Lei 12.334/2010): National Dam Safety Policy
- NBR 12211-12218: Brazilian Water & Wastewater Standards
- ANEEL Resolution 786/2020: Regulatory compliance (energy)

**Infrastructure & Observability:**
- PostgreSQL pgvector: https://github.com/pgvector/pgvector
- Grafana Dashboards: https://grafana.com
- Anthropic SDK (Python): https://github.com/anthropics/anthropic-sdk-python

---

## 17. Glossary

| Term | Definition |
|------|-----------|
| **LoRA** | Low-Rank Adaptation — efficient fine-tuning method updating only 1–5% of model weights |
| **pgvector** | PostgreSQL extension for vector similarity search (cosine, L2, inner product) |
| **Confidence Gate** | Three-tier filtering: auto-approve (≥0.90) → manual (0.70–0.90) → reject (<0.70) |
| **Semantic Drift** | Shift in response quality measured via cosine distance in embedding space |
| **Contrastive Learning** | Training method learning from positive/negative example pairs, minimizing distance to positive, maximizing to negative |
| **Knowledge Distillation** | Compressing large teacher model (Opus/Sonnet) to smaller student (Haiku) while retaining accuracy |
| **Specialist Agent** | Domain-specific fine-tuned variant of parent agent (e.g., barragens-cfrd-expert from Manta 03-S10) |
| **Aluci-guard** | Manta internal hallucination detector measuring factual consistency with RAG knowledge base |
| **Canary Deployment** | Gradual rollout: 10% → 50% → 100% traffic, with health checks at each stage |
| **Audit Trail** | Immutable log of all decisions: feedback approval, fine-tuning, deployments, rollbacks |

---

## 18. Document Control

| Field | Value |
|-------|-------|
| **Document ID** | PK_MN_4.3.0 |
| **Title** | Phase 4.3 — Agent Learning & Specialization |
| **Version** | 1.0 (Final Specification) |
| **Status** | Ready for Implementation |
| **Owner** | Maestro Team (Manta Associados) |
| **Last Updated** | 2026-07-26 |
| **Next Review** | 2028-09-15 (Start of Phase 4.3 execution) |
| **Approvers** | Engineering Lead, Product Lead, Compliance Officer |

---

**END OF SPECIFICATION**
