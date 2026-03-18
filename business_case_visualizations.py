"""
PhonePe Pulse — Business Case Study Visualizations
===================================================
Case 1 : Decoding Transaction Dynamics
Case 2 : Device Dominance & User Engagement
Case 3 : Insurance Penetration & Growth
Case 4 : Transaction Analysis for Market Expansion
Case 5 : User Engagement & Growth Strategy

Libraries  : Pandas, Matplotlib, Seaborn
DB columns : Exact Colab standards
             State, Year, Quater, Transacion_type,
             Transacion_count, Transacion_amount,
             Brands, Count, Registered_user, App_opens,
             District, Amount, EntityType, EntityName
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings("ignore")

# ── DB Connection ─────────────────────────────────────────────────────────────
engine = create_engine("mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")

# ── Global Theme ─────────────────────────────────────────────────────────────
PURPLE  = "#6739B7"
CYAN    = "#00d4ff"
ORANGE  = "#ff6b35"
GREEN   = "#34d399"
YELLOW  = "#f59e0b"
PINK    = "#a855f7"
BG      = "#0d0b1e"
CARD_BG = "#1c1240"
TEXT    = "#e0d8ff"
GRID    = "#1e1650"
MUTED   = "#9b8ec4"

PALETTE = [PURPLE, CYAN, ORANGE, PINK, GREEN, YELLOW, "#22d3ee", "#fb7185"]

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    CARD_BG,
    "axes.edgecolor":    GRID,
    "axes.labelcolor":   TEXT,
    "axes.titlecolor":   TEXT,
    "axes.titlesize":    13,
    "axes.labelsize":    10,
    "xtick.color":       TEXT,
    "ytick.color":       TEXT,
    "xtick.labelsize":   8.5,
    "ytick.labelsize":   8.5,
    "grid.color":        GRID,
    "grid.linewidth":    0.6,
    "text.color":        TEXT,
    "legend.facecolor":  CARD_BG,
    "legend.edgecolor":  GRID,
    "legend.fontsize":   8.5,
    "font.family":       "DejaVu Sans",
})

# ── Helpers ───────────────────────────────────────────────────────────────────
def q(sql):
    return pd.read_sql(sql, engine)

def crore(x, _):
    return f"₹{x/1e7:,.0f}Cr"

def millions(x, _):
    return f"{x/1e6:.1f}M"

def add_bar_labels(ax, bars, fmt="{:.0f}", color=TEXT, fontsize=8.5,
                   orient="h", offset_pct=0.01):
    """Add value labels to bar charts."""
    max_val = max(b.get_width() if orient == "h"
                  else b.get_height() for b in bars)
    for bar in bars:
        val = bar.get_width() if orient == "h" else bar.get_height()
        if orient == "h":
            ax.text(val + max_val * offset_pct,
                    bar.get_y() + bar.get_height() / 2,
                    fmt.format(val), va="center",
                    fontsize=fontsize, color=color)
        else:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    val + max_val * offset_pct,
                    fmt.format(val), ha="center",
                    fontsize=fontsize, color=color)

def section_title(title, subtitle=""):
    """Print a section header to console."""
    print(f"\n{'═'*60}")
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print(f"{'═'*60}")

def save(fig, filename):
    fig.tight_layout()
    fig.savefig(f"{filename}.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.show()
    plt.close(fig)
    print(f"  ✅  Saved → {filename}.png")


# ─────────────────────────────────────────────────────────────────────────────
#  CHECK INSURANCE TABLE
# ─────────────────────────────────────────────────────────────────────────────
try:
    test = q("SELECT COUNT(*) AS cnt FROM aggregated_insurance")
    HAS_INSURANCE = int(test["cnt"].iloc[0]) > 0
except Exception:
    HAS_INSURANCE = False
    print("  ⚠️  aggregated_insurance not found — Case 3 charts skipped")


# ═════════════════════════════════════════════════════════════════════════════
#
#  ██████╗ █████╗ ███████╗███████╗     ██╗
# ██╔════╝██╔══██╗██╔════╝██╔════╝    ███║
# ██║     ███████║███████╗█████╗      ╚██║
# ██║     ██╔══██║╚════██║██╔══╝       ██║
# ╚██████╗██║  ██║███████║███████╗     ██║
#  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝
#  DECODING TRANSACTION DYNAMICS
#
# ═════════════════════════════════════════════════════════════════════════════
section_title("CASE 1 — Decoding Transaction Dynamics",
              "Transaction behavior across states, quarters & categories")

# ── Data Loads ────────────────────────────────────────────────────────────────
df_type = q("""
    SELECT Transacion_type,
           SUM(Transacion_count)  AS Total_Count,
           ROUND(SUM(Transacion_amount),2) AS Total_Amount,
           ROUND(SUM(Transacion_count)*100.0
                 /SUM(SUM(Transacion_count)) OVER(),2) AS Count_Share_Pct,
           ROUND(SUM(Transacion_amount)*100.0
                 /SUM(SUM(Transacion_amount)) OVER(),2) AS Amount_Share_Pct
    FROM aggregated_transaction
    GROUP BY Transacion_type
    ORDER BY Total_Amount DESC
""")

df_top10_state = q("""
    SELECT State,
           SUM(Transacion_count)  AS Total_Transactions,
           ROUND(SUM(Transacion_amount),2) AS Total_Amount
    FROM aggregated_transaction
    GROUP BY State
    ORDER BY Total_Amount DESC
    LIMIT 10
""")

df_bottom10 = q("""
    SELECT State,
           SUM(Transacion_count)  AS Total_Transactions,
           ROUND(SUM(Transacion_amount),2) AS Total_Amount
    FROM aggregated_transaction
    GROUP BY State
    ORDER BY Total_Amount ASC
    LIMIT 10
""")

df_quarterly = q("""
    SELECT Year, Quater,
           SUM(Transacion_count)  AS Total_Transactions,
           ROUND(SUM(Transacion_amount),2) AS Total_Amount
    FROM aggregated_transaction
    GROUP BY Year, Quater
    ORDER BY Year, Quater
""")
df_quarterly["Period"] = (df_quarterly["Year"].astype(str)
                          + " Q" + df_quarterly["Quater"].astype(str))

df_type_year = q("""
    SELECT Year, Transacion_type,
           ROUND(SUM(Transacion_amount)/1e7,2) AS Amount_Cr
    FROM aggregated_transaction
    GROUP BY Year, Transacion_type
    ORDER BY Year
