"""Prompt templates for cultural affinity evaluation."""

from langchain_core.prompts import PromptTemplate

CULTURAL_AFFINITY_TEMPLATE = """
You are an expert in Japanese regional culture and consumer behavior. Your task is to evaluate how well an advertisement aligns with the cultural preferences and characteristics of a specific Japanese prefecture.

## Prefecture Profile
Prefecture: {agent_id}
Region: {region}
Population: {population}
Age Distribution: {age_distribution}
Key Preferences: {preferences}
Cultural Cluster: {cluster}
Urban/Rural Ratio: {urban_rural_ratio}
Consumer Trends: {consumer_trends}

## Advertisement to Evaluate
Advertisement Content:
'''
{ad_content}
'''

## Analysis Instructions
Please evaluate the cultural affinity between this advertisement and the prefecture's characteristics. Consider:

1. Overall Affinity Score: Provide a score from 0.0 to 1.0 indicating how well the ad aligns with this prefecture's culture and preferences (0 = completely misaligned, 1 = perfectly aligned)

2. Alignment Factors: List the specific cultural factors where the ad aligns well with the prefecture, each with a strength score (0.0-1.0)

3. Misalignment Factors: List the specific cultural factors where the ad doesn't align well with the prefecture, each with a strength score (0.0-1.0)

4. Regional Considerations: Provide additional context or considerations about how this ad might be received in this specific prefecture compared to others

Format your response as a JSON object with the following structure:
{
  "affinity_score": float (0.0-1.0),
  "alignment_factors": [
    {"factor": string, "strength": float (0.0-1.0)},
    ...
  ],
  "misalignment_factors": [
    {"factor": string, "strength": float (0.0-1.0)},
    ...
  ],
  "regional_considerations": string
}

Be thoughtful in your analysis, considering regional preferences, demographic characteristics, and cultural nuances.
"""

cultural_affinity_prompt = PromptTemplate(
    template=CULTURAL_AFFINITY_TEMPLATE,
    input_variables=[
        "agent_id", "region", "population", "age_distribution", 
        "preferences", "cluster", "urban_rural_ratio", 
        "consumer_trends", "ad_content"
    ]
)