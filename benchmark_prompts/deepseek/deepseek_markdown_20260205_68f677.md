# FINANCIAL BENCHMARK PROMPT #4: ADVANCED OPTIONS STRATEGY FOR PORTFOLIO HEDGING

## INSTRUCTIONS
Analyze the portfolio scenario and market conditions to recommend, price, and analyze options-based hedging strategies. Include Greek calculations and scenario analysis.

---

## PORTFOLIO SCENARIO
- **Portfolio Value**: $2,500,000
- **Primary Holdings**: 70% US Large Cap Tech/Healthcare
- **Current Beta (to S&P 500)**: 1.15
- **Portfolio Delta**: +$2,875,000
- **Portfolio Gamma**: -$45,000
- **Portfolio Vega**: +$85,000
- **Portfolio Theta**: +$3,200 (positive theta from existing options)

### SPECIFIC LARGE HOLDINGS
1. **Apple (AAPL)**: $350,000 (15,000 shares at $233.33)
2. **Microsoft (MSFT)**: $300,000 (8,000 shares at $375.00)
3. **NVIDIA (NVDA)**: $275,000 (2,000 shares at $137.50) *high volatility
4. **SPDR S&P 500 ETF (SPY)**: $750,000 (1,750 shares at $428.57)
5. **Various individual stocks**: $825,000

---

## MARKET CONDITIONS
- **S&P 500 Level**: 4,300
- **VIX Index**: 21.5
- **VIX Term Structure**: Contango (1-month: 21.5, 3-month: 23.1, 6-month: 24.8)
- **Risk-Free Rate**: 4.5%
- **Dividend Yield (S&P 500)**: 1.6%

### OPTIONS MARKET DATA
**SPY Options (30-day)**:
- ATM (430 strike) IV: 20.5%
- 5% OTM Put (408.5 strike) IV: 23.2%
- 5% OTM Call (451.5 strike) IV: 19.8%
- Put-Call Ratio: 1.45 (elevated)
- Skew (25-delta put IV / 25-delta call IV): 1.12

**Single Stock Options**:
- AAPL 30-day ATM IV: 28%
- MSFT 30-day ATM IV: 26%
- NVDA 30-day ATM IV: 52% (extremely elevated)

---

## INVESTOR OBJECTIVES & CONSTRAINTS
1. **Time Horizon**: 6-month hedge (earnings season + election uncertainty)
2. **Cost Constraint**: Maximum 2.5% of portfolio value ($62,500) for hedge premium
3. **Downside Protection Target**: Limit losses to maximum 15% in severe downturn (>20% market drop)
4. **Upside Participation**: Maintain at least 70% of portfolio upside if market rises
5. **Tax Considerations**: Holdings in taxable accounts (long-term gains)
6. **Regulatory**: No leverage beyond 2:1 (Reg T compliant)

---

## RISK SCENARIOS TO HEDGE
1. **Market Correction**: S&P 500 drops 15% over 3 months (VIX spikes to 35)
2. **Single Stock Event**: NVDA earnings miss (stock drops 25% overnight)
3. **Volatility Spike**: VIX doubles to 40+ (volatility shock)
4. **Sector Rotation**: Tech underperforms by 10% relative to market
5. **Geopolitical Event**: Sudden risk-off (flight to quality)

---

## EXISTING OPTIONS POSITIONS (to incorporate in analysis)
- **Covered Calls**: 500 SPY shares covered with 440 strike calls (45 DTE, +$8,500 premium collected)
- **Protective Puts**: 1,000 SPY shares protected with 410 strike puts (90 DTE, -$15,200 premium paid)
- **Ratio Spread**: NVDA 120/130 put spread (long 1x 120 put, short 2x 130 puts)

---

## ANALYSIS REQUEST

### 1. Strategy Selection
Recommend 2-3 multi-leg options strategies with rationale

### 2. Greeks Analysis
Calculate net portfolio Greeks after implementing hedge

### 3. Pricing & Execution
Specific strikes, expirations, and expected fill prices

### 4. Payoff Diagrams
Describe profit/loss profiles at key market levels

### 5. Scenario Analysis
Show hedge performance in 5 market scenarios:
   a. Market up 10% (bull case)
   b. Market down 10% (mild correction)
   c. Market down 25% (crash scenario)
   d. Volatility spike (VIX at 40) with flat market
   e. Tech sector underperformance (-15% relative)

### 6. Cost-Benefit
Compare hedge cost to expected value of protection

### 7. Rolling Strategy
When and how to adjust/roll positions

### 8. Tax Implications
Impact on qualified dividends, wash sales, etc.

### 9. Stress Test
Maximum margin requirement under extreme move

### 10. Alternative Considered
Why you rejected collar strategy, put spreads, etc.

---

**Include Black-Scholes calculations where appropriate, breakeven analysis, and probability of profit calculations.**