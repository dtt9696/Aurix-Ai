# Corporate Risk Diagnosis Multi-Source Strategy

To ensure data integrity and prevent single-point-of-failure or hallucination, the agent must cross-verify data across at least THREE distinct sources for each domain.

## 1. Financial Data (SEC & Market)
- **Primary**: SEC EDGAR (via `sec-edgar-mcp` or `financialdatasets-mcp`).
- **Secondary**: Alpha Vantage (Market pricing, fundamentals).
- **Consensus**: Yahoo Finance / Google Finance (Real-time pricing, consensus estimates).
- **Verification Rule**: Compare Revenue/Net Income across SEC filings and third-party aggregators.

## 2. Judicial & Litigation (司法涉诉)
- **Primary**: CourtListener (RECAP) - Federal dockets and opinions.
- **Secondary**: PACER (via `companylens-mcp`) - Direct federal court access.
- **Consensus**: Law360 / Justia (via `google_search`) - Legal news and case summaries.
- **Verification Rule**: Confirm case status and case numbers across at least two legal databases.

## 3. Sanctions & Compliance (制裁/合规)
- **Primary**: OFAC (US Treasury) SDN/SSI Lists.
- **Secondary**: OpenSanctions (via `companylens-mcp`) - Global sanctions and PEP check.
- **Consensus**: UN/EU Sanctions Lists (Cross-border compliance check).
- **Verification Rule**: A "Match" in any primary list triggers a Red Alert; use secondary lists to identify indirect nexus.

## 4. News & Sentiment
- **Primary**: Financial Datasets News API.
- **Secondary**: Google News / GNews.
- **Consensus**: X (Twitter) / Specialized Industry News (via `google_search`).
- **Verification Rule**: Look for "Triangulated Reports" – the same event reported by three different publishers.

## 5. Macro & Sector
- **Primary**: FRED (Federal Reserve).
- **Secondary**: BLS (Bureau of Labor Statistics).
- **Consensus**: World Bank / OECD US Data.
- **Verification Rule**: Cross-verify interest rate or inflation impacts across central bank and statistical bureau data.