""")

# ── C1 Fig 1 — Payment Category Breakdown (Donut + H-Bar) ────────────────────
print("  Plotting C1-F1 : Payment Category Breakdown…")
fig, axes = plt.subplots(1, 2, figsize=(16, 6), facecolor=BG)
fig.suptitle("Case 1 — Payment Category Breakdown",
             color=TEXT, fontsize=15, fontweight="bold")

# Donut — count share
wedges, texts, autotexts = axes[0].pie(
    df_type["Total_Count"],
    labels=df_type["Transacion_type"],
    autopct="%1.1f%%",
    colors=PALETTE[:len(df_type)],
    startangle=140,
    pctdistance=0.78,
    wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
)
for t in texts:      t.set_color(TEXT);    t.set_fontsize(8.5)
for a in autotexts:  a.set_color("white"); a.set_fontsize(8); a.set_fontweight("bold")
axes[0].set_title("Transaction Count Share (%)", color=TEXT, pad=12)

# H-Bar — amount
bars = axes[1].barh(df_type["Transacion_type"], df_type["Total_Amount"],
                    color=PALETTE[:len(df_type)], edgecolor=BG, height=0.6)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(crore))
axes[1].set_title("Total Transaction Amount (₹ Crore)", color=TEXT, pad=12)
axes[1].invert_yaxis()
axes[1].grid(axis="x", alpha=0.35)
axes[1].set_axisbelow(True)
for bar, val in zip(bars, df_type["Total_Amount"]):
    axes[1].text(bar.get_width() + df_type["Total_Amount"].max() * 0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"₹{val/1e7:,.0f}Cr", va="center", fontsize=8.5, color=TEXT)
save(fig, "C1_F1_payment_category_breakdown")

# ── C1 Fig 2 — Top 10 & Bottom 10 States ─────────────────────────────────────
print("  Plotting C1-F2 : Top 10 vs Bottom 10 States…")
fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=BG)
fig.suptitle("Case 1 — State Performance: Top 10 vs Bottom 10",
             color=TEXT, fontsize=15, fontweight="bold")

# Top 10
top_sorted = df_top10_state.sort_values("Total_Amount")
colors_top = sns.color_palette("rocket_r", len(top_sorted))
bars = axes[0].barh(top_sorted["State"], top_sorted["Total_Amount"],
                    color=colors_top, edgecolor=BG, height=0.7)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(crore))
axes[0].set_title("🏆 Top 10 States by Transaction Amount", color=CYAN, pad=10)
axes[0].grid(axis="x", alpha=0.35)
axes[0].set_axisbelow(True)
for bar, val in zip(bars, top_sorted["Total_Amount"]):
    axes[0].text(bar.get_width() + top_sorted["Total_Amount"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"₹{val/1e7:,.0f}Cr", va="center", fontsize=8, color=TEXT)

# Bottom 10
bot_sorted = df_bottom10.sort_values("Total_Amount", ascending=False)
colors_bot = sns.color_palette("mako_r", len(bot_sorted))
bars2 = axes[1].barh(bot_sorted["State"], bot_sorted["Total_Amount"],
                     color=colors_bot, edgecolor=BG, height=0.7)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(crore))
axes[1].set_title("⚠️ Bottom 10 States (Low Adoption)", color=ORANGE, pad=10)
axes[1].grid(axis="x", alpha=0.35)
axes[1].set_axisbelow(True)
for bar, val in zip(bars2, bot_sorted["Total_Amount"]):
    axes[1].text(bar.get_width() + bot_sorted["Total_Amount"].max()*0.02,
                 bar.get_y() + bar.get_height()/2,
                 f"₹{val/1e7:,.2f}Cr", va="center", fontsize=8, color=TEXT)
save(fig, "C1_F2_top_bottom_states")

# ── C1 Fig 3 — Quarterly Growth Trend (Dual Line) ────────────────────────────
print("  Plotting C1-F3 : Quarterly Growth Trend…")
fig, axes = plt.subplots(2, 1, figsize=(14, 9), facecolor=BG, sharex=True)
fig.suptitle("Case 1 — Quarter-wise Transaction Growth Trend",
             color=TEXT, fontsize=15, fontweight="bold")

# Count
axes[0].plot(df_quarterly["Period"], df_quarterly["Total_Transactions"],
             color=PURPLE, marker="o", lw=2.5, ms=6,
             markerfacecolor=CYAN, markeredgecolor=BG, markeredgewidth=1.5)
axes[0].fill_between(df_quarterly["Period"],
                     df_quarterly["Total_Transactions"], alpha=0.15, color=PURPLE)
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(millions))
axes[0].set_ylabel("Transaction Count (M)")
axes[0].set_title("Transaction Count per Quarter", color=TEXT)
axes[0].grid(alpha=0.35); axes[0].set_axisbelow(True)

# Amount
axes[1].plot(df_quarterly["Period"], df_quarterly["Total_Amount"],
             color=CYAN, marker="s", lw=2.5, ms=6,
             markerfacecolor=ORANGE, markeredgecolor=BG, markeredgewidth=1.5)
axes[1].fill_between(df_quarterly["Period"],
                     df_quarterly["Total_Amount"], alpha=0.15, color=CYAN)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(crore))
axes[1].set_ylabel("Transaction Amount (₹Cr)")
axes[1].set_title("Transaction Amount per Quarter", color=TEXT)
axes[1].grid(alpha=0.35); axes[1].set_axisbelow(True)
axes[1].set_xticklabels(df_quarterly["Period"], rotation=45, ha="right")
save(fig, "C1_F3_quarterly_growth_trend")

# ── C1 Fig 4 — Transaction Type per Year (Grouped Bar) ───────────────────────
print("  Plotting C1-F4 : Transaction Type Year-wise Trend…")
fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
fig.suptitle("Case 1 — Transaction Type Trend per Year (₹ Crore)",
             color=TEXT, fontsize=15, fontweight="bold")
sns.barplot(data=df_type_year, x="Year", y="Amount_Cr",
            hue="Transacion_type", palette=PALETTE,
            ax=ax, edgecolor=BG, linewidth=0.8)
ax.set_xlabel("Year"); ax.set_ylabel("Amount (₹ Crore)")
ax.legend(title="Transaction Type", title_fontsize=8.5,
          loc="upper left", framealpha=0.7)
ax.grid(axis="y", alpha=0.35); ax.set_axisbelow(True)
save(fig, "C1_F4_type_year_trend")


# ═════════════════════════════════════════════════════════════════════════════
#
#  ██████╗ █████╗ ███████╗███████╗    ██████╗
# ██╔════╝██╔══██╗██╔════╝██╔════╝    ╚════██╗
# ██║     ███████║███████╗█████╗       █████╔╝
# ██║     ██╔══██║╚════██║██╔══╝      ██╔═══╝
# ╚██████╗██║  ██║███████║███████╗    ███████╗
#  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝
#  DEVICE DOMINANCE & USER ENGAGEMENT
#
# ═════════════════════════════════════════════════════════════════════════════
section_title("CASE 2 — Device Dominance & User Engagement",
              "Brand preferences, regional adoption & engagement ratios")

# ── Data Loads ────────────────────────────────────────────────────────────────
df_brands = q("""
    SELECT Brands,
           SUM(Count) AS Total_Users,
           ROUND(AVG(Percentage)*100,2) AS Avg_Market_Share_Pct,
           ROUND(SUM(Count)*100.0/SUM(SUM(Count)) OVER(),2) AS Overall_Share_Pct
    FROM aggregated_user
    WHERE Brands IS NOT NULL
    GROUP BY Brands
    ORDER BY Total_Users DESC
    LIMIT 10
