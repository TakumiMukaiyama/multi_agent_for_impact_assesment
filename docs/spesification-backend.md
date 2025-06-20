# GraphとMultiAgentを組み合わせた効果測定システム

## 概要
47都道府県を模したLLMエージェントを構築し、地理的な隣接関係をグラフで表現することで、広告の効果を分析・予測するシミュレーション基盤を構築する。各Agentは、都道府県の民群特性に基づいたペルソナを搭載し、広告文に対する好意度、購買意向などをスコアとして出力する。

## バックエンド処理

### 言語
Python

### フレームワーク
- FastAPI (API層)
- LangChain (LLM Agent制御)
- Ray (Agentの平行実行)
- NetworkX (Graph構築)
- Pydantic (envやschema検証)

### Database設計

#### DB選定方針の前提整理

| データ種類             | 特徴      | 適したDB    |
|------------------------|----------------------------------------------|--------------|
| Agentの出力スコア      | JSON構造・項目の可変性・階層構造             |  MongoDB   |
| 地域・広告履歴         | 柔軟な構造でバージョン・履歴が重要           |  MongoDB   |
| 広告のメタ情報         | 固定構造・JOINで分析向き  | PostgreSQL|
| 実ユーザーの評価ログ   | 時系列・集計分析が多く、正規化に適する       | PostgreSQL|
| Agent設定・プロンプト  | JSONベースで更新頻度が高い| MongoDB   |

#### 📦 MongoDB：構造が柔軟なJSONベースデータの保存

##### 🔸 コレクション1: `agent_outputs`

| 項目名           | 型        | 説明                |
|------------------|-----------|---------------------------------------|
| `agent_id`       | str       | 例: `"Tokyo"`       |
| `ad_id`          | str       | 対象広告のID        |
| `liking`         | float     | 広告の好意度スコア（0.0〜5.0）        |
| `purchase_intent`| float     | 購買意欲スコア      |
| `neighbors_used` | list[str] | 評価に使用した隣接AgentのID一覧       |
| `commentary`     | str       | Agentによる自然言語コメント           |
| `timestamp`      | datetime  | 出力時刻            |

##### 🔸 コレクション2: `agents`

| 項目名          | 型        | 説明             |
|-----------------|-----------|------------------------------------|
| `agent_id`      | str       | `"Tokyo"` など   |
| `persona_config`| dict      | 年齢分布・志向など                 |
| `prompt_template`| str      | システムプロンプトテンプレート     |
| `created_at`    | datetime  | 登録時刻         |

##### 🔸 コレクション3: `ad_logs`

| 項目名      | 型      | 説明                |
|-------------|---------|---------------------------------------|
| `ad_id`     | str     | 広告ID              |
| `agent_id`  | str     | 表示地域            |
| `content`   | str     | 広告文              |
| `shown_at`  | datetime| 表示された日時      |

---

#### PostgreSQL：分析・検索・集計に強い構造化データ向け

##### 🔹 テーブル1: `ads`

```sql
CREATE TABLE ads (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    published_at TIMESTAMP
);
```

##### 🔹 テーブル2: agent_metadata
```sql
CREATE TABLE agent_metadata (
    id UUID PRIMARY KEY,
    agent_code TEXT UNIQUE NOT NULL,   -- e.g., 'Tokyo'
    population INT,
    age_distribution JSONB,
    preferences JSONB,
    region TEXT
);
```

##### 🔹 テーブル3: user_feedback
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

#### 🔁 MongoDB と PostgreSQL のデータ関係図（概念）

[ads] ----------------------> [user_feedback]
  |                                  ▲
  |                                  |
  ↓                                  |
[ad_logs] --(agent_id)--> [agent_metadata]
  ↓
[agent_outputs]

## プロジェクト構成 (Docker/開発実行前提)

