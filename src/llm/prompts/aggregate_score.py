"""Prompt templates for aggregate score calculation."""

from langchain_core.prompts import PromptTemplate

AGGREGATE_SCORE_TEMPLATE = """
You are an expert in regional market analysis in Japan. Your task is to calculate weighted aggregate scores that combine a prefecture's own evaluation with scores from neighboring prefectures.

## Agent Profile
Prefecture: {agent_id}
Region: {region}
Demographics: {age_distribution}
Key Preferences: {preferences}
Cultural Cluster: {cluster}

## Own Scores
Liking Score: {own_liking}/5
Purchase Intent Score: {own_purchase_intent}/5

## Neighbor Scores
{neighbor_scores_formatted}

## Task Instructions
Please calculate aggregate scores that combine the prefecture's own evaluation with weighted scores from neighboring prefectures. Your approach should:

1. Consider the cultural and demographic similarities between the central prefecture and its neighbors
2. Apply appropriate weights based on population, cultural overlap, or other relevant factors
3. Provide a clear explanation of your weighting methodology
4. Produce final aggregate scores for both liking and purchase intent (on the 0-5 scale)

Format your response as a JSON object with the following structure:
{
  "aggregate_liking": float (0.0-5.0),
  "aggregate_purchase_intent": float (0.0-5.0),
  "weighting_explanation": string,
  "neighbor_influence": {
    "neighbor_id1": float (weight),
    "neighbor_id2": float (weight),
    ...
  }
}

Ensure your weighting approach is logical and well-explained.
"""

aggregate_score_prompt = PromptTemplate(
    template=AGGREGATE_SCORE_TEMPLATE,
    input_variables=[
        "agent_id", "region", "age_distribution", "preferences", "cluster", 
        "own_liking", "own_purchase_intent", "neighbor_scores_formatted"
    ]
)