""")

df_state_users = q("""
    SELECT State,
           SUM(Registered_user) AS Total_Registered,
           SUM(App_opens)       AS Total_App_Opens,
           ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Engagement_Ratio
    FROM aggregated_user
    GROUP BY State
    ORDER BY Total_Registered DESC
    LIMIT 10
""")

df_low_engage = q("""
    SELECT State,
           SUM(Registered_user) AS Total_Registered,
           SUM(App_opens)       AS Total_App_Opens,
           ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Engagement_Ratio
    FROM aggregated_user
    GROUP BY State
    HAVING Engagement_Ratio < (
        SELECT ROUND(AVG(App_opens/Registered_user),2)
        FROM aggregated_user WHERE Registered_user > 0
    )
    ORDER BY Total_Registered DESC
    LIMIT 10
""")

df_user_trend = q("""
    SELECT Year, Quater,
           SUM(Registered_user) AS Total_Registered,
           SUM(App_opens)       AS Total_App_Opens
    FROM aggregated_user
    GROUP BY Year, Quater
    ORDER BY Year, Quater
""")
df_user_trend["Period"] = (df_user_trend["Year"].astype(str)
                           + " Q" + df_user_trend["Quater"].astype(str))

df_brand_year = q("""
    SELECT Brands, Year,
           SUM(Count) AS Yearly_Users
    FROM aggregated_user
    WHERE Brands IS NOT NULL
    GROUP BY Brands, Year
    ORDER BY Brands, Year
