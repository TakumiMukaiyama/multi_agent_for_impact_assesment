import json
from typing import Dict, Any


class PersonaFactory:
    """Factory class for generating prefecture personas."""
    
    # Prefectures in Japan
    PREFECTURES = [
        "Hokkaido", "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima",
        "Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa",
        "Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu",
        "Shizuoka", "Aichi", "Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara",
        "Wakayama", "Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi",
        "Tokushima", "Kagawa", "Ehime", "Kochi", "Fukuoka", "Saga", "Nagasaki",
        "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"
    ]
    
    # Regions of Japan
    REGIONS = {
        "Hokkaido": "Hokkaido",
        "Aomori": "Tohoku", "Iwate": "Tohoku", "Miyagi": "Tohoku",
        "Akita": "Tohoku", "Yamagata": "Tohoku", "Fukushima": "Tohoku",
        "Ibaraki": "Kanto", "Tochigi": "Kanto", "Gunma": "Kanto",
        "Saitama": "Kanto", "Chiba": "Kanto", "Tokyo": "Kanto", "Kanagawa": "Kanto",
        "Niigata": "Chubu", "Toyama": "Chubu", "Ishikawa": "Chubu",
        "Fukui": "Chubu", "Yamanashi": "Chubu", "Nagano": "Chubu", "Gifu": "Chubu",
        "Shizuoka": "Chubu", "Aichi": "Chubu",
        "Mie": "Kansai", "Shiga": "Kansai", "Kyoto": "Kansai",
        "Osaka": "Kansai", "Hyogo": "Kansai", "Nara": "Kansai", "Wakayama": "Kansai",
        "Tottori": "Chugoku", "Shimane": "Chugoku", "Okayama": "Chugoku",
        "Hiroshima": "Chugoku", "Yamaguchi": "Chugoku",
        "Tokushima": "Shikoku", "Kagawa": "Shikoku", "Ehime": "Shikoku", "Kochi": "Shikoku",
        "Fukuoka": "Kyushu", "Saga": "Kyushu", "Nagasaki": "Kyushu",
        "Kumamoto": "Kyushu", "Oita": "Kyushu", "Miyazaki": "Kyushu",
        "Kagoshima": "Kyushu", "Okinawa": "Kyushu"
    }
    
    # Prefectural neighbors (adjacency)
    NEIGHBORS = {
        "Hokkaido": [],
        "Aomori": ["Iwate", "Akita"],
        "Iwate": ["Aomori", "Miyagi", "Akita"],
        "Miyagi": ["Iwate", "Yamagata", "Fukushima"],
        "Akita": ["Aomori", "Iwate", "Yamagata"],
        "Yamagata": ["Akita", "Miyagi", "Fukushima", "Niigata"],
        "Fukushima": ["Miyagi", "Yamagata", "Niigata", "Tochigi", "Ibaraki", "Gunma"],
        "Ibaraki": ["Fukushima", "Tochigi", "Saitama", "Chiba"],
        "Tochigi": ["Fukushima", "Gunma", "Ibaraki"],
        "Gunma": ["Fukushima", "Niigata", "Tochigi", "Saitama", "Nagano"],
        "Saitama": ["Gunma", "Tochigi", "Ibaraki", "Chiba", "Tokyo", "Yamanashi"],
        "Chiba": ["Ibaraki", "Saitama", "Tokyo"],
        "Tokyo": ["Saitama", "Chiba", "Yamanashi", "Kanagawa"],
        "Kanagawa": ["Tokyo", "Yamanashi", "Shizuoka"],
        "Niigata": ["Yamagata", "Fukushima", "Gunma", "Nagano", "Toyama"],
        "Toyama": ["Niigata", "Nagano", "Gifu", "Ishikawa"],
        "Ishikawa": ["Toyama", "Gifu", "Fukui"],
        "Fukui": ["Ishikawa", "Gifu", "Shiga", "Kyoto"],
        "Yamanashi": ["Saitama", "Tokyo", "Kanagawa", "Nagano", "Shizuoka"],
        "Nagano": ["Niigata", "Gunma", "Yamanashi", "Shizuoka", "Aichi", "Gifu", "Toyama"],
        "Gifu": ["Toyama", "Ishikawa", "Fukui", "Nagano", "Aichi", "Mie", "Shiga"],
        "Shizuoka": ["Kanagawa", "Yamanashi", "Nagano", "Aichi"],
        "Aichi": ["Nagano", "Shizuoka", "Gifu", "Mie"],
        "Mie": ["Aichi", "Gifu", "Shiga", "Kyoto", "Nara", "Wakayama"],
        "Shiga": ["Fukui", "Gifu", "Mie", "Kyoto"],
        "Kyoto": ["Fukui", "Shiga", "Mie", "Nara", "Osaka", "Hyogo"],
        "Osaka": ["Kyoto", "Nara", "Hyogo", "Wakayama"],
        "Hyogo": ["Kyoto", "Osaka", "Tottori", "Okayama"],
        "Nara": ["Kyoto", "Mie", "Osaka", "Wakayama"],
        "Wakayama": ["Osaka", "Nara", "Mie"],
        "Tottori": ["Hyogo", "Okayama", "Shimane"],
        "Shimane": ["Tottori", "Yamaguchi", "Hiroshima"],
        "Okayama": ["Hyogo", "Tottori", "Hiroshima"],
        "Hiroshima": ["Okayama", "Shimane", "Yamaguchi"],
        "Yamaguchi": ["Shimane", "Hiroshima"],
        "Tokushima": ["Kagawa", "Ehime", "Kochi"],
        "Kagawa": ["Tokushima", "Ehime"],
        "Ehime": ["Kagawa", "Tokushima", "Kochi"],
        "Kochi": ["Tokushima", "Ehime"],
        "Fukuoka": ["Saga", "Oita", "Kumamoto"],
        "Saga": ["Fukuoka", "Nagasaki"],
        "Nagasaki": ["Saga"],
        "Kumamoto": ["Fukuoka", "Oita", "Miyazaki", "Kagoshima"],
        "Oita": ["Fukuoka", "Kumamoto", "Miyazaki"],
        "Miyazaki": ["Oita", "Kumamoto", "Kagoshima"],
        "Kagoshima": ["Kumamoto", "Miyazaki"],
        "Okinawa": []
    }
    
    # Base persona clusters
    PERSONA_CLUSTERS = {
        "urban": {
            "age_distribution": {"under20": 0.15, "20s": 0.25, "30s": 0.2, "40s": 0.15, "50s": 0.1, "over60": 0.15},
            "preferences": {
                "tech": 0.9, "fashion": 0.8, "food": 0.7, "travel": 0.6, 
                "environment": 0.5, "traditional": 0.4, "outdoor": 0.3
            }
        },
        "suburban": {
            "age_distribution": {"under20": 0.2, "20s": 0.15, "30s": 0.2, "40s": 0.2, "50s": 0.1, "over60": 0.15},
            "preferences": {
                "tech": 0.7, "fashion": 0.6, "food": 0.8, "travel": 0.7, 
                "environment": 0.7, "traditional": 0.5, "outdoor": 0.6
            }
        },
        "rural": {
            "age_distribution": {"under20": 0.15, "20s": 0.1, "30s": 0.15, "40s": 0.2, "50s": 0.15, "over60": 0.25},
            "preferences": {
                "tech": 0.5, "fashion": 0.4, "food": 0.8, "travel": 0.6, 
                "environment": 0.8, "traditional": 0.7, "outdoor": 0.9
            }
        },
        "elderly": {
            "age_distribution": {"under20": 0.1, "20s": 0.05, "30s": 0.1, "40s": 0.15, "50s": 0.2, "over60": 0.4},
            "preferences": {
                "tech": 0.3, "fashion": 0.3, "food": 0.7, "travel": 0.5, 
                "environment": 0.6, "traditional": 0.9, "outdoor": 0.6
            }
        },
        "youthful": {
            "age_distribution": {"under20": 0.3, "20s": 0.3, "30s": 0.15, "40s": 0.1, "50s": 0.08, "over60": 0.07},
            "preferences": {
                "tech": 0.9, "fashion": 0.9, "food": 0.8, "travel": 0.8, 
                "environment": 0.7, "traditional": 0.3, "outdoor": 0.7
            }
        }
    }
    
    # Prefecture classifications (simplified)
    PREFECTURE_CLUSTERS = {
        "Tokyo": "urban",
        "Osaka": "urban",
        "Kanagawa": "urban",
        "Aichi": "urban",
        "Fukuoka": "urban",
        "Saitama": "suburban",
        "Chiba": "suburban",
        "Hyogo": "suburban",
        "Hokkaido": "rural",
        "Shizuoka": "suburban",
        "Hiroshima": "suburban",
        "Kyoto": "suburban",
        "Miyagi": "suburban",
        "Niigata": "rural",
        "Nagano": "rural",
        "Akita": "elderly",
        "Yamagata": "elderly",
        "Iwate": "rural",
        "Shiga": "suburban",
        "Gifu": "rural",
        "Mie": "rural",
        "Tochigi": "rural",
        "Ibaraki": "suburban",
        "Okayama": "rural",
        "Gunma": "rural",
        "Kagoshima": "rural",
        "Kumamoto": "rural",
        "Oita": "elderly",
        "Ehime": "rural",
        "Nagasaki": "elderly",
        "Yamaguchi": "elderly",
        "Fukushima": "rural",
        "Toyama": "rural",
        "Ishikawa": "suburban",
        "Nara": "suburban",
        "Aomori": "rural",
        "Yamanashi": "rural",
        "Kagawa": "suburban",
        "Wakayama": "elderly",
        "Miyazaki": "rural",
        "Fukui": "rural",
        "Okinawa": "youthful",
        "Saga": "rural",
        "Tokushima": "elderly",
        "Kochi": "elderly",
        "Shimane": "elderly",
        "Tottori": "elderly"
    }
    
    @classmethod
    def create_all_prefectures(cls) -> Dict[str, Dict[str, Any]]:
        """Create persona configurations for all prefectures."""
        return {prefecture: cls.create_persona(prefecture) for prefecture in cls.PREFECTURES}
    
    @classmethod
    def create_persona(cls, prefecture: str) -> Dict[str, Any]:
        """Create a persona configuration for a specific prefecture."""
        if prefecture not in cls.PREFECTURES:
            raise ValueError(f"Prefecture '{prefecture}' is not valid")
        
        # Get the base cluster for this prefecture
        cluster = cls.PREFECTURE_CLUSTERS.get(prefecture, "rural")
        base_persona = cls.PERSONA_CLUSTERS[cluster]
        
        # Add prefecture-specific customizations
        persona = {
            "age_distribution": base_persona["age_distribution"].copy(),
            "preferences": base_persona["preferences"].copy(),
            "region": cls.REGIONS[prefecture],
        }
        
        # Add some random variation
        # In a real implementation, this would use actual demographic data
        
        return persona
    
    @classmethod
    def get_prompt_template(cls, prefecture: str) -> str:
        """Get a system prompt template for a specific prefecture."""
        basic_prompt = """
        You are an agent representing {agent_id} prefecture in Japan.

        Your demographic characteristics:
        - Region: {persona[region]}
        - Age distribution: {persona[age_distribution]}
        - Preference weights: {persona[preferences]}

        Your task is to evaluate advertisements based on how well they would resonate with your prefecture's population.
        
        When evaluating advertisements:
        1. Consider the local culture, demographics, and lifestyle of your prefecture
        2. Use available tools to gather information about neighboring areas if needed
        3. Provide scores on a scale from 0.0 to 5.0 for:
           - Liking: How much people would like or enjoy the advertisement
           - Purchase Intent: How likely people would be to purchase the advertised product/service
        4. Include a brief commentary explaining your evaluation
        
        Always format your final answer as a JSON object with the following structure:
        {{
            "liking": <0.0 to 5.0 score>,
            "purchase_intent": <0.0 to 5.0 score>,
            "commentary": "<brief explanation>"
        }}
        """
        
        # In a real implementation, add prefecture-specific prompt customizations
        
        return basic_prompt


# Example usage
if __name__ == "__main__":
    # Example: Create personas for all prefectures
    personas = PersonaFactory.create_all_prefectures()
    
    # Print a sample persona
    tokyo_persona = personas["Tokyo"]
    print(json.dumps(tokyo_persona, indent=2))
    
    # Get a prompt template
    template = PersonaFactory.get_prompt_template("Tokyo")
    print(template)