以下は、Google Design Doc（GDD）スタイルに従った、MongoDB と PostgreSQL の DB設計ドキュメントです。要件に沿って Purpose, Background, Design, Schema, Trade-offs 等のセクションを含めています。

⸻


# Design Doc: Database Design for Multi-Agent Graph-based Advertising Evaluation System

## Authors
- Takumi (Data Engineer)

## Created
- 2025-06-21

## Status
- Draft

---

## 1. Overview

This document outlines the database design for the advertising effectiveness evaluation platform that simulates 47 local agents (modeled after Japanese prefectures). The system uses LangChain-based LLM agents and Ray for concurrent simulation and evaluation, storing structured outputs in MongoDB and PostgreSQL.

---

## 2. Goals and Non-Goals

### Goals
- Store structured LLM outputs (e.g., liking, purchase_intent, commentary) with metadata.
- Record advertising metadata and region-specific feedback.
- Enable both JSON-style document storage and relational analytics.
- Enable future expansion for user-level personalization and campaign simulation.

### Non-Goals
- Real-time streaming data ingestion.
- Full-text search or vector similarity at this stage.

---

## 3. Background

Due to the hybrid nature of the simulation (LLM outputs with flexible structure + fixed advertising metadata), we adopt a dual-database architecture:

- **MongoDB** for semi-structured documents from agents.
- **PostgreSQL** for normalized structured data like ads, users, and feedback.

---

## 4. Design Summary

| Purpose                | MongoDB                       | PostgreSQL                   |
|------------------------|-------------------------------|------------------------------|
| LLM Agent Outputs      | ✅ Yes                        | 🚫 No                         |
| Advertising Metadata   | ❌ Not Suitable                | ✅ Yes                        |
| Aggregation / Analytics| ❌ Weak                        | ✅ Strong                     |
| Persona Configuration  | ✅ JSON-based, flexible        | 🚫 Not needed in relational  |

---

## 5. Detailed Schema Design

### 5.1 MongoDB Collections

#### `agent_outputs`

```json
{
  "agent_id": "Tokyo",
  "ad_id": "abc-123",
  "liking": 4.2,
  "purchase_intent": 3.8,
  "neighbors_used": ["Chiba", "Saitama"],
  "commentary": "健康意識の高い人には響くが、価格面での魅力がやや弱い",
  "timestamp": "2025-06-21T10:00:00Z"
}
```

#### agents

```json
{
  "agent_id": "Osaka",
  "persona_config": {
    "age_distribution": {"20s": 0.3, "30s": 0.4, "40s": 0.3},
    "preferences": ["price-sensitive", "urban"],
    "cluster": "cost-conscious"
  },
  "prompt_template": "あなたは都会的な購買志向をもつ消費者です...",
  "created_at": "2025-06-01T00:00:00Z"
}
```

#### ad_logs

```json
{
  "ad_id": "xyz-789",
  "agent_id": "Hokkaido",
  "content": "無添加・国産素材のスキンケア商品をご紹介！",
  "shown_at": "2025-06-10T08:30:00Z"
}
```


### 5.2 PostgreSQL Tables

##### ads
```sql
CREATE TABLE ads (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  published_at TIMESTAMP
);
```

#### agent_metadata

```sql
CREATE TABLE agent_metadata (
  id UUID PRIMARY KEY,
  agent_code TEXT UNIQUE NOT NULL,
  population INTEGER,
  age_distribution JSONB,
  preferences JSONB,
  region TEXT
);
```

#### user_feedback

```sql
CREATE TABLE user_feedback (
  id UUID PRIMARY KEY,
  ad_id UUID REFERENCES ads(id),
  agent_code TEXT,
  liking NUMERIC(3,1),
  purchase_intent NUMERIC(3,1),
  feedback_text TEXT,
  collected_at TIMESTAMP
);
```

⸻

## 6. Trade-offs

| Option | 	Pros | Cons |
| ------ | ------ | ------ |
|MongoDB for agent output |	Flexible schema, fast inserts, JSON-native | Not ideal for large-scale joins or aggregations|
|PostgreSQL for analytics | Strong typing, indexing, JOIN support | Less flexible for evolving agent schemas|
|Separate DBs | Each is optimized for use case | ETL and data consistency must be managed explicitly | 


⸻

## 7. Future Considerations
- Add vector support (e.g., pgvector, MongoDB Atlas Vector Search) for similarity-based feedback.
- Support data sync pipelines for joining Mongo + SQL data in Snowflake / BigQuery.
- Evaluate TTL indexes in MongoDB for transient data storage.

⸻

## 8. Appendix

Required Indexes

### MongoDB
- agent_outputs: Compound index on (agent_id, ad_id)
- agents: Unique index on agent_id

### PostgreSQL
- user_feedback.ad_id
- agent_metadata.agent_code