```plaintext
project_root/
├── Dockerfile         # FastAPI + Agentサービス用Docker設定
├── docker-compose.yml    # MongoDB、Ray、WebAPIの統合起動設定
├── pyproject.toml        # Poetry または pip-tools 用
├── .env # DB接続情報やAPIキー
├── README.md
└── src/
    ├── main.py           # FastAPIのエントリーポイント
    ├── api/            # APIルーティング
    │   ├── router.py                # include_router のハブ
    │   └── v1/
    │       ├── agent.py             # /agents 管理API
    │       ├── ad.py                # /ads 管理API
    │       └── graph.py             # /graph の構造取得
    ├── core/            # Graph構築、静的初期化
    │   ├── llm_settings.py  # PydanticでLLMの設定を行う。
    │   └── db_settings.py  # Pydanticでdbの設定を行う。
    ├── agents/          # Agent本体
    │   ├── base.py # LangChain BaseAgent
    │   ├── persona_factory.py       # 都道府県ペルソナの生成
    │   ├── registry.py              # Agentの登録・管理
    │   └── tools/# Agentが使用するTool群
    │       ├── retrieve_neighbor_scores.py
    │       ├── access_local_statistics.py
    │       ├── fetch_previous_ads.py
    │       ├── analyze_ad_content.py
    │       ├── estimate_cultural_affinity.py
    │       ├── generate_commentary.py
    │       ├── calculate_aggregate_score.py
    │       ├── log_score_to_db.py
    │       └── validate_input_format.py
    ├── llm/              # LLMの拡張性を保つ
    │   ├── client/              
    │   │   ├── azure_openai_client.py
    │   │   └── gemini_client.py
    │   └── chain/
    │       └── pydantic_chain.py
    │   
    ├── db/ 
    │   ├── model/               
    │   │   └── {model_name}.py     # dbのmodel ORMで定義する
    │   ├── client/               
    │   │   ├── postgredb_client.py # postgredbの接続
    │   │   └── mongodb_client.py       # Mongoの接続
    │   └── repository.py            # CRUD抽象化
    ├── services/         # ドメインロジック
    │   ├── graph/         # graph ロジック
    │   │   ├── executor.py     # 隣接関係の情報依存計算
    │   │   └── builder.py     # NetworkX の構築
    │   ├── llm_excecuter/  # Rayベースの並行エージェント呼び出し
    │   │          └── scheduler.py #Rayの平行Agent呼び出し
    │   ├── ad_evaluation.py # 広告をAgentが分析する主ロジック
    │   └── score_formatter.py   # 出力JSONの形式化
    └── utils/            # 補助的モジュール
        ├── logger.py
        ├── cache.py
        ├── token_counter.py
        └── timer.py

chain/pydantic.py
```python
import time
from typing import Type

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from src.llm.client.azure_openai_client import AzureOpenAIClient
from src.llm.client.nomuchat_client import NomuchatClient
from src.llm.dependancy.base import BaseInput, BaseOutput
from src.llm.dependancy.prompt import FACT_SUMMARY_PROMPT
from src.llm.schema.fact_summary import FactSummaryInput, FactSummaryOutput


