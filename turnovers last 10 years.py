import pandas as pd

def get_turnover_game_rows(year):
    print(f"Processing {year}...")
    url = f"https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.csv.gz"
    pbp = pd.read_csv(url, compression='gzip', low_memory=False)
    pbp = pbp[pbp['season_type'].isin(['REG', 'POST'])]

    games = pbp[['game_id', 'week', 'home_team', 'away_team', 'home_score', 'away_score']].drop_duplicates()
    games['season'] = year
    games['winner'] = games.apply(lambda row: row['home_team'] if row['home_score'] > row['away_score'] else row['away_team'], axis=1)

    # Turnover data
    turnover_plays = pbp[(pbp['interception'] == 1) | (pbp['fumble_lost'] == 1)]
    committed = turnover_plays.groupby(['game_id', 'posteam']).size().reset_index(name='turnovers_committed')
    forced = turnover_plays.groupby(['game_id', 'defteam']).size().reset_index(name='turnovers_forced')

    # Format for both teams
    home_rows = games.copy()
    away_rows = games.copy()

    home_rows['team'] = home_rows['home_team']
    home_rows['opponent'] = home_rows['away_team']
    home_rows['team_score'] = home_rows['home_score']
    home_rows['opp_score'] = home_rows['away_score']

    away_rows['team'] = away_rows['away_team']
    away_rows['opponent'] = away_rows['home_team']
    away_rows['team_score'] = away_rows['away_score']
    away_rows['opp_score'] = away_rows['home_score']

    # Combine perspectives
    long_df = pd.concat([home_rows, away_rows])[[
        'game_id', 'season', 'week', 'team', 'opponent', 'team_score', 'opp_score', 'winner'
    ]]

    # Merge turnover data
    long_df = long_df.merge(committed, how='left', left_on=['game_id', 'team'], right_on=['game_id', 'posteam'])
    long_df = long_df.merge(forced, how='left', left_on=['game_id', 'team'], right_on=['game_id', 'defteam'])
    long_df = long_df.drop(columns=['posteam', 'defteam'])

    long_df['turnovers_committed'] = long_df['turnovers_committed'].fillna(0).astype(int)
    long_df['turnovers_forced'] = long_df['turnovers_forced'].fillna(0).astype(int)
    long_df['turnover_differential'] = long_df['turnovers_forced'] - long_df['turnovers_committed']
    long_df['won_game'] = (long_df['team'] == long_df['winner']).astype(int)

    return long_df[[
        'game_id', 'season', 'week', 'team', 'opponent', 'won_game',
        'turnovers_committed', 'turnovers_forced', 'turnover_differential'
    ]]

# Run and combine all years
all_years_df = pd.concat([get_turnover_game_rows(year) for year in range(2014, 2024)], ignore_index=True)

# Save to CSV
all_years_df.to_csv("2turnover_summary_2014_2023.csv", index=False)
print("✅ Saved to '2turnover_summary_2014_2023.csv'")


# === Turnover Differential Summary Table ===
summary = (
    all_years_df.groupby("turnover_differential")["won_game"]
    .agg(["sum", "count"])
    .rename(columns={"sum": "Games_Won", "count": "Total_Games"})
)
summary["Games_Lost"] = summary["Total_Games"] - summary["Games_Won"]
summary["Win_Rate"] = summary["Games_Won"] / summary["Total_Games"]
zero_win_rate = summary.loc[summary.index == 0, "Win_Rate"]
summary["Change_vs_Zero_TO"] = summary["Win_Rate"] - zero_win_rate.values[0]
summary = summary.reset_index().sort_values("turnover_differential")
print(summary)

# === Optional: SRS Win Prob Curves by Turnover Differential Buckets ===
if "team_srs_differential" in all_years_df.columns:
    import seaborn as sns
    import matplotlib.pyplot as plt

    all_years_df["srs_bucket"] = pd.cut(
        all_years_df["team_srs_differential"],
        bins=[-100, -10, 0, 10, 100],
        labels=["<-10", "-10 to 0", "0 to 10", "10+"]
    )

    srs_win_prob = (
        all_years_df.groupby(["srs_bucket", "turnover_differential"])["won_game"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=srs_win_prob,
        x="turnover_differential",
        y="won_game",
        hue="srs_bucket",
        marker="o"
    )
    plt.title("Win Probability by Turnover Differential and SRS Differential")
    plt.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    plt.xlabel("Turnover Differential")
    plt.ylabel("Win Probability")
    plt.legend(title="SRS Differential")
    plt.grid(True)
    plt.tight_layout()
    plt.show()