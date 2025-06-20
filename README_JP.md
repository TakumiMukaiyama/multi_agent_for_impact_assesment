# マルチエージェント効果測定システム

日本の異なる地理的地域における広告効果をシミュレーションおよび予測するためのグラフベースのマルチエージェントシステムです。このシステムは日本の47都道府県を、地域特性に基づいた個別のペルソナを持つ個別のLLMエージェントとしてモデル化しています。

## 概要

このシステムはグラフとマルチエージェントLLMアーキテクチャを組み合わせて、広告効果を分析・予測します。各都道府県エージェントは地域の人口統計データに基づいて広告を評価し、日本の地理的隣接関係を表すグラフ構造を通じて隣接する都道府県に影響を与えることができます。

主な機能：
- 固有のペルソナと特性を持つ47都道府県ベースのLLMエージェント
- 隣接地域間の影響のグラフベースシミュレーション
- 好意度と購買意欲に基づく広告評価スコアリング
- MongoDBとPostgreSQLデータストレージを備えたFastAPIバックエンド

## 技術スタック

- **フレームワーク**: FastAPI
- **エージェントフレームワーク**: LangChain
- **グラフ処理**: NetworkX
- **並列処理**: Ray
- **データベース**: MongoDB & PostgreSQL
- **設定**: Pydantic
- **LLM統合**: 複数のプロバイダーサポート（OpenAI、Azure OpenAI、Google Gemini）

## 使い方

### 前提条件

- Python 3.12+
- MongoDB
- PostgreSQL

### インストール

1. リポジトリのクローン
```bash
git clone https://github.com/TakumiMukaiyama/multi_agent_for_impact_assesment.git
cd multi_agent_for_impact_assesment
```

2. 仮想環境のセットアップ
```bash
python -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
```

3. 依存関係のインストール
```bash
uv sync
```

4. .envファイルの作成と設定
```bash
cp sample.env .env
# .envファイルを自分の設定情報で編集してください
```

5. アプリケーションの実行
```bash
python main.py
```

APIは http://localhost:8000 で利用可能になります。

## プロジェクト構造

```
project_root/
├── Dockerfile         # FastAPI + エージェントサービスのDockerコンフィグ
├── docker-compose.yml # MongoDB、Ray、WebAPI統合
├── pyproject.toml     # プロジェクト依存関係
├── .env               # DB接続情報とAPIキー
├── README.md
└── src/
    ├── main.py           # FastAPIエントリーポイント
    ├── api/              # APIルーティング
    │   ├── router.py
    │   └── v1/
    │       ├── agent.py  # /agentsエンドポイント
    │       ├── ad.py     # /adsエンドポイント
    │       └── graph.py  # /graphエンドポイント
    ├── core/             # グラフ構築、静的初期化
    │   ├── llm_settings.py
    │   ├── db_settings.py
    │   └── app_settings.py
    ├── agents/           # エージェント実装
    │   ├── base.py
    │   ├── persona_factory.py
    │   ├── registry.py
    │   └── tools/        # エージェントツール
    ├── db/               # データベースモデルとクライアント
    ├── services/         # ドメインロジック
    └── utils/            # ヘルパーモジュール
```

## APIエンドポイント

APIには以下の主要なエンドポイントが含まれています：

- `/api/v1/agents` - 都道府県エージェントの管理
- `/api/v1/ads` - 広告の管理
- `/api/v1/graph` - グラフ構造へのアクセス
- `/health` - サービスの健全性確認

## エージェントシステム

各都道府県エージェントは以下を備えています：
- 人口統計プロファイル（年齢分布、嗜好）
- 地域特性
- ローカルおよび隣接データにアクセスするためのツール

エージェントは広告を以下の観点で評価します：
- 好意度（0.0〜5.0のスケール）
- 購入意欲（0.0〜5.0のスケール）
- 評価を説明するコメンタリー付き

## データベース設計

システムはMongoDBとPostgreSQLの両方を使用します：

### MongoDB
- 柔軟なJSONベースのデータ
- エージェント出力、エージェント構成、広告ログ

### PostgreSQL
- 分析用の構造化データ
- 広告メタデータ、統計データ、ユーザーフィードバック

## 今後の開発予定

- エージェント精度向上のための実データ統合
- 地域内伝播モデル（SIR、GNNなど）
- マップベースのヒートマップを用いたフロントエンド視覚化
- マルチモーダル広告分析（画像、音声）

## ライセンス

[MIT]