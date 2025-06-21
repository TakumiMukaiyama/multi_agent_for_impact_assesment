from langchain_core.prompts import PromptTemplate

# Ad Evaluation Prompt
AD_EVALUATION_PROMPT = PromptTemplate.from_template(
    """
    あなたは{agent_id}の住民の特性を持つエージェントです。
    以下の広告に対して、{agent_id}の人々がどのように反応するかを評価してください。

    ## 広告情報
    - タイトル: {ad_title}
    - 内容: {ad_content}
    - カテゴリ: {ad_category}

    ## 評価指標
    - 好意度: 広告に対してどれだけ好意的な印象を持つか（0.0〜5.0の範囲）
    - 購買意欲: 広告を見てどれだけ購入したいと思うか（0.0〜5.0の範囲）

    ## {agent_id}の特性
    - 地域: {region}
    - 年齢構成: {age_distribution}
    - 好み: {preferences}

    以上の情報を元に、{agent_id}の住民視点での広告評価を行ってください。
    評価結果はJSON形式で、以下のキーを含めてください：
    - agent_id: 評価を行ったエージェントID
    - ad_id: 評価対象の広告ID
    - liking: 好意度スコア（0.0〜5.0）
    - purchase_intent: 購買意欲スコア（0.0〜5.0）
    - neighbors_used: 参照した隣接エージェントのID一覧（該当する場合）
    - commentary: 評価結果に関する簡潔な説明

    必ず指定された形式で出力してください。
    """
)

# Ad Content Analysis Prompt
AD_CONTENT_ANALYSIS_PROMPT = PromptTemplate.from_template(
    """
    以下の広告コンテンツを分析し、その主要な特徴や要素を抽出してください。

    ## 広告情報
    - ID: {ad_id}
    - タイトル: {ad_title}
    - 内容: {ad_content}
    - カテゴリ: {ad_category}

    広告の内容を詳細に分析し、以下の点について情報を抽出してください：
    - 主要カテゴリ
    - 副次的カテゴリ
    - ターゲットとなる人口統計グループ（年齢層、性別など）とその関連度（0.0〜1.0）
    - 主要テーマや論点
    - キーとなる便益や価値提案
    - 感情的訴求とその強度（0.0〜1.0）
    - 文化的文脈や参照
    - 全体的なトーン
    - 行動喚起（もしあれば）

    分析結果はJSON形式で提供してください。すべての数値評価は0.0から1.0の間で表現してください。
    """
)

# Cultural Affinity Prompt
CULTURAL_AFFINITY_PROMPT = PromptTemplate.from_template(
    """
    広告と{agent_id}の地域特性との文化的親和性を評価してください。

    ## 広告情報
    - ID: {ad_id}
    - 内容: {ad_content}

    ## {agent_id}のプロファイル
    {agent_profile}

    広告の内容と{agent_id}の地域特性を比較し、以下の観点から文化的親和性を評価してください：
    - 全体的な親和性スコア（0.0〜1.0）
    - 人口統計セグメントごとの適合度（0.0〜1.0）
    - 嗜好カテゴリごとの適合度（0.0〜1.0）
    - 地域特有の特性に対する関連性（0.0〜1.0）
    - 評価の詳細な説明

    すべての評価スコアは0.0から1.0の間で表現し、結果をJSON形式で提供してください。
    """
)

# Commentary Generation Prompt
COMMENTARY_GENERATION_PROMPT = PromptTemplate.from_template(
    """
    {agent_id}の視点から、以下の広告に対する自然言語コメントを生成してください。

    ## 広告情報
    - ID: {ad_id}
    - 内容: {ad_content}

    ## {agent_id}のプロファイル
    {agent_profile}

    ## 評価スコア
    - 好意度: {liking_score}（0.0〜5.0）
    - 購買意欲: {purchase_intent_score}（0.0〜5.0）

    このスコアを説明する自然な文体のコメントを生成してください。コメントには以下の要素を含めてください：
    - 広告に対する全体的な印象
    - 広告の肯定的な側面
    - 改善できる否定的な側面
    - 地域特有の観点からの洞察

    結果はJSON形式で提供し、以下のキーを含めてください：
    - agent_id: コメントを生成したエージェントID
    - ad_id: 評価対象の広告ID
    - commentary: 全体的なコメント
    - positive_aspects: 肯定的な側面の説明
    - negative_aspects: 否定的な側面の説明
    - local_perspective: 地域特有の観点
    """
)

# Aggregate Score Prompt
AGGREGATE_SCORE_PROMPT = PromptTemplate.from_template(
    """
    {agent_id}と隣接地域のスコアから集計スコアを計算してください。

    ## エージェント情報
    - エージェントID: {agent_id}
    - 広告ID: {ad_id}
    
    ## スコア情報
    - 自身のスコア: {own_scores}
    - 隣接地域のスコア: {neighbor_scores}
    - ウェイト（オプション）: {weights}

    自身のスコアと隣接地域のスコアを加重平均して、集計スコアを計算してください。
    集計結果には以下の要素を含めてください：
    - agent_id: 集計を行ったエージェントID
    - ad_id: 評価対象の広告ID
    - aggregate_liking: 集計された好意度スコア（0.0〜5.0）
    - aggregate_purchase_intent: 集計された購買意欲スコア（0.0〜5.0）
    - weights_used: 計算に使用したウェイト
    - neighbors_used: 計算に使用した隣接地域のID一覧

    結果はJSON形式で提供してください。
    """
)