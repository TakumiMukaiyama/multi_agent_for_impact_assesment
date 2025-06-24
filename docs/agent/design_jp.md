# エージェント設計

* 各都道府県Agentはペルソナに基づくシステムプロンプトを持つ
* ペルソナは人口統計や購買データに基づき、複数クラスタから設計される（例：若年層志向、高齢層志向、自然派志向など）
* ツールはBaseToolを定義した上で、それを継承して作成する

## Agentが使うTool

### データ取得・参照系

| Tool名                      | 説明                         | 入力                                | 出力                       |
| -------------------------- | -------------------------- | --------------------------------- | ------------------------ |
| retrieve\_neighbor\_scores | 隣接Agentのスコアを取得し、評価の文脈に組み込む | agent\_id（都道府県コード）                | {neighbor\_id: スコア, ...} |
| access\_local\_statistics  | 地域別の統計情報（人口、年齢構成、消費傾向）を取得  | agent\_id                         | 地域統計の構造化データ（JSON形式）      |
| fetch\_previous\_ads       | 対象エリアで過去に表示された広告の履歴を取得     | agent\_id, ad\_category(optional) | 広告履歴リスト                  |

### 分析・評価系

| Tool名                        | 説明                        | 入力                           | 出力                              |
| ---------------------------- | ------------------------- | ---------------------------- | ------------------------------- |
| analyze\_ad\_content         | 広告の内容を分類・要素抽出（カテゴリ、訴求軸など） | ad\_text                     | 分析結果（カテゴリ、特徴語など）                |
| estimate\_cultural\_affinity | 広告と地域ペルソナとの親和性を評価         | ad\_text, agent\_profile     | 親和性スコア（0.0〜1.0）                 |
| generate\_commentary         | 広告に対するAgentの自然言語的コメントを生成  | ad\_text, agent\_profile     | コメント文                           |
| calculate\_aggregate\_score  | 自身と隣接Agentのスコアから加重平均を算出   | own\_score, neighbor\_scores | 平均スコア（liking, purchase\_intent） |

### 管理・補助系

| Tool名                   | 説明                          | 入力                            | 出力            |
| ----------------------- | --------------------------- | ----------------------------- | ------------- |
| log\_score\_to\_db      | Agentのスコア・コメント等を永続化ストレージに記録 | agent\_id, ad\_id, スコア, コメント等 | 成功・失敗ステータス    |
| validate\_input\_format | 入力された広告データの形式チェック           | ad\_payload (dict)            | 正常 / エラー + 内容 |

### 拡張候補ツール（Optional）

| Tool名                     | 説明                         | 入力                     | 出力              |
| ------------------------- | -------------------------- | ---------------------- | --------------- |
| simulate\_word\_of\_mouth | Agent間の口コミ伝播を模擬（SIR/拡散モデル） | agent\_id, 初期スコア       | スコア変化シミュレーション結果 |
| translate\_advertisement  | 広告テキストを多言語に翻訳（グローバル展開検証用）  | ad\_text, target\_lang | 翻訳後テキスト         |
| retrieve\_user\_feedback  | 実ユーザーからの評価・アンケート結果を取得      | ad\_id, agent\_id      | ユーザー評価スコア／分布    |

---

## LangChain実装方針

### 全体アーキテクチャ

* **FastAPI Entrypoint**：外部からの広告評価リクエストを受付
* **AgentExecutorManager**：評価フローを統括。Graph構造を参照し、隣接ノード数が少ないAgentから順に評価を実行

  * **GraphManager**：NetworkX で都道府県隣接Graphを保持し、評価順序や隣接ノード取得を提供
  * **ScoreCache**：MongoDB／PostgreSQL に Agent 出力スコアを保存・取得
  * **AgentFactory**：都道府県IDを渡すと対応する LangChain AgentExecutor を生成

```
FastAPI  ─▶ AgentExecutorManager ─▶ AgentExecutor (47)
             ▲            │
             │            └─▶ ScoreCache (DB)
             │
             └─▶ GraphManager (隣接情報)
```

### AgentExecutor の構成

| レイヤ               | 役割                                                                              |
| ----------------- | ------------------------------------------------------------------------------- |
| **System Prompt** | ペルソナ・評価タスク・Tool使用指示を含む                                                          |
| **LLM**           | OpenAI GPT-4o / Claude / その他基盤モデル                                               |
| **Tools**         | 前述した StructuredTool 群を利用 (`retrieve_neighbor_scores`, `analyze_ad_content`, など) |
| **Output Parser** | Pydantic で `liking`, `purchase_intent`, `commentary` を構造化                       |

### Tool 実装ガイドライン

* `@tool` デコレータで LangChain StructuredTool として実装し、入出力を型安全に管理
* DB アクセス系 Tool（`retrieve_neighbor_scores`, `log_score_to_db` 等）は非同期 (async) 実装
* 分析系 Tool（`analyze_ad_content`, `estimate_cultural_affinity`）は LLM 呼び出しをラップし、再利用を想定
* Tool 群は DI コンテナで一元管理し、AgentFactory に注入

### 評価フロー

1. GraphManager が `degree` の小さいノードリストを生成
2. 順次 AgentExecutor に `ad_text` と `agent_id` を投入
3. Agent 内で必要に応じて `retrieve_neighbor_scores` を呼び出し、隣接スコアを取得
4. Agent が `liking` と `purchase_intent` を算出し、`log_score_to_db` で保存
5. AgentExecutorManager が全 47 Agent のスコアを集計し、最終レポートを返却

### ディレクトリ構成例

```
src/
├─ agents/
│   ├─ factory.py        # AgentFactory
│   ├─ prompts/
│   │   └─ tokyo_prompt.txt
│   └─ tools/
│       ├─ __init__.py
│       ├─ data_access.py
│       ├─ analysis.py
│       └─ utils.py
├─ graph/
│   └─ graph_manager.py
├─ executor/
│   └─ manager.py
├─ api/
│   └─ main.py           # FastAPI Entrypoint
└─ schemas/
    └─ score.py          # Pydantic Models
```

### 今後の拡張

* **GNN統合**：PyTorch Geometric を導入し、ノード特徴 + 隣接重みでスコア補正
* **RAG導入**：ChromaDB に過去広告をベクトル化格納し、類似広告をContext注入
* **UI 可視化**：Streamlit で地図ヒートマップ & コメント一覧をリアルタイム表示