""")
top5_brands = df_brands["Brands"].head(5).tolist()
df_brand_year = df_brand_year[df_brand_year["Brands"].isin(top5_brands)]

# ── C2 Fig 1 — Top 10 Brands (Donut + Bar) ───────────────────────────────────
print("  Plotting C2-F1 : Top Mobile Brands…")
fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=BG)
fig.suptitle("Case 2 — Top Mobile Brands by PhonePe Users",
             color=TEXT, fontsize=15, fontweight="bold")

wedges, texts, autotexts = axes[0].pie(
    df_brands["Total_Users"],
    labels=df_brands["Brands"],
    autopct="%1.1f%%",
    colors=PALETTE[:len(df_brands)],
    startangle=90,
    pctdistance=0.80,
    wedgeprops=dict(width=0.5, edgecolor=BG, linewidth=2)
)
for t in texts:      t.set_color(TEXT);    t.set_fontsize(8)
for a in autotexts:  a.set_color("white"); a.set_fontsize(7.5); a.set_fontweight("bold")
axes[0].set_title("Market Share — User Count (%)", color=TEXT, pad=12)

sorted_brands = df_brands.sort_values("Total_Users")
bars = axes[1].barh(sorted_brands["Brands"], sorted_brands["Total_Users"],
                    color=PALETTE[:len(sorted_brands)], edgecolor=BG, height=0.65)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(millions))
axes[1].set_title("Total Users per Brand (Millions)", color=TEXT, pad=12)
axes[1].grid(axis="x", alpha=0.35); axes[1].set_axisbelow(True)
for bar, val in zip(bars, sorted_brands["Total_Users"]):
    axes[1].text(bar.get_width() + sorted_brands["Total_Users"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"{val/1e6:.2f}M", va="center", fontsize=8.5, color=TEXT)
save(fig, "C2_F1_top_mobile_brands")

# ── C2 Fig 2 — Registered Users vs App Opens (Top 10 States) ─────────────────
print("  Plotting C2-F2 : Registered Users vs App Opens…")
fig, ax = plt.subplots(figsize=(13, 7), facecolor=BG)
fig.suptitle("Case 2 — Registered Users vs App Opens (Top 10 States)",
             color=TEXT, fontsize=15, fontweight="bold")

x     = range(len(df_state_users))
width = 0.38
s     = df_state_users.sort_values("Total_Registered")

bars1 = ax.barh([i + width/2 for i in range(len(s))], s["Total_Registered"],
                height=width, color=PURPLE, label="Registered Users",
                edgecolor=BG, linewidth=0.8)
bars2 = ax.barh([i - width/2 for i in range(len(s))], s["Total_App_Opens"],
                height=width, color=CYAN, label="App Opens",
                edgecolor=BG, linewidth=0.8)

ax.set_yticks(list(range(len(s))))
ax.set_yticklabels(s["State"].str.title())
ax.xaxis.set_major_formatter(mticker.FuncFormatter(millions))
ax.set_xlabel("Count (Millions)")
ax.legend(loc="lower right")
ax.grid(axis="x", alpha=0.35); ax.set_axisbelow(True)
save(fig, "C2_F2_users_vs_appopens")

# ── C2 Fig 3 — Low Engagement States (Bar) ───────────────────────────────────
print("  Plotting C2-F3 : Low Engagement States…")
fig, ax = plt.subplots(figsize=(13, 6), facecolor=BG)
fig.suptitle("Case 2 — Underutilised States (High Users, Low Engagement)",
             color=TEXT, fontsize=15, fontweight="bold")

le = df_low_engage.sort_values("Total_Registered")
colors_le = sns.color_palette("flare_r", len(le))
bars = ax.barh(le["State"], le["Engagement_Ratio"],
               color=colors_le, edgecolor=BG, height=0.65)
ax.set_xlabel("Engagement Ratio (App Opens / Registered Users)")
ax.set_title("States Below Average Engagement", color=ORANGE, fontsize=11)
ax.grid(axis="x", alpha=0.35); ax.set_axisbelow(True)
for bar, val in zip(bars, le["Engagement_Ratio"]):
    ax.text(bar.get_width() + le["Engagement_Ratio"].max()*0.01,
            bar.get_y() + bar.get_height()/2,
            f"{val:.1f}x", va="center", fontsize=9, color=ORANGE)
save(fig, "C2_F3_low_engagement_states")

# ── C2 Fig 4 — Brand Growth Over Years (Multi-line) ──────────────────────────
print("  Plotting C2-F4 : Top 5 Brand Growth Over Years…")
fig, ax = plt.subplots(figsize=(13, 6), facecolor=BG)
fig.suptitle("Case 2 — Top 5 Mobile Brands: Year-wise User Growth",
             color=TEXT, fontsize=15, fontweight="bold")

for idx, brand in enumerate(top5_brands):
    subset = df_brand_year[df_brand_year["Brands"] == brand]
    ax.plot(subset["Year"].astype(str), subset["Yearly_Users"],
            marker="o", lw=2.2, ms=6, color=PALETTE[idx], label=brand,
            markeredgecolor=BG, markeredgewidth=1.2)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(millions))
ax.set_xlabel("Year"); ax.set_ylabel("Users (Millions)")
ax.legend(title="Brand", framealpha=0.7, loc="upper left")
ax.grid(alpha=0.35); ax.set_axisbelow(True)
save(fig, "C2_F4_brand_growth_years")

# ── C2 Fig 5 — User & App Opens Trend (Dual Line) ────────────────────────────
print("  Plotting C2-F5 : Quarterly User & App Opens Trend…")
fig, axes = plt.subplots(2, 1, figsize=(14, 9), facecolor=BG, sharex=True)
fig.suptitle("Case 2 — Quarterly User Registration & App Opens Trend",
             color=TEXT, fontsize=15, fontweight="bold")

axes[0].plot(df_user_trend["Period"], df_user_trend["Total_Registered"],
             color=PURPLE, marker="o", lw=2.5, ms=6,
             markerfacecolor=CYAN, markeredgecolor=BG, markeredgewidth=1.5)
axes[0].fill_between(df_user_trend["Period"],
                     df_user_trend["Total_Registered"], alpha=0.15, color=PURPLE)
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(millions))
axes[0].set_ylabel("Registered Users (M)")
axes[0].set_title("Registered Users per Quarter", color=TEXT)
axes[0].grid(alpha=0.35); axes[0].set_axisbelow(True)

axes[1].plot(df_user_trend["Period"], df_user_trend["Total_App_Opens"],
             color=GREEN, marker="^", lw=2.5, ms=6,
             markerfacecolor=YELLOW, markeredgecolor=BG, markeredgewidth=1.5)
axes[1].fill_between(df_user_trend["Period"],
                     df_user_trend["Total_App_Opens"], alpha=0.15, color=GREEN)
axes[1].yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"{x/1e9:.2f}B"))
axes[1].set_ylabel("App Opens (Billions)")
axes[1].set_title("App Opens per Quarter", color=TEXT)
axes[1].grid(alpha=0.35); axes[1].set_axisbelow(True)
axes[1].set_xticklabels(df_user_trend["Period"], rotation=45, ha="right")
save(fig, "C2_F5_quarterly_user_trend")


# ═════════════════════════════════════════════════════════════════════════════
#
#  ██████╗ █████╗ ███████╗███████╗    ██████╗
# ██╔════╝██╔══██╗██╔════╝██╔════╝    ╚════██╗
# ██║     ███████║███████╗█████╗       █████╔╝
# ██║     ██╔══██║╚════██║██╔══╝       ╚═══██╗
# ╚██████╗██║  ██║███████║███████╗    ██████╔╝
#  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═════╝
#  INSURANCE PENETRATION & GROWTH
#
# ═════════════════════════════════════════════════════════════════════════════
section_title("CASE 3 — Insurance Penetration & Growth Potential",
              "Growth trajectory & untapped insurance opportunities")

if HAS_INSURANCE:

    df_ins_state = q("""
        SELECT State,
               SUM(Transacion_count)  AS Total_Policies,
               ROUND(SUM(Transacion_amount),2) AS Total_Amount,
               ROUND(SUM(Transacion_amount)*100.0
                     /SUM(SUM(Transacion_amount)) OVER(),2) AS Amount_Share_Pct
        FROM aggregated_insurance
        GROUP BY State
        ORDER BY Total_Amount DESC
        LIMIT 10
    """)

    df_ins_bottom = q("""
        SELECT State,
               SUM(Transacion_count)  AS Total_Policies,
               ROUND(SUM(Transacion_amount),2) AS Total_Amount
        FROM aggregated_insurance
        GROUP BY State
        ORDER BY Total_Policies ASC
        LIMIT 10
    """)

    df_ins_trend = q("""
        SELECT Year, Quater,
               SUM(Transacion_count)  AS Total_Policies,
               ROUND(SUM(Transacion_amount),2) AS Total_Amount
        FROM aggregated_insurance
        GROUP BY Year, Quater
        ORDER BY Year, Quater
    """)
    df_ins_trend["Period"] = (df_ins_trend["Year"].astype(str)
                              + " Q" + df_ins_trend["Quater"].astype(str))

    df_ins_penetration = q("""
        SELECT t.State,
               SUM(t.Transacion_amount) AS Txn_Amount,
               SUM(i.Transacion_amount) AS Insurance_Amount,
               ROUND(SUM(i.Transacion_amount)
                     /SUM(t.Transacion_amount)*100, 4) AS Penetration_Pct
        FROM aggregated_transaction t
        JOIN aggregated_insurance i
            ON t.State=i.State AND t.Year=i.Year AND t.Quater=i.Quater
        GROUP BY t.State
        ORDER BY Penetration_Pct DESC
        LIMIT 10
    """)

    # ── C3 Fig 1 — Top 10 States Insurance (Pie + Bar) ───────────────────────
    print("  Plotting C3-F1 : Top 10 States by Insurance…")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=BG)
    fig.suptitle("Case 3 — Top 10 States: Insurance Transactions",
                 color=TEXT, fontsize=15, fontweight="bold")

    wedges, texts, autotexts = axes[0].pie(
        df_ins_state["Total_Amount"],
        labels=df_ins_state["State"].str.title(),
        autopct="%1.1f%%",
        colors=PALETTE[:len(df_ins_state)],
        startangle=140,
        pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
    )
    for t in texts:      t.set_color(TEXT);    t.set_fontsize(7.5)
    for a in autotexts:  a.set_color("white"); a.set_fontsize(7.5); a.set_fontweight("bold")
    axes[0].set_title("Insurance Amount Share by State", color=TEXT, pad=12)

    sorted_ins = df_ins_state.sort_values("Total_Amount")
    colors_ins = sns.color_palette("rocket_r", len(sorted_ins))
    bars = axes[1].barh(sorted_ins["State"], sorted_ins["Total_Amount"],
                        color=colors_ins, edgecolor=BG, height=0.65)
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(crore))
    axes[1].set_title("Insurance Amount (₹ Crore)", color=TEXT, pad=12)
    axes[1].grid(axis="x", alpha=0.35); axes[1].set_axisbelow(True)
    for bar, val in zip(bars, sorted_ins["Total_Amount"]):
        axes[1].text(bar.get_width() + sorted_ins["Total_Amount"].max()*0.01,
                     bar.get_y() + bar.get_height()/2,
                     f"₹{val/1e7:,.1f}Cr", va="center", fontsize=8, color=TEXT)
    save(fig, "C3_F1_insurance_top10_states")

    # ── C3 Fig 2 — Untapped Markets + Quarterly Trend ────────────────────────
    print("  Plotting C3-F2 : Untapped Markets & Quarterly Trend…")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), facecolor=BG)
    fig.suptitle("Case 3 — Untapped Markets & Insurance Growth Trend",
                 color=TEXT, fontsize=15, fontweight="bold")

    bot_sorted = df_ins_bottom.sort_values("Total_Policies")
    colors_bot = sns.color_palette("mako", len(bot_sorted))
    bars = axes[0].barh(bot_sorted["State"], bot_sorted["Total_Policies"],
                        color=colors_bot, edgecolor=BG, height=0.65)
    axes[0].xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    axes[0].set_title("⚠️ Bottom 10 States — Lowest Insurance Policies",
                      color=ORANGE, pad=10)
    axes[0].grid(axis="x", alpha=0.35); axes[0].set_axisbelow(True)
    for bar, val in zip(bars, bot_sorted["Total_Policies"]):
        axes[0].text(bar.get_width() + bot_sorted["Total_Policies"].max()*0.01,
                     bar.get_y() + bar.get_height()/2,
                     f"{val:,.0f}", va="center", fontsize=8, color=TEXT)

    axes[1].plot(df_ins_trend["Period"], df_ins_trend["Total_Amount"],
                 color=GREEN, marker="o", lw=2.5, ms=6,
                 markerfacecolor=YELLOW, markeredgecolor=BG, markeredgewidth=1.5)
    axes[1].fill_between(df_ins_trend["Period"],
                         df_ins_trend["Total_Amount"], alpha=0.15, color=GREEN)
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(crore))
    axes[1].set_title("📈 Insurance Growth Trend (Quarter-wise)", color=CYAN, pad=10)
    axes[1].set_xticklabels(df_ins_trend["Period"], rotation=45, ha="right")
    axes[1].grid(alpha=0.35); axes[1].set_axisbelow(True)
    save(fig, "C3_F2_untapped_markets_trend")

    # ── C3 Fig 3 — Insurance Penetration Rate per State ──────────────────────
    print("  Plotting C3-F3 : Insurance Penetration Rate…")
    fig, ax = plt.subplots(figsize=(13, 6), facecolor=BG)
    fig.suptitle("Case 3 — Insurance Penetration Rate vs Total Transactions",
                 color=TEXT, fontsize=15, fontweight="bold")

    pen = df_ins_penetration.sort_values("Penetration_Pct")
    colors_pen = sns.color_palette("viridis", len(pen))
    bars = ax.barh(pen["State"], pen["Penetration_Pct"],
                   color=colors_pen, edgecolor=BG, height=0.65)
    ax.set_xlabel("Insurance Penetration (%)")
    ax.set_title("Insurance as % of Total Transactions per State",
                 color=TEXT, fontsize=11)
    ax.grid(axis="x", alpha=0.35); ax.set_axisbelow(True)
    for bar, val in zip(bars, pen["Penetration_Pct"]):
        ax.text(bar.get_width() + pen["Penetration_Pct"].max()*0.01,
                bar.get_y() + bar.get_height()/2,
                f"{val:.4f}%", va="center", fontsize=8.5, color=CYAN)
    save(fig, "C3_F3_insurance_penetration_rate")

else:
    print("  ⚠️  Skipping Case 3 — insurance table empty or missing.")


# ═════════════════════════════════════════════════════════════════════════════
#
#  ██████╗ █████╗ ███████╗███████╗    ██╗  ██╗
# ██╔════╝██╔══██╗██╔════╝██╔════╝    ██║  ██║
# ██║     ███████║███████╗█████╗      ███████║
# ██║     ██╔══██║╚════██║██╔══╝      ╚════██║
# ╚██████╗██║  ██║███████║███████╗         ██║
#  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝         ╚═╝
#  TRANSACTION ANALYSIS FOR MARKET EXPANSION
#
# ═════════════════════════════════════════════════════════════════════════════
section_title("CASE 4 — Transaction Analysis for Market Expansion",
              "Identify trends, high-growth states & expansion opportunities")

df_state_rank = q("""
    SELECT State,
           SUM(Transacion_count)  AS Total_Transactions,
           ROUND(SUM(Transacion_amount),2) AS Total_Amount,
           ROUND(AVG(Transacion_amount),2) AS Avg_Amount,
           RANK() OVER (ORDER BY SUM(Transacion_amount) DESC) AS Amount_Rank
    FROM aggregated_transaction
    GROUP BY State
    ORDER BY Amount_Rank
    LIMIT 15
