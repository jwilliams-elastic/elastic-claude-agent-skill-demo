# Analyze Sentiment Risk

## Description
Analyzes text sentiment from various sources (social media, news, customer feedback) to identify reputation and market risks for businesses.

## Domain
Financial Services / Risk Management

## Use Cases
- Brand reputation monitoring
- Market sentiment analysis
- Customer feedback risk assessment
- Crisis early warning detection
- Investor sentiment tracking

## Input Parameters
- `analysis_id`: Unique analysis identifier
- `entity_name`: Company or brand being analyzed
- `text_sources`: List of text content with source metadata
- `historical_baseline`: Historical sentiment baseline for comparison
- `alert_thresholds`: Custom alert threshold settings
- `analysis_date`: Date of analysis

## Output
- Sentiment scores by source and topic
- Risk level classification
- Trend analysis vs baseline
- Alert triggers
- Recommended actions

## Business Rules
1. Aggregate sentiment from multiple sources with source-specific weighting
2. Apply industry-specific risk thresholds
3. Detect sudden sentiment shifts that may indicate emerging issues
4. Calculate composite risk score based on sentiment, volume, and velocity
5. Generate alerts when thresholds are breached
