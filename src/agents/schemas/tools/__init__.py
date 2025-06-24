"""Schema exports for agent tools."""

from .access_local_statistics import AccessLocalStatisticsInput, AccessLocalStatisticsOutput
from .analyze_ad_content import AnalyzeAdContentInput, AnalyzeAdContentOutput
from .base import ToolInput, ToolOutput
from .calculate_aggregate_score import CalculateAggregateScoreInput, CalculateAggregateScoreOutput
from .estimate_cultural_affinity import (
    AlignmentFactor,
    EstimateCulturalAffinityInput,
    EstimateCulturalAffinityOutput,
)
from .fetch_previous_ads import AdRecord, FetchPreviousAdsInput, FetchPreviousAdsOutput
from .generate_commentary import GenerateCommentaryInput, GenerateCommentaryOutput
from .log_score_to_db import LogScoreToDbInput, LogScoreToDbOutput
from .retrieve_neighbor_scores import NeighborScore, RetrieveNeighborScoresInput, RetrieveNeighborScoresOutput
from .validate_input_format import (
    ValidateInputFormatInput,
    ValidateInputFormatOutput,
    ValidationResult,
)

__all__ = [
    # Base schemas
    "ToolInput",
    "ToolOutput",
    # Access local statistics
    "AccessLocalStatisticsInput",
    "AccessLocalStatisticsOutput",
    # Analyze ad content
    "AnalyzeAdContentInput",
    "AnalyzeAdContentOutput",
    # Calculate aggregate score
    "CalculateAggregateScoreInput",
    "CalculateAggregateScoreOutput",
    # Estimate cultural affinity
    "AlignmentFactor",
    "EstimateCulturalAffinityInput",
    "EstimateCulturalAffinityOutput",
    # Fetch previous ads
    "AdRecord",
    "FetchPreviousAdsInput",
    "FetchPreviousAdsOutput",
    # Generate commentary
    "GenerateCommentaryInput",
    "GenerateCommentaryOutput",
    # Log score to db
    "LogScoreToDbInput",
    "LogScoreToDbOutput",
    # Retrieve neighbor scores
    "NeighborScore",
    "RetrieveNeighborScoresInput",
    "RetrieveNeighborScoresOutput",
    # Validate input format
    "ValidationResult",
    "ValidateInputFormatInput",
    "ValidateInputFormatOutput",
]