""")

df_expansion = q("""
    SELECT State,
           SUM(Transacion_count)  AS Total_Count,
           ROUND(SUM(Transacion_amount),2) AS Total_Amount,
           ROUND(SUM(Transacion_amount)/SUM(Transacion_count),2) AS Avg_Txn_Value
    FROM aggregated_transaction
    GROUP BY State
    HAVING Avg_Txn_Value < (
        SELECT SUM(Transacion_amount)/SUM(Transacion_count)
        FROM aggregated_transaction
    )
    ORDER BY Total_Count DESC
    LIMIT 10
""")

df_top5_type = q("""
    WITH ranked AS (
        SELECT State, Transacion_type,
               SUM(Transacion_count) AS Total_Count,
               ROUND(SUM(Transacion_amount),2) AS Total_Amount,
               RANK() OVER (
                   PARTITION BY Transacion_type
                   ORDER BY SUM(Transacion_amount) DESC
               ) AS rnk
        FROM aggregated_transaction
        GROUP BY State, Transacion_type
    )
    SELECT State, Transacion_type, Total_Count, Total_Amount
    FROM ranked WHERE rnk <= 5
    ORDER BY Transacion_type, Total_Amount DESC
""")

df_districts = q("""
    SELECT District, State,
           SUM(Count) AS Total_Transactions,
           ROUND(SUM(Amount),2) AS Total_Amount
    FROM map_transaction
    GROUP BY District, State
    ORDER BY Total_Amount DESC
    LIMIT 10
