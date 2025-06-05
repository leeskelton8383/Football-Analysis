# Football-Analysis
### Introduction

Turnovers have long been recognized as a defining variable in the outcome of NFL games. However, the context of those turnovers matters. A game between two evenly matched teams might swing wildly on a single interception, while a blowout matchup may be less sensitive to turnover swings. To more precisely model how win probability changes based on game dynamics, we evaluated the interaction between **turnover differential** and **team quality**, as measured by the **Simple Rating System (SRS)**.

The objective of this research was to explore two complementary approaches:

1. An empirical **bucketed win rate analysis** based on actual outcomes from 10 years of NFL games.
2. A **logistic regression model** that incorporates turnover differential, binned SRS differential, and their interaction.

We aim to quantify the real-world impact of turnovers and team strength and evaluate how these factors interact to predict the likelihood of a team winning a game.

---

### What is SRS?

**Simple Rating System (SRS)** is a single metric published by Pro Football Reference (PFR) that measures a team’s overall strength relative to league average. It combines:

- **Margin of Victory** (point differential per game), and
- **Strength of Schedule** (opponent quality)

SRS is expressed as a point value — for example, a team with an SRS of +5.0 is estimated to be five points better than an average team on a neutral field. Because it adjusts for opponent quality, it’s a helpful tool for comparing teams beyond just win-loss records.

In this study, we compute **SRS differential** as the team’s SRS minus their opponent’s SRS to capture relative matchup quality. All SRS values were sourced from **Pro Football Reference (PFR)**.

---

### Data Sources and Feature Engineering

