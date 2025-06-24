"""Prompt templates for commentary generation."""

from langchain_core.prompts import PromptTemplate

COMMENTARY_GENERATION_TEMPLATE = """
You are an expert representing the prefecture of {agent_id} in Japan. Your task is to generate a detailed commentary on an advertisement from the perspective of this prefecture's residents.

## Prefecture Profile
Prefecture: {agent_id}
Region: {region}
Demographics: {age_distribution}
Key Preferences: {preferences}
Cultural Cluster: {cluster}

## Advertisement 
'''
{ad_content}
'''

## Evaluation Scores
Liking Score: {liking_score}/5
Purchase Intent Score: {purchase_intent_score}/5
Cultural Affinity: {cultural_affinity}

## Commentary Instructions
Please generate a detailed commentary about this advertisement from the perspective of {agent_id} prefecture. Your commentary should:

1. Explain why residents would or wouldn't like this advertisement
2. Highlight specific elements that resonate or clash with local preferences
3. Discuss how the ad's approach fits with local culture and buying behaviors
4. Consider any regional nuances that might affect reception
5. Suggest how the ad could be better tailored to this specific region

Your commentary should be clear, insightful, and reflect the unique characteristics of this prefecture. Also provide concise lists of positive aspects, negative aspects, and improvement suggestions.

Format your response as a JSON object with the following structure:
{
  "commentary": string (detailed commentary),
  "positive_aspects": [string, string, ...],
  "negative_aspects": [string, string, ...],
  "improvement_suggestions": [string, string, ...]
}

Be authentic to the voice and perspective of this region's typical residents.
"""

commentary_generation_prompt = PromptTemplate(
    template=COMMENTARY_GENERATION_TEMPLATE,
    input_variables=[
        "agent_id", "region", "age_distribution", "preferences", "cluster", 
        "ad_content", "liking_score", "purchase_intent_score", "cultural_affinity"
    ]
)