""")

df_pincodes = q("""
    SELECT EntityName AS Pincode, State,
           SUM(Count) AS Total_Transactions,
           ROUND(SUM(Amount),2) AS Total_Amount
    FROM top_transaction
    WHERE EntityType='Pincode'
    GROUP BY EntityName, State
    ORDER BY Total_Amount DESC
    LIMIT 10
""")

# ── C4 Fig 1 — State Ranking (Amount + Count side by side) ───────────────────
print("  Plotting C4-F1 : State Rankings…")
fig, axes = plt.subplots(1, 2, figsize=(18, 8), facecolor=BG)
fig.suptitle("Case 4 — State Rankings: Amount vs Transaction Count",
             color=TEXT, fontsize=15, fontweight="bold")

sr = df_state_rank.sort_values("Total_Amount")
colors_r = sns.color_palette("rocket_r", len(sr))

bars = axes[0].barh(sr["State"], sr["Total_Amount"],
                    color=colors_r, edgecolor=BG, height=0.7)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(crore))
axes[0].set_title("By Transaction Amount (₹ Crore)", color=CYAN, pad=10)
axes[0].grid(axis="x", alpha=0.35); axes[0].set_axisbelow(True)
for bar, val in zip(bars, sr["Total_Amount"]):
    axes[0].text(bar.get_width() + sr["Total_Amount"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"₹{val/1e7:,.0f}Cr", va="center", fontsize=8, color=TEXT)

sr2 = df_state_rank.sort_values("Total_Transactions")
bars2 = axes[1].barh(sr2["State"], sr2["Total_Transactions"],
                     color=colors_r, edgecolor=BG, height=0.7)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(millions))
axes[1].set_title("By Transaction Count (Millions)", color=CYAN, pad=10)
axes[1].grid(axis="x", alpha=0.35); axes[1].set_axisbelow(True)
for bar, val in zip(bars2, sr2["Total_Transactions"]):
    axes[1].text(bar.get_width() + sr2["Total_Transactions"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"{val/1e6:.1f}M", va="center", fontsize=8, color=TEXT)
save(fig, "C4_F1_state_rankings")

# ── C4 Fig 2 — Expansion Opportunity States ──────────────────────────────────
print("  Plotting C4-F2 : Market Expansion Opportunities…")
fig, axes = plt.subplots(1, 2, figsize=(16, 6), facecolor=BG)
fig.suptitle("Case 4 — Market Expansion: High Volume, Below-Avg Value States",
             color=TEXT, fontsize=15, fontweight="bold")

exp = df_expansion.sort_values("Total_Count")
colors_e = sns.color_palette("mako_r", len(exp))

bars = axes[0].barh(exp["State"], exp["Total_Count"],
                    color=colors_e, edgecolor=BG, height=0.65)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(millions))
axes[0].set_title("Transaction Volume (High Count)", color=CYAN, pad=10)
axes[0].grid(axis="x", alpha=0.35); axes[0].set_axisbelow(True)
for bar, val in zip(bars, exp["Total_Count"]):
    axes[0].text(bar.get_width() + exp["Total_Count"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"{val/1e6:.1f}M", va="center", fontsize=8, color=TEXT)

bars2 = axes[1].barh(exp["State"], exp["Avg_Txn_Value"],
                     color=ORANGE, edgecolor=BG, height=0.65, alpha=0.85)
axes[1].set_xlabel("Avg Transaction Value (₹)")
axes[1].set_title("Avg Transaction Value (Below National Avg)",
                  color=ORANGE, pad=10)
axes[1].grid(axis="x", alpha=0.35); axes[1].set_axisbelow(True)
for bar, val in zip(bars2, exp["Avg_Txn_Value"]):
    axes[1].text(bar.get_width() + exp["Avg_Txn_Value"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"₹{val:,.0f}", va="center", fontsize=8, color=TEXT)
save(fig, "C4_F2_expansion_opportunities")

# ── C4 Fig 3 — Top 5 States per Transaction Type (Grouped) ───────────────────
print("  Plotting C4-F3 : Top 5 States per Transaction Type…")
fig, ax = plt.subplots(figsize=(15, 7), facecolor=BG)
fig.suptitle("Case 4 — Top 5 States per Payment Category (₹ Amount)",
             color=TEXT, fontsize=15, fontweight="bold")
sns.barplot(data=df_top5_type, x="Transacion_type", y="Total_Amount",
            hue="State", palette=sns.color_palette("husl", 5),
            ax=ax, edgecolor=BG, linewidth=0.8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(crore))
ax.set_xlabel("Payment Category"); ax.set_ylabel("Amount (₹)")
ax.legend(title="State", title_fontsize=8.5,
          loc="upper right", framealpha=0.7, fontsize=7.5)
ax.tick_params(axis="x", rotation=15)
ax.grid(axis="y", alpha=0.35); ax.set_axisbelow(True)
save(fig, "C4_F3_top5_states_per_type")

# ── C4 Fig 4 — Top Districts & Pincodes ──────────────────────────────────────
print("  Plotting C4-F4 : Top Districts & Pincodes…")
fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=BG)
fig.suptitle("Case 4 — Top 10 Districts & Pincodes by Transaction Amount",
             color=TEXT, fontsize=15, fontweight="bold")

dist = df_districts.sort_values("Total_Amount")
colors_d = sns.color_palette("flare", len(dist))
bars = axes[0].barh(
    dist["District"].str.title() + "\n(" + dist["State"] + ")",
    dist["Total_Amount"], color=colors_d, edgecolor=BG, height=0.7)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(crore))
axes[0].set_title("Top 10 Districts", color=CYAN, pad=10)
axes[0].grid(axis="x", alpha=0.35); axes[0].set_axisbelow(True)
for bar, val in zip(bars, dist["Total_Amount"]):
    axes[0].text(bar.get_width() + dist["Total_Amount"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"₹{val/1e7:,.0f}Cr", va="center", fontsize=8, color=TEXT)

pins = df_pincodes.sort_values("Total_Amount")
colors_p = sns.color_palette("mako_r", len(pins))
bars2 = axes[1].barh(
    pins["Pincode"].astype(str) + " (" + pins["State"] + ")",
    pins["Total_Amount"], color=colors_p, edgecolor=BG, height=0.7)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(crore))
axes[1].set_title("Top 10 Pincodes", color=CYAN, pad=10)
axes[1].grid(axis="x", alpha=0.35); axes[1].set_axisbelow(True)
for bar, val in zip(bars2, pins["Total_Amount"]):
    axes[1].text(bar.get_width() + pins["Total_Amount"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"₹{val/1e7:,.0f}Cr", va="center", fontsize=8, color=TEXT)
save(fig, "C4_F4_districts_pincodes")


# ═════════════════════════════════════════════════════════════════════════════
#
#  ██████╗ █████╗ ███████╗███████╗    ███████╗
# ██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔════╝
# ██║     ███████║███████╗█████╗      ███████╗
# ██║     ██╔══██║╚════██║██╔══╝      ╚════██║
# ╚██████╗██║  ██║███████║███████╗    ███████║
#  ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝
#  USER ENGAGEMENT & GROWTH STRATEGY
#
# ═════════════════════════════════════════════════════════════════════════════
section_title("CASE 5 — User Engagement & Growth Strategy",
              "Engagement scores, growth states & district-level insights")

df_engage_score = q("""
    SELECT State,
           SUM(Registered_user) AS Total_Registered,
           SUM(App_opens)       AS Total_App_Opens,
           ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Engagement_Score,
           CASE
               WHEN SUM(App_opens)/SUM(Registered_user) >= 50 THEN 'High'
               WHEN SUM(App_opens)/SUM(Registered_user) >= 20 THEN 'Medium'
               ELSE 'Low'
           END AS Engagement_Category
    FROM aggregated_user
    GROUP BY State
    ORDER BY Engagement_Score DESC