We used game-level data from the 2014 to 2023 NFL seasons, primarily sourced from nflverse play-by-play data. Each record represents a team-game instance (i.e., each game is counted twice, once from each team's perspective). Key features engineered include:

- **Turnover Differential**: Takeaways minus giveaways
- **Team SRS Differential**: Team SRS minus opponent SRS
- **Binned SRS Categories**:
    - srs_Much_Weaker_than_Opponent: SRS diff ≤ –7.5
    - srs_Weaker_than_Opponent: –7.5 < diff ≤ –2.5
    - srs_About_Equal_to_Opponent: –2.5 < diff ≤ 2.5
    - srs_Stronger_than_Opponent: 2.5 < diff ≤ 7.5
    - srs_Much_Stronger_than_Opponent: diff > 7.5
- **Interaction Terms**: Turnover differential multiplied by each SRS bin indicator (one-hot encoded)

---

### Methodology

### Empirical Win Rate Analysis

We grouped games by turnover differential and calculated historical win rates to visualize real-world performance. This serves as a benchmark for model calibration.

### Logistic Regression Model

We trained a logistic regression model using the following features:

- Turnover differential (continuous)
- One-hot encoded SRS bins (categorical)
- Interaction terms (turnover differential x SRS bin)

The model outputs a win probability based on these features.

---

### Bucket Analysis Recap (Empirical Win Rates)

From 10 seasons of data (2014–2023):

| Turnover Diff | Win Rate | Δ vs. 0 TO Diff |
| --- | --- | --- |
| -3 | 9% | -41% |
| -2 | 18% | -32% |
| -1 | 34% | -16% |
| 0 | 50% | --- |
| +1 | 66% | +16% |
| +2 | 82% | +32% |
| +3 | 91% | +41% |

The pattern is strikingly linear: each additional turnover in your favor increases win rate by roughly 15-17%, up to a point.

---

### Coefficient Interpretation (Logistic Regression)

| Feature | Coefficient |
| --- | --- |
| Turnover Differential | +0.762 |
| srs_Weaker_than_Opponent | +0.644 |
| srs_About_Equal_to_Opponent | +1.408 |
| srs_Stronger_than_Opponent | +2.235 |
| srs_Much_Stronger_than_Opponent | +3.050 |
| interact_srs_Weaker_than_Opponent | –0.086 |
| interact_srs_About_Equal_to_Opponent | +0.014 |
| interact_srs_Stronger_than_Opponent | –0.084 |
| interact_srs_Much_Stronger_than_Opponent | +0.026 |

### Key Observations:

- ✅ **Turnover Differential**: Positive coefficient (+0.76): Each additional turnover in your favor (forcing one or avoiding one) significantly increases the odds of winning. This confirms the intuitive understanding that turnovers swing outcomes.
    - **Interpretation Note**: Logistic regression operates on log-odds. Around the 50% win probability baseline, each +1 in turnover differential increases win probability by ~15–16 percentage points (e.g., from 50% to ~66%).
- ✅ **SRS Bins**:
    - Being in the **srs_Much_Stronger_than_Opponent** bin (+3.05) has a larger effect than even a +3 turnover swing.
    - Surprisingly, being in the **srs_Weaker_than_Opponent** bin (+0.64) offers nearly the same odds boost as a +1 turnover swing.
    - All SRS bins stronger than "Weaker" have coefficients greater than +0.76, confirming **SRS differential is a more powerful base predictor** than turnovers alone.
- ✅ **Interaction Terms**: Mostly negative and small. This suggests the effect of turnovers is **diminished slightly** when the team is already expected to dominate or be outmatched.

---

### Predicted Win Probability Matrix

| TO Diff | srs_Much_Weaker_than_Opponent (–∞ to –7.5) | srs_Weaker_than_Opponent (–7.5 to –2.5) | srs_About_Equal_to_Opponent (–2.5 to 2.5) | srs_Stronger_than_Opponent (2.5 to 7.5) | srs_Much_Stronger_than_Opponent (7.5 to ∞) |
| --- | --- | --- | --- | --- | --- |
| -3 | 8% | 13% | 25% | 52% | 76% |
| -2 | 11% | 17% | 32% | 59% | 82% |
| -1 | 14% | 23% | 41% | 68% | 88% |
| 0 | 18% | 30% | 50% | 75% | 92% |
| +1 | 22% | 38% | 59% | 81% | 95% |
| +2 | 27% | 46% | 67% | 86% | 97% |
| +3 | 32% | 53% | 73% | 90% | 98% |

This matrix illustrates how **SRS dominates the baseline expectation** across columns, while **turnover differential creates vertical movement** within each column.

---

### Examining Turnover Differential Distribution by Team Quality (SRS)

A supplementary analysis of 10 years of game data shows a clear link between raw team strength (SRS) and turnover differential outcomes. High-SRS teams not only start with a higher baseline win probability—they also generate more takeaways and avoid giveaways more consistently. This reinforces why the interaction between turnovers and team quality is minimal in the model: **better teams are structurally more likely to win both the turnover battle and the game.**

| SRS Tier | –7 | –6 | –5 | –4 | –3 | –2 | –1 | 0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Low SRS [–100, –7.5] | 0.2 | 0.2 | 0.6 | 3.3 | 9.7 | 15.4 | 20.3 | 23.3 | 14.3 | 8.5 | 2.7 | 1.1 | 0.3 | 0.2 | 0.0 |
| Below Avg [–7.5, –2.5] | 0.0 | 0.2 | 0.7 | 3.2 | 7.0 | 13.1 | 20.7 | 23.3 | 17.4 | 8.8 | 4.1 | 1.2 | 0.3 | 0.1 | 0.0 |
| Average [–2.5, 2.5] | 0.0 | 0.2 | 0.4 | 1.9 | 5.4 | 11.3 | 19.9 | 22.3 | 18.6 | 11.3 | 6.1 | 2.0 | 0.6 | 0.0 | 0.0 |
| Above Avg [2.5, 7.5] | 0.0 | 0.0 | 0.3 | 0.9 | 4.0 | 10.9 | 16.4 | 22.0 | 21.8 | 13.6 | 7.3 | 2.0 | 0.3 | 0.3 | 0.1 |
| High SRS [7.5, 100] | 0.0 | 0.0 | 0.1 | 0.7 | 3.9 | 7.6 | 15.5 | 24.0 | 20.2 | 16.0 | 7.3 | 3.9 | 0.7 | 0.1 | 0.0 |

### Turnover Balance by SRS Tier

When simplifying turnover differentials into two buckets (negative vs. even/positive), we observe a striking trend:
This progression highlights a structural edge: **as team quality increases, so does the likelihood of producing a positive turnover outcome**. This supports our earlier conclusion that strong teams not only win more — they create favorable turnover margins that compound their advantage.

| SRS Tier | % Negative TO Ratio | % Even/Positive TO Ratio |
| --- | --- | --- |
| Low SRS [–100, –7.5] | 49.7% | 50.4% |
| Below Avg [–7.5, –2.5] | 44.9% | 55.2% |
| Average [–2.5, 2.5] | 39.1% | 60.9% |
| Above Avg [2.5, 7.5] | 32.5% | 67.4% |
| High SRS [7.5, 100] | 27.8% | 72.2% |
|  |  |  |

This progression highlights a structural edge: **as team quality increases, so does the likelihood of producing a positive turnover outcome**. This supports our earlier conclusion that strong teams not only win more — they create favorable turnover margins that compound their advantage.

### Conclusions

This study demonstrates that both **turnover differential** and **team quality (SRS)** are critical and complementary variables in understanding NFL game outcomes. Our findings align across two distinct modeling approaches:

- The **bucketed win rate analysis** shows that each turnover swing shifts win probability by approximately 15–17 percentage points near the 50% win-probability mark.
- The **logistic regression model** confirms this relationship and further reveals how **SRS differentials drive even stronger effects** on win probability than turnovers alone.

Key conclusions include:

- **Turnovers remain a high-leverage factor**. The model confirms that a single turnover swing (e.g., going from 0 to +1) can significantly improve win odds, particularly in matchups with similar SRS.
- **SRS is a more stable predictor**. Teams that are much stronger than their opponent (by SRS) start with a far higher baseline probability of winning—even before any turnovers occur. The coefficient for “Much Stronger than Opponent” exceeds that of even a +3 turnover differential.
- **Interaction terms are minimal but meaningful**. Turnovers tend to matter slightly less when a team is already heavily favored or outmatched, suggesting diminishing returns at the extremes of SRS differential.
- **Stronger teams win the turnover battle more often**. Supplementary analysis shows that as team SRS increases, so does the likelihood of having an even or positive turnover differential. This makes turnovers partially endogenous: good teams play cleaner football, which reinforces their pre-existing strength.
- **Empirical and model-driven insights agree**. The predicted win probabilities from the model align closely with the actual win rates seen in historical data, validating the model’s use for future predictive applications.

In sum, **SRS and turnovers are not competing predictors—they are complementary, but hierarchical**. SRS sets the baseline expectation, and turnovers act as the in-game disruptor that can elevate or derail outcomes. This layered perspective allows for more nuanced game forecasting and postgame evaluation.

---

### Next Steps

- Include **home-field advantage** (fixed or team-specific)
- Add **team-specific SRS trends or rolling averages**
- Use model for **real-time win projection and game prediction**
- Consider **non-linear models** to explore deeper patterns
