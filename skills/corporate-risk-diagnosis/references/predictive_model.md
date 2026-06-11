# Accounts Receivable (AR) Default Prediction Model

## 1. Core Predictive Indicators (Benchmarking Palantir/C3)
- **DSO (Days Sales Outstanding)**: Trend analysis of payment delays.
- **Credit Score Volatility**: Real-time monitoring of corporate credit rating shifts.
- **Sentiment Shift**: Negative news in legal or financial domains (from MCP sources).
- **Macro-Headwinds**: Industry-specific downturns (from FRED/BLS).
- **Z-Score Degradation**: Rapid decline in financial health indicators.

## 2. Threshold & Alert Logic
- **Critical (Red)**: Predicted Default Probability > 70% OR OFAC Sanction Hit.
  *   *Action*: Immediate halt of credit extensions; trigger legal collection protocol.
- **Warning (Yellow)**: DSO increase > 20% in 30 days OR Significant new litigation.
  *   *Action*: Reduce credit limit; request collateral.
- **Observational (Blue)**: Macro-economic sector downgrade.
  *   *Action*: Quarterly review.

## 3. Dynamic Monitoring Workflow
1.  **Subscription**: User selects a company for 24/7 monitoring.
2.  **Continuous Polling**: Agent periodically runs a 'Lite' version of the diagnosis across MCP sources.
3.  **Predictive Inference**: Gemini 3.5 Flash processes the delta (changes) to predict default risk.
4.  **Notification**: Push alert via UI with specific 'Risk Mitigation Actions'.