""")

df_top_districts_user = q("""
    SELECT District, State,
           SUM(Registered_user) AS Total_Registered,
           SUM(App_opens)       AS Total_App_Opens,
           ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Engagement_Score
    FROM map_user
    GROUP BY District, State
    ORDER BY Total_Registered DESC
    LIMIT 10
""")

df_user_growth = q("""
    WITH user_yearly AS (
        SELECT State, Year,
               SUM(Registered_user) AS Yearly_Users
        FROM aggregated_user
        GROUP BY State, Year
    )
    SELECT curr.State, curr.Year,
           curr.Yearly_Users AS Current_Users,
           prev.Yearly_Users AS Previous_Users,
           ROUND((curr.Yearly_Users-prev.Yearly_Users)
                 /prev.Yearly_Users*100,2) AS User_Growth_Pct
    FROM user_yearly curr
    JOIN user_yearly prev
        ON curr.State=prev.State AND curr.Year=prev.Year+1
    ORDER BY User_Growth_Pct DESC
    LIMIT 10
""")

df_top_pins_user = q("""
    SELECT EntityName AS Pincode, State,
           SUM(Registered_user) AS Total_Registered
    FROM top_user
    WHERE EntityType='Pincode'
    GROUP BY EntityName, State
    ORDER BY Total_Registered DESC
    LIMIT 10
