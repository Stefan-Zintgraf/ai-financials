# QUANTITATIVE RESEARCH PROJECT: MULTI-FACTOR EQUITY STRATEGY DEVELOPMENT

## MANDATE PARAMETERS

| Parameter | Specification |
|-----------|---------------|
| Strategy Type | Long-only enhanced index (S&P 500 benchmark) |
| AUM Capacity | $500 million |
| Benchmark | S&P 500 Total Return Index |
| Tracking Error Limit | 3% annualized (information ratio target &gt; 0.8) |
| Turnover Constraint | 100% annual (single-trip cost: 15bps) |
| Universe | S&P 500 constituents (rebalanced quarterly) |
| Sector Deviations | +/- 3% |
| Single Stock Limits | Max 5%, Min 0.5% |
| ESG Constraints | Exclude controversy score &lt; 30 (MSCI), carbon intensity top decile |

---

## DATA SETS PROVIDED

### HISTORICAL RETURNS (Last 10 Years, Monthly)

| Metric | Value |
|--------|-------|
| S&P 500 annualized return | 12.4% |
| S&P 500 volatility | 15.2% |
| Backtest period | January 2015 - December 2024 |
| Risk-free rate (avg) | 1.8% (3-month T-bill) |

---

## FACTOR DATA (Monthly Z-Scores, Cross-Sectionally Normalized)

### 1. VALUE FACTORS

| Factor | Historical IC | Characteristics |
|--------|---------------|-----------------|
| Book-to-Price (BP) | 0.02 | High volatility decay |
| Forward Earnings Yield (EY) | 0.03 | More stable than BP |
| Free Cash Flow Yield (FCFY) | 0.035 | Quality bias |
| Dividend Yield (DY) | 0.01 | Defensive characteristics |

### 2. QUALITY FACTORS

| Factor | Historical IC | Characteristics |
|--------|---------------|-----------------|
| Return on Equity (ROE) | 0.025 | High persistence |
| Gross Profitability (GP/A) | 0.03 | Novy-Marx factor |
| Earnings Quality (Accruals) | -0.02 | Negative = good |
| Balance Sheet Quality | 0.015 | Net Debt/EBITDA |

### 3. MOMENTUM FACTORS

| Factor | Historical IC | Characteristics |
|--------|---------------|-----------------|
| 12-1 Month Price Momentum (MOM12) | **0.04** | **Strongest factor** |
| 6-1 Month Price Momentum (MOM6) | 0.035 | Faster decay |
| Earnings Momentum (EPS Revision) | 0.03 | Fundamental anchor |
| Industry-Relative Momentum | 0.025 | Removes sector bias |

### 4. LOW VOLATILITY

| Factor | Historical IC | Characteristics |
|--------|---------------|-----------------|
| Beta (60-month) | -0.015 | Low beta outperforms |
| Idiosyncratic Volatility | -0.02 | |
| Maximum Drawdown (12-month) | 0.01 | |

### 5. GROWTH

| Factor | Historical IC | Characteristics |
|--------|---------------|-----------------|
| Sales Growth (3-year CAGR) | 0.01 | |
| EPS Growth (3-year CAGR) | 0.015 | |
| Long-term Growth Estimate | 0.005 | Noisy |

---

## FACTOR CORRELATION MATRIX (Average)

| | Value | Quality | Momentum | LowVol | Growth |
|---|-------|---------|----------|--------|--------|
| **Value** | 1.0 | 0.2 | -0.3 | 0.4 | -0.5 |
| **Quality** | 0.2 | 1.0 | 0.1 | 0.3 | 0.2 |
| **Momentum** | -0.3 | 0.1 | 1.0 | -0.2 | 0.4 |
| **LowVol** | 0.4 | 0.3 | -0.2 | 1.0 | -0.3 |
| **Growth** | -0.5 | 0.2 | 0.4 | -0.3 | 1.0 |

---

## CURRENT MARKET ENVIRONMENT (February 2025)

### FACTOR PERFORMANCE (Last 12 Months)

| Factor | Performance vs. Market |
|--------|------------------------|
| Value | +8% vs. growth |
| Quality | +3% vs. market |
| Momentum | +5% vs. market |
| Low Vol | -2% vs. market (underperforming) |
| Small Cap | -5% vs. large cap |

### MARKET REGIME INDICATORS

| Indicator | Value | Implication |
|-----------|-------|-------------|
| VIX | 18.5 | Moderate volatility |
| Credit Spreads | 95bps (tight) | Risk-on environment |
| Yield Curve | Normalized (positive slope) | Healthy financial conditions |
| Economic Cycle | Late expansion | GDP slowing but positive |
| Fed Policy | Paused | Potential cuts ahead |

### FACTOR CROWDING METRICS