class PydanticChain:
    prompt_template: PromptTemplate = FACT_SUMMARY_PROMPT
    input_schema: Type[BaseInput] = FactSummaryInput
    output_schema: Type[BaseOutput] = FactSummaryOutput

    def __init__(
        self,
        chat_llm: ChatOpenAI,
    ):
        self.chat_llm = chat_llm
        self.parser = PydanticOutputParser(pydantic_object=self.output_schema)
        self.chain = self.prompt_template | self.chat_llm | self.parser

    def invoke_with_retry(self, *args, max_retries: int = 10, llm_client: AzureOpenAIClient | NomuchatClient, **kwargs):
        """Invoke the chain with retry.
        Args:
            max_retries (int): 最大リトライ回数
            llm_client (AzureOpenAIClient | NomuchatClient): LLMクライアント
            *args: チェーンに渡す位置引数
            **kwargs: チェーンに渡すキーワード引数
        Returns:
            Any: チェーンの実行結果
        Raises:
            Exception: エラー発生時に再送出
        """
        try:
            return self.invoke(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()

            # 401: APIキー期限切れ
            if any(msg in error_msg for msg in ["invalid api key", "invalid authorization"]):
                if isinstance(llm_client, NomuchatClient):
                    self.chat_llm = llm_client.reinitialize_llm(self.chat_llm)
                    # chat_llm_smallがある場合だけ再初期化
                    if hasattr(self, "chat_llm_small"):
                        self.chat_llm_small = llm_client.reinitialize_llm(self.chat_llm_small)
                    # RunnableSequenceでチェーンを再構築
                    self.chain = self.prompt_template | self.chat_llm | self.parser
                    return self.invoke(*args, **kwargs)
                raise e

            # 429: レート制限
            elif any(msg in error_msg for msg in ["rate limit", "requests", "threshold"]):
                last_error = e
                for attempt in range(max_retries - 1):  # 初回実行を除いてリトライ
                    time.sleep(60)
                    try:
                        return self.invoke(*args, **kwargs)
                    except Exception as retry_e:
                        last_error = retry_e
                        continue
                raise last_error

            # その他のエラー
            raise e

    def invoke(self, inputs: BaseInput, **kwargs):
        """Invoke the chain."""
        return self.chain.invoke(
            inputs.model_dump(),
            **kwargs,
        )

    def validate_output(self, output: dict) -> bool:
        """出力のバリデーションを行う"""
        if not isinstance(output.get("fund_evaluation_fact_summary"), str):
            return False
        return True

```

### エージェント設計
- 各都道府県Agentはペルソナに基づくシステムプロンプトを持つ
- ペルソナは人口統計や購買データに基づき、複数クラスタから設計される（例：若年層志向、高齢層志向、自然派志向など）
- ツールはBaseToolを定義した上で、それを継承して作成する


#### Agentが使うTool
##### データ取得・参照系

| Tool名   | 説明          | 入力| 出力|
|---------------------------|------------------------------------------------------------------|---------------------------------------|---------------------------------------|
| retrieve_neighbor_scores  | 隣接Agentのスコアを取得し、評価の文脈に組み込む                | agent_id（都道府県コード）            | {neighbor_id: スコア, ...}            |
| access_local_statistics   | 地域別の統計情報（人口、年齢構成、消費傾向）を取得             | agent_id             | 地域統計の構造化データ（JSON形式）  |
| fetch_previous_ads        | 対象エリアで過去に表示された広告の履歴を取得  | agent_id, ad_category(optional)       | 広告履歴リスト        |

##### 分析・評価系

| Tool名   | 説明          | 入力| 出力|
|---------------------------|------------------------------------------------------------------|---------------------------------------|---------------------------------------|
| analyze_ad_content        | 広告の内容を分類・要素抽出（カテゴリ、訴求軸など）             | ad_text              | 分析結果（カテゴリ、特徴語など）      |
| estimate_cultural_affinity| 広告と地域ペルソナとの親和性を評価            | ad_text, agent_profile                | 親和性スコア（0.0〜1.0）              |
| generate_commentary       | 広告に対するAgentの自然言語的コメントを生成    | ad_text, agent_profile                | コメント文            |
| calculate_aggregate_score | 自身と隣接Agentのスコアから加重平均を算出      | own_score, neighbor_scores            | 平均スコア（liking, purchase_intent） |

##### 管理・補助系

| Tool名   | 説明          | 入力| 出力|
|---------------------------|------------------------------------------------------------------|---------------------------------------|---------------------------------------|
| log_score_to_db           | Agentのスコア・コメント等を永続化ストレージに記録               | agent_id, ad_id, スコア, コメント等   | 成功・失敗ステータス |
| validate_input_format     | 入力された広告データの形式チェック            | ad_payload (dict)    | 正常 / エラー + 内容 |

## 拡張候補ツール（Optional）

| Tool名   | 説明          | 入力| 出力|
|---------------------------|------------------------------------------------------------------|---------------------------------------|---------------------------------------|
| simulate_word_of_mouth    | Agent間の口コミ伝播を模擬（SIR/拡散モデル）    | agent_id, 初期スコア| スコア変化シミュレーション結果        |
| translate_advertisement   | 広告テキストを多言語に翻訳（グローバル展開検証用）             | ad_text, target_lang | 翻訳後テキスト        |
| retrieve_user_feedback    | 実ユーザーからの評価・アンケート結果を取得      | ad_id, agent_id      | ユーザー評価スコア／分布              |

### グラフ処理仕様
	•	ノード：都道府県名
	•	エッジ：地理的な隣接関係（双方向・無向グラフ）
	•	推論順序：隣接ノード数が少ないノードから順に処理（情報伝播を段階的に可能にする）

### スコア出力仕様
	•	出力形式（JSON）：
```json
{
 "agent": "Tokyo",
 "liking": 4.2,
 "purchase_intent": 3.8,
 "neighbors_used": ["Chiba", "Saitama"],
 "commentary": "健康意識の高い人には響くが、価格面での魅力がやや弱い"
}
```

### 評価対象のコンテンツ
	•	広告文（テキスト）
	•	レポート・スライド（マルチモーダル拡張余地あり）


### フロントエンド想定（別プロジェクトでも構わない）
	•	Streamlit または Next.js + REST API連携
	•	地図連携ヒートマップ表示（Kepler.gl などの地理可視化ツールも検討）

### 今後の拡張
	•	実データとの照合によるAgent精度改善
	•	地域内伝播モデルの導入（SIR, GNN等）
```
