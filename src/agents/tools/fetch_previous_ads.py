"""Tool for fetching previous advertisements."""

from datetime import datetime, timedelta

from src.agents.schemas.tools.fetch_previous_ads import (
    AdRecord,
    FetchPreviousAdsInput,
    FetchPreviousAdsOutput,
)
from src.agents.tools.base import BaseAgentTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FetchPreviousAds(BaseAgentTool[FetchPreviousAdsInput, FetchPreviousAdsOutput]):
    """Tool for fetching previous advertisements."""

    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="fetch_previous_ads",
            description="Fetch previous advertisements with optional filtering. Requires agent_id. Optional: category, brand, limit.",
        )

        # Mock ads database
        current_date = datetime.now()
        self.mock_ads = [
            {
                "ad_id": "ad_001",
                "ad_content": "新しいスマートフォンが登場！最新技術で快適な生活を。",
                "category": "technology",
                "brand": "TechCorp",
                "created_date": (current_date - timedelta(days=30)).isoformat(),
                "liking_scores": {"Tokyo": 4.2, "Osaka": 3.8, "Kyoto": 3.5, "Hokkaido": 3.0},
                "purchase_intent_scores": {"Tokyo": 3.9, "Osaka": 3.4, "Kyoto": 3.1, "Hokkaido": 2.8},
            },
            {
                "ad_id": "ad_002",
                "ad_content": "本格的な味わいのラーメンをご自宅で。伝統の製法で作りました。",
                "category": "food",
                "brand": "NoodleMaster",
                "created_date": (current_date - timedelta(days=25)).isoformat(),
                "liking_scores": {"Tokyo": 3.5, "Osaka": 4.5, "Kyoto": 4.0, "Hokkaido": 3.2},
                "purchase_intent_scores": {"Tokyo": 3.2, "Osaka": 4.2, "Kyoto": 3.8, "Hokkaido": 3.0},
            },
            {
                "ad_id": "ad_003",
                "ad_content": "京都の職人が手作りする伝統工芸品。美しさと実用性を兼ね備えています。",
                "category": "crafts",
                "brand": "KyotoCrafts",
                "created_date": (current_date - timedelta(days=20)).isoformat(),
                "liking_scores": {"Tokyo": 3.8, "Osaka": 3.2, "Kyoto": 4.7, "Hokkaido": 3.5},
                "purchase_intent_scores": {"Tokyo": 3.0, "Osaka": 2.8, "Kyoto": 4.2, "Hokkaido": 3.1},
            },
            {
                "ad_id": "ad_004",
                "ad_content": "北海道の大自然で育った新鮮な海産物をお届け。自然の恵みをそのまま。",
                "category": "food",
                "brand": "HokkaidoFresh",
                "created_date": (current_date - timedelta(days=15)).isoformat(),
                "liking_scores": {"Tokyo": 4.0, "Osaka": 3.6, "Kyoto": 3.8, "Hokkaido": 4.8},
                "purchase_intent_scores": {"Tokyo": 3.7, "Osaka": 3.3, "Kyoto": 3.5, "Hokkaido": 4.5},
            },
            {
                "ad_id": "ad_005",
                "ad_content": "忙しい毎日に便利なオンラインサービス。24時間いつでもご利用可能。",
                "category": "service",
                "brand": "ConvenienceNow",
                "created_date": (current_date - timedelta(days=10)).isoformat(),
                "liking_scores": {"Tokyo": 4.3, "Osaka": 3.9, "Kyoto": 3.4, "Hokkaido": 3.1},
                "purchase_intent_scores": {"Tokyo": 4.0, "Osaka": 3.6, "Kyoto": 3.1, "Hokkaido": 2.9},
            },
            {
                "ad_id": "ad_006",
                "ad_content": "伝統的な和菓子の味を現代に。職人の技と心を込めて作りました。",
                "category": "food",
                "brand": "TraditionalSweets",
                "created_date": (current_date - timedelta(days=8)).isoformat(),
                "liking_scores": {"Tokyo": 3.6, "Osaka": 3.8, "Kyoto": 4.4, "Hokkaido": 3.3},
                "purchase_intent_scores": {"Tokyo": 3.2, "Osaka": 3.5, "Kyoto": 4.0, "Hokkaido": 3.0},
            },
            {
                "ad_id": "ad_007",
                "ad_content": "最新のファッショントレンドをお手頃価格で。スタイリッシュな毎日を。",
                "category": "fashion",
                "brand": "StyleForward",
                "created_date": (current_date - timedelta(days=5)).isoformat(),
                "liking_scores": {"Tokyo": 4.1, "Osaka": 3.7, "Kyoto": 3.2, "Hokkaido": 2.9},
                "purchase_intent_scores": {"Tokyo": 3.8, "Osaka": 3.4, "Kyoto": 2.9, "Hokkaido": 2.6},
            },
            {
                "ad_id": "ad_008",
                "ad_content": "家族で楽しめる温泉旅行プラン。リラックスできる時間をお過ごしください。",
                "category": "travel",
                "brand": "RelaxResorts",
                "created_date": (current_date - timedelta(days=3)).isoformat(),
                "liking_scores": {"Tokyo": 3.9, "Osaka": 4.1, "Kyoto": 4.3, "Hokkaido": 4.6},
                "purchase_intent_scores": {"Tokyo": 3.5, "Osaka": 3.8, "Kyoto": 4.0, "Hokkaido": 4.2},
            },
        ]

    async def execute(self, input_data: FetchPreviousAdsInput) -> FetchPreviousAdsOutput:
        """Execute the tool to fetch previous advertisements.

        Args:
            input_data: Input containing fetch criteria

        Returns:
            Output containing previous ads
        """
        agent_id = input_data.agent_id
        category_filter = input_data.category
        brand_filter = input_data.brand
        limit = input_data.limit or 10

        try:
            logger.info(
                f"Fetching previous ads for {agent_id} with filters: category={category_filter}, brand={brand_filter}"
            )

            # Apply filters
            filtered_ads = self.mock_ads.copy()
            filters_applied = {}

            if category_filter:
                filtered_ads = [ad for ad in filtered_ads if ad["category"].lower() == category_filter.lower()]
                filters_applied["category"] = category_filter

            if brand_filter:
                filtered_ads = [
                    ad for ad in filtered_ads if ad["brand"] and ad["brand"].lower() == brand_filter.lower()
                ]
                filters_applied["brand"] = brand_filter

            # Apply limit
            total_count = len(filtered_ads)
            filtered_ads = filtered_ads[:limit]
            filters_applied["limit"] = limit

            # Convert to AdRecord objects
            ad_records = []
            for ad_data in filtered_ads:
                ad_record = AdRecord(
                    ad_id=ad_data["ad_id"],
                    ad_content=ad_data["ad_content"],
                    category=ad_data["category"],
                    brand=ad_data.get("brand"),
                    created_date=ad_data["created_date"],
                    liking_scores=ad_data.get("liking_scores", {}),
                    purchase_intent_scores=ad_data.get("purchase_intent_scores", {}),
                )
                ad_records.append(ad_record)

            logger.info(f"Fetched {len(ad_records)} ads for {agent_id} (total matching: {total_count})")

            return FetchPreviousAdsOutput(
                success=True, ads=ad_records, total_count=total_count, filters_applied=filters_applied
            )

        except Exception as e:
            logger.error(f"Error fetching previous ads for {agent_id}: {e}")
            return FetchPreviousAdsOutput(
                success=False,
                message=f"Failed to fetch previous ads: {str(e)}",
                ads=[],
                total_count=0,
                filters_applied={},
            )