""")

# ── C5 Fig 1 — Engagement Score by State (Color-coded Category) ──────────────
print("  Plotting C5-F1 : Engagement Score by State…")
fig, ax = plt.subplots(figsize=(14, 9), facecolor=BG)
fig.suptitle("Case 5 — State Engagement Score (App Opens / Registered Users)",
             color=TEXT, fontsize=15, fontweight="bold")

es = df_engage_score.sort_values("Engagement_Score")
color_map = {"High": GREEN, "Medium": YELLOW, "Low": ORANGE}
bar_colors = [color_map[c] for c in es["Engagement_Category"]]

bars = ax.barh(es["State"], es["Engagement_Score"],
               color=bar_colors, edgecolor=BG, height=0.7)
ax.set_xlabel("Engagement Score (App Opens per Registered User)")
ax.grid(axis="x", alpha=0.35); ax.set_axisbelow(True)

# Legend
patches = [mpatches.Patch(color=v, label=k) for k, v in color_map.items()]
ax.legend(handles=patches, title="Engagement Level",
          loc="lower right", framealpha=0.8)

for bar, val, cat in zip(bars, es["Engagement_Score"], es["Engagement_Category"]):
    ax.text(bar.get_width() + es["Engagement_Score"].max()*0.01,
            bar.get_y() + bar.get_height()/2,
            f"{val:.1f}x  [{cat}]", va="center",
            fontsize=7.5, color=color_map[cat])
save(fig, "C5_F1_engagement_score_states")

# ── C5 Fig 2 — Top 10 Districts by Users & Opens ─────────────────────────────
print("  Plotting C5-F2 : Top 10 Districts User & Engagement…")
fig, axes = plt.subplots(1, 2, figsize=(17, 7), facecolor=BG)
fig.suptitle("Case 5 — Top 10 Districts: Users & Engagement",
             color=TEXT, fontsize=15, fontweight="bold")

td = df_top_districts_user.sort_values("Total_Registered")
colors_td = sns.color_palette("rocket_r", len(td))

bars = axes[0].barh(
    td["District"].str.title() + "\n(" + td["State"] + ")",
    td["Total_Registered"],
    color=colors_td, edgecolor=BG, height=0.7)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(millions))
axes[0].set_title("By Registered Users", color=CYAN, pad=10)
axes[0].grid(axis="x", alpha=0.35); axes[0].set_axisbelow(True)
for bar, val in zip(bars, td["Total_Registered"]):
    axes[0].text(bar.get_width() + td["Total_Registered"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"{val/1e6:.2f}M", va="center", fontsize=8, color=TEXT)

bars2 = axes[1].barh(
    td["District"].str.title() + "\n(" + td["State"] + ")",
    td["Engagement_Score"],
    color=colors_td, edgecolor=BG, height=0.7)
axes[1].set_xlabel("Engagement Score")
axes[1].set_title("By Engagement Score", color=CYAN, pad=10)
axes[1].grid(axis="x", alpha=0.35); axes[1].set_axisbelow(True)
for bar, val in zip(bars2, td["Engagement_Score"]):
    axes[1].text(bar.get_width() + td["Engagement_Score"].max()*0.01,
                 bar.get_y() + bar.get_height()/2,
                 f"{val:.1f}x", va="center", fontsize=8, color=CYAN)
save(fig, "C5_F2_top_districts_engagement")

# ── C5 Fig 3 — Top States by User Growth YoY ─────────────────────────────────
print("  Plotting C5-F3 : Top States by User Growth (YoY)…")
fig, ax = plt.subplots(figsize=(13, 6), facecolor=BG)
fig.suptitle("Case 5 — Top 10 States by Year-on-Year User Growth",
             color=TEXT, fontsize=15, fontweight="bold")

ug = df_user_growth.sort_values("User_Growth_Pct")
colors_ug = sns.color_palette("viridis_r", len(ug))
bars = ax.barh(ug["State"] + " (" + ug["Year"].astype(str) + ")",
               ug["User_Growth_Pct"],
               color=colors_ug, edgecolor=BG, height=0.65)
ax.set_xlabel("YoY User Growth (%)")
ax.grid(axis="x", alpha=0.35); ax.set_axisbelow(True)
for bar, val in zip(bars, ug["User_Growth_Pct"]):
    ax.text(bar.get_width() + ug["User_Growth_Pct"].max()*0.01,
            bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=9, color=GREEN)
save(fig, "C5_F3_yoy_user_growth")

# ── C5 Fig 4 — Top 10 Pincodes by Registered Users ───────────────────────────
print("  Plotting C5-F4 : Top 10 Pincodes by Registered Users…")
fig, ax = plt.subplots(figsize=(13, 6), facecolor=BG)
fig.suptitle("Case 5 — Top 10 Pincodes by Registered Users",
             color=TEXT, fontsize=15, fontweight="bold")

pu = df_top_pins_user.sort_values("Total_Registered")
colors_pu = sns.color_palette("mako_r", len(pu))
bars = ax.barh(pu["Pincode"].astype(str) + " (" + pu["State"] + ")",
               pu["Total_Registered"],
               color=colors_pu, edgecolor=BG, height=0.65)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x/1e3:.0f}K"))
ax.set_xlabel("Registered Users")
ax.grid(axis="x", alpha=0.35); ax.set_axisbelow(True)
for bar, val in zip(bars, pu["Total_Registered"]):
    ax.text(bar.get_width() + pu["Total_Registered"].max()*0.01,
            bar.get_y() + bar.get_height()/2,
            f"{val/1e3:.1f}K", va="center", fontsize=9, color=TEXT)
save(fig, "C5_F4_top_pincodes_users")

# ── C5 Fig 5 — Engagement Category Distribution (Pie) ────────────────────────
print("  Plotting C5-F5 : Engagement Category Distribution…")
cat_counts = df_engage_score["Engagement_Category"].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)
fig.suptitle("Case 5 — Engagement Category Distribution Across States",
             color=TEXT, fontsize=15, fontweight="bold")

cat_colors = [color_map.get(c, PURPLE) for c in cat_counts.index]
wedges, texts, autotexts = axes[0].pie(
    cat_counts.values,
    labels=cat_counts.index,
    autopct="%1.1f%%",
    colors=cat_colors,
    startangle=90,
    wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
)
for t in texts:      t.set_color(TEXT);    t.set_fontsize(11); t.set_fontweight("bold")
for a in autotexts:  a.set_color("white"); a.set_fontsize(10)
axes[0].set_title("States by Engagement Category", color=TEXT, pad=12)

# Bar — count per category
bars = axes[1].bar(cat_counts.index, cat_counts.values,
                   color=cat_colors, edgecolor=BG, width=0.5)
axes[1].set_ylabel("Number of States")
axes[1].set_title("State Count per Engagement Level", color=TEXT, pad=12)
axes[1].grid(axis="y", alpha=0.35); axes[1].set_axisbelow(True)
for bar, val in zip(bars, cat_counts.values):
    axes[1].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.2,
                 f"{val} States", ha="center", fontsize=10,
                 fontweight="bold", color=TEXT)
save(fig, "C5_F5_engagement_category_distribution")


# ─────────────────────────────────────────────────────────────────────────────
#  FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print("  🎉  All Business Case Visualizations Saved!")
print(f"{'═'*60}")
print("\n  CASE 1 — Transaction Dynamics")
print("    C1_F1_payment_category_breakdown.png")
print("    C1_F2_top_bottom_states.png")
print("    C1_F3_quarterly_growth_trend.png")
print("    C1_F4_type_year_trend.png")
print("\n  CASE 2 — Device & User Engagement")
print("    C2_F1_top_mobile_brands.png")
print("    C2_F2_users_vs_appopens.png")
print("    C2_F3_low_engagement_states.png")
print("    C2_F4_brand_growth_years.png")
print("    C2_F5_quarterly_user_trend.png")
if HAS_INSURANCE:
    print("\n  CASE 3 — Insurance Penetration")
    print("    C3_F1_insurance_top10_states.png")
    print("    C3_F2_untapped_markets_trend.png")
    print("    C3_F3_insurance_penetration_rate.png")
print("\n  CASE 4 — Market Expansion")
print("    C4_F1_state_rankings.png")
print("    C4_F2_expansion_opportunities.png")
print("    C4_F3_top5_states_per_type.png")
print("    C4_F4_districts_pincodes.png")
print("\n  CASE 5 — User Engagement & Growth")
print("    C5_F1_engagement_score_states.png")
print("    C5_F2_top_districts_engagement.png")
print("    C5_F3_yoy_user_growth.png")
print("    C5_F4_top_pincodes_users.png")
print("    C5_F5_engagement_category_distribution.png")
print(f"\n  Total Charts : {'21 (+ 3 insurance)' if HAS_INSURANCE else '18'}")
print(f"{'═'*60}\n")