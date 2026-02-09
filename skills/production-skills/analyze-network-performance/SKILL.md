# Skill: Analyze Network Performance

## Domain
telecommunications

## Description
Analyzes telecommunications network performance metrics identifying bottlenecks, quality issues, and optimization opportunities.

## Tags
telecom, network, performance, QoS, monitoring, optimization

## Use Cases
- Network health monitoring
- QoS analysis
- Capacity planning
- Fault identification

## Proprietary Business Rules

### Rule 1: KPI Threshold Analysis
Network KPI evaluation against thresholds.

### Rule 2: Trend Detection
Performance degradation trend identification.

### Rule 3: Root Cause Analysis
Issue root cause determination.

### Rule 4: Capacity Forecasting
Network capacity projection.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `network_metrics` (list): Performance measurements
- `topology_data` (dict): Network topology
- `traffic_data` (list): Traffic patterns
- `threshold_config` (dict): Performance thresholds
- `time_range` (dict): Analysis period

## Output
- `health_score` (float): Network health rating
- `kpi_analysis` (dict): KPI performance summary
- `issues_detected` (list): Performance issues
- `trend_analysis` (dict): Performance trends
- `recommendations` (list): Optimization actions

## Implementation
The analysis logic is implemented in `network_analyzer.py` and references data from CSV files:
- `performance_metrics.csv` - Reference data
- `application_requirements.csv` - Reference data
- `capacity_planning.csv` - Reference data
- `sla_definitions.csv` - Reference data
- `alert_thresholds.csv` - Reference data
- `baseline_deviation.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from network_analyzer import analyze_network

result = analyze_network(
    analysis_id="NET-001",
    network_metrics=[{"metric": "latency_ms", "value": 25, "node": "router_1"}],
    topology_data={"nodes": 50, "links": 75, "type": "mesh"},
    traffic_data=[{"timestamp": "2025-12-15T10:00", "throughput_gbps": 8.5}],
    threshold_config={"latency_warning": 30, "latency_critical": 50},
    time_range={"start": "2025-12-15", "end": "2025-12-16"}
)

print(f"Network Health: {result['health_score']}")
```

## Test Execution
```python
from network_analyzer import analyze_network

result = analyze_network(
    analysis_id=input_data.get('analysis_id'),
    network_metrics=input_data.get('network_metrics', []),
    topology_data=input_data.get('topology_data', {}),
    traffic_data=input_data.get('traffic_data', []),
    threshold_config=input_data.get('threshold_config', {}),
    time_range=input_data.get('time_range', {})
)
```
