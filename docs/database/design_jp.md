承知しました。以下は、**Google Design Doc形式に準拠した、MongoDB・PostgreSQLのDB設計書（完全日本語版）**です。

⸻


# デザインドキュメント: Multi-Agent広告効果測定システムにおけるDB設計

## 作成者
- Takumi（データエンジニア）

## 作成日
- 2025年6月21日

## ステータス
- ドラフト

---

## 1. 概要

本ドキュメントでは、47都道府県を模したLLMエージェントが広告効果をスコアリングするシステムにおける、MongoDBおよびPostgreSQLのデータベース設計について説明する。

本システムはLangChainベースのマルチエージェント構成、Rayによる並列実行を特徴とし、スコア出力などの半構造データをMongoDBへ、広告メタデータやユーザー評価などの構造化データをPostgreSQLへ格納する。

---

## 2. 目的と非目的

### 目的
- エージェントの出力（スコア、コメント等）を構造化された形式で保存可能にする
- 広告・ユーザー評価・地域メタデータを分析可能な形で管理する
- MongoDBとPostgreSQLの役割を明確に分離することで保守性と拡張性を確保する

### 非目的
- リアルタイムストリーミング処理
- ベクトル検索や全文検索（本設計では対象外）

---

## 3. 背景

LLMの出力はJSON形式でフィールド構造が変動しやすいため、柔軟なスキーマを持つMongoDBが適している。一方で、広告やユーザー評価などのデータは集計分析が必要であり、正規化・インデックス・集約が可能なPostgreSQLの方が適している。

このため、デュアルストレージアーキテクチャを採用する。

---

## 4. 全体設計の要約

| 用途                         | MongoDB ✅                     | PostgreSQL ✅                   |
|------------------------------|--------------------------------|---------------------------------|
| Agentの出力スコア・コメント  | 柔軟な構造が必要 → ✅          | 集計向きではない → ❌           |
| 広告の基本情報・分類         | JSONは不要 → ❌                | 正規化が適する → ✅             |
| 地域メタ情報                 | 階層構造・クラスタ → ✅        | 分析・JOIN → ✅                 |
| ユーザー評価・スコア集計     | 構造が固定・分析向き → ❌      | 正規化と集約が必要 → ✅         |

---

## 5. スキーマ詳細

### 5.1 MongoDB コレクション設計

####  agent_outputs

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

⸻

### 5.2 PostgreSQL テーブル設計

#### ads

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

## 6. トレードオフと判断理由

|項目 | 採用理由 | 留意点 |
| ------ | ------ | ------ |
| MongoDB | 柔軟な構造でLLM出力に最適 | 集計やJOINには不向き |
| PostgreSQL | 集計・正規化・JOINに強い | スキーマの変更に柔軟性がない|
| 分離構成 | 役割分離が明確、分析と保存を両立 | ETLや整合性の担保が必要|


⸻

## 7. 今後の拡張
- MongoDBにTTLインデックスを設定し、一時的な評価結果を自動削除
- PostgreSQLでのBI分析用にビューやマテリアライズドビューを設計
- ベクトル検索対応（pgvector / MongoDB Atlas Vector Search）

⸻

## 8. 補足：インデックス設計

### MongoDB
- agent_outputs: (agent_id, ad_id) に複合インデックス
- agents: agent_id にユニークインデックス

### PostgreSQL
- user_feedback.ad_id: 外部キー＋インデックス
- agent_metadata.agent_code: 一意性のためのインデックス

---

この設計をベースに、必要であれば以下のステップに進めます：

- MongoDBのODMモデル定義（Beanie / PyMongo）
- PostgreSQLのORM定義（SQLAlchemy）
- `docker-compose.yml`によるサービス統合構成の自動化

どこから進めましょうか？