| Factor | Crowding Percentile | Risk Assessment |
|--------|-------------------|-----------------|
| Value | 65% | Moderate crowding |
| Momentum | **85%** | **High crowding - reversal risk** |
| Quality | 40% | Low crowding |
| Low Vol | **90%** | **Very high crowding - bubble risk** |

---

## MACHINE LEARNING ENHANCEMENTS (Optional)

| Technique | Finding | Concern |
|-----------|---------|---------|
| Random Forest | Non-linear interactions between Value x Quality | Interpretability |
| Neural Network (3-layer) | IC improvement | Overfitting |
| NLP Sentiment | +1.5% annual alpha | Data cost |
| Alternative Data (credit card, satellite) | Unproven at scale | Expensive |

---

## RISK MODEL & TRANSACTION COSTS

### Risk Model
- **Model:** Barra USE4
- **Updates:** Monthly factor covariance matrix
- **Specific risk:** Individual stock estimates available

### Transaction Costs

| Component | Cost |
|-------------|------|
| Market impact | $0.05 per $1M traded |
| Spread costs | 5bps average (large caps) |
| Commission | 1bp |
| **Total round-trip** | **15bps** |

---

## TASK REQUIREMENTS

### 1. FACTOR RESEARCH & SELECTION

#### a) Analyze Each Factor
- [ ] Information coefficient (IC) persistence and decay
- [ ] Turnover implications (how often do signals change?)
- [ ] Capacity constraints (can it absorb $500M?)
- [ ] Cyclicality (when does it work/fail?)

#### b) Propose Factor Combination Methodology
- [ ] Equal weight vs. IC-weighted vs. optimization
- [ ] Timing: Static weights vs. dynamic regime switching
- [ ] Interaction terms (e.g., Value + Quality composite)

### 2. PORTFOLIO CONSTRUCTION

#### a) Alpha Model Design
- [ ] Specify exact factor combination formula
- [ ] Include transformations (winsorization, neutralization)
- [ ] Decay rates for different factors

#### b) Risk Model Integration
- [ ] Use Barra factor covariance for risk estimation
- [ ] Target tracking error: 3%
- [ ] Calculate required active share to achieve IR &gt; 0.8

#### c) Optimization Framework
- [ ] Mean-variance vs. risk parity vs. fundamental weighting
- [ ] Constraints handling (sector, position limits, turnover)
- [ ] Rebalancing frequency: Monthly vs. quarterly trade-off

### 3. BACKTESTING & PERFORMANCE ATTRIBUTION

#### a) Simulate Strategy Performance (2015-2024)
- [ ] Annualized return, volatility, Sharpe ratio
- [ ] Information ratio vs. S&P 500
- [ ] Maximum drawdown and recovery time
- [ ] Hit rate (months outperforming benchmark)

#### b) Attribution Analysis
- [ ] Factor contribution to returns (Brinson attribution)
- [ ] Sector allocation vs. stock selection effects
- [ ] Transaction cost drag analysis

#### c) Risk Analysis
- [ ] Factor exposure report (value, momentum, etc.)
- [ ] Drawdown attribution (which factors caused losses?)
- [ ] Tail risk: Skewness, kurtosis, VaR (95%)

### 4. IMPLEMENTATION DESIGN

#### a) Execution Strategy
- [ ] VWAP vs. implementation shortfall algorithms
- [ ] Trade scheduling across rebalancing days
- [ ] Handling of corporate actions and index changes

#### b) Operational Infrastructure
- [ ] Data requirements (vendors, frequency, cleaning)
- [ ] Model monitoring and decay detection
- [ ] Override protocols (when to deviate from model?)

### 5. CURRENT MARKET APPLICATION

- [ ] Adjust factor weights given high momentum crowding and low vol bubble risk
- [ ] Propose defensive positioning for late-cycle environment
- [ ] Identify specific sector tilts based on macro outlook

### 6. ADVANCED CONSIDERATIONS (Bonus)

- [ ] Machine learning integration: Random forest for stock selection?
- [ ] Alternative data: Cost-benefit analysis of credit card data
- [ ] ESG integration: Does it hurt expected returns? How to minimize drag?

---

## DELIVERABLES

1. **Strategy Blueprint** (3 pages): Concept, factors, construction rules
2. **Simulated Performance Report** (2015-2024): Returns, risk metrics, attribution
3. **Factor Exposure Dashboard**: Current portfolio characteristics
4. **Implementation Manual**: Data, execution, monitoring procedures
5. **Risk Management Framework**: Limits, stress tests, kill switches

---

## EVALUATION CRITERIA

- [ ] Statistical rigor in factor analysis and backtesting
- [ ] Understanding of transaction cost impact and capacity constraints
- [ ] Sophistication in portfolio optimization and risk management
- [ ] Practical implementation feasibility
- [ ] Awareness of overfitting and data mining risks
- [ ] Clarity in explaining quantitative concepts to non-technical stakeholders

---

*Prompt Version: 1.0 | Benchmark Category: Quantitative Strategy & Systematic Investing*
