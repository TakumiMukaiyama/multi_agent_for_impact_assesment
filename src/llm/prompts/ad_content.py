"""Prompt templates for ad content analysis."""

from langchain_core.prompts import PromptTemplate

AD_CONTENT_ANALYSIS_TEMPLATE = """
You are an expert ad content analyzer. Your task is to analyze the following advertisement and provide a structured breakdown of its characteristics.

## Advertisement to Analyze
Advertisement ID: {ad_id}

Advertisement Content:
'''
{ad_content}
'''

## Analysis Instructions
Please analyze this advertisement for the following elements:

1. Category: What is the main product/service category? (e.g., "food", "technology", "healthcare", etc.)

2. Subcategories: What specific subcategories does it belong to? (e.g., "organic food", "smartphone", "skincare")

3. Target Demographics: Who appears to be the target audience? Consider age groups, lifestyle, income level, etc.

4. Key Selling Points: What are the main features or benefits emphasized in the ad?

5. Emotional Appeals: What emotions or values does the ad try to invoke? (e.g., "luxury", "nostalgia", "security", "health", "status")

6. Tone: What is the overall tone of the ad? (e.g., "informative", "humorous", "urgent", "inspirational", etc.)

7. Price Emphasis: On a scale from 0.0 to 1.0, how much does the ad emphasize price or value? (0 = no mention, 1 = primary focus)

8. Quality Emphasis: On a scale from 0.0 to 1.0, how much does the ad emphasize quality or premium attributes? (0 = no mention, 1 = primary focus)

Format your response as a JSON object with the following structure:
{
  "category": string,
  "subcategories": [string, string, ...],
  "target_demographic": [string, string, ...],
  "key_selling_points": [string, string, ...],
  "emotional_appeal": [string, string, ...],
  "tone": string,
  "price_emphasis": float (0.0-1.0),
  "quality_emphasis": float (0.0-1.0)
}

Be as specific and accurate as possible in your analysis.
"""

ad_content_analysis_prompt = PromptTemplate(
    template=AD_CONTENT_ANALYSIS_TEMPLATE,
    input_variables=["ad_id", "ad_content"]
)