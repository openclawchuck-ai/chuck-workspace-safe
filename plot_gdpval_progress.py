from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from scipy.optimize import curve_fit


DATA = [
    ("2025-09", "Anthropic", "Claude Sonnet 4.5", 1277, "v1"),
    ("2025-11", "Google", "Gemini 3 Pro", 1195, "v1"),
    ("2025-11", "Anthropic", "Claude Opus 4.5", 1416, "v1"),
    ("2025-12", "DeepSeek", "DeepSeek-V3.2", 1203, "v1"),
    ("2025-12", "OpenAI", "GPT-5.2", 1462, "v1"),
    ("2026-02", "Google", "Gemini 3.1 Pro", 971, "v2"),
    ("2026-02", "Anthropic", "Claude Sonnet 4.6", 1395, "v2"),
    ("2026-03", "OpenAI", "GPT-5.4 (xhigh)", 1401, "v2"),
    ("2026-04", "xAI", "Grok 4.3 (high)", 1094, "v2"),
    ("2026-04", "DeepSeek", "DeepSeek V4 Pro", 1318, "v2"),
    ("2026-04", "OpenAI", "GPT-5.5 (xhigh)", 1509, "v2"),
    ("2026-04", "Anthropic", "Claude Opus 4.7", 1512, "v2"),
    ("2026-05", "Google", "Gemini 3.5 Flash (high)", 1357, "v2"),
    ("2026-05", "Anthropic", "Claude Opus 4.8", 1615, "v2"),
    ("2026-06", "Anthropic", "Claude Fable 5*", 1783, "v2"),
]

COLORS = {
    "OpenAI": "#10A37F",
    "Google": "#4285F4",
    "Anthropic": "#D97757",
    "xAI": "#A78BFA",
    "DeepSeek": "#38BDF8",
}


def main():
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(16, 9), dpi=180)
    fig.patch.set_facecolor("#080D18")
    ax.set_facecolor("#0C1423")

    for date_text, company, _, score, version in DATA:
        ax.scatter(
            datetime.strptime(date_text, "%Y-%m"),
            score,
            s=130,
            marker="D" if version == "v1" else "o",
            facecolor="none" if version == "v1" else COLORS[company],
            edgecolor=COLORS[company] if version == "v1" else "#F8FAFC",
            linewidth=2.2 if version == "v1" else 0.9,
            alpha=0.98,
            zorder=4,
        )

    # Build the monthly cumulative frontier.
    v2_data = [row for row in DATA if row[4] == "v2"]
    months = sorted(set(row[0] for row in v2_data))
    frontier_dates = []
    frontier_scores = []
    best = -np.inf
    for month in months:
        month_best = max(row[3] for row in v2_data if row[0] == month)
        best = max(best, month_best)
        frontier_dates.append(datetime.strptime(month, "%Y-%m"))
        frontier_scores.append(best)

    nums = mdates.date2num(frontier_dates)
    x_months = (nums - nums.min()) / 30.4375
    frontier_scores = np.array(frontier_scores)

    def exponential(x, floor, amplitude, rate):
        return floor + amplitude * np.exp(rate * x)

    params, _ = curve_fit(
        exponential,
        x_months,
        frontier_scores,
        p0=(1100.0, 250.0, 0.2),
        maxfev=20000,
    )
    curve_nums = np.linspace(nums.min(), nums.max(), 300)
    curve_months = (curve_nums - nums.min()) / 30.4375
    curve_scores = exponential(curve_months, *params)
    ax.plot(
        mdates.num2date(curve_nums),
        curve_scores,
        color="#F8FAFC",
        linewidth=3.0,
        alpha=0.92,
        label="Frontier exponential fit",
        zorder=3,
    )
    ax.fill_between(
        mdates.num2date(curve_nums),
        curve_scores,
        800,
        color="#8B5CF6",
        alpha=0.07,
        zorder=1,
    )

    # Show the earlier v1 capability frontier as a distinct dashed trajectory.
    v1_data = sorted(
        [row for row in DATA if row[4] == "v1"],
        key=lambda row: datetime.strptime(row[0], "%Y-%m"),
    )
    v1_dates = []
    v1_scores = []
    v1_best = -np.inf
    for date_text, _, _, score, _ in v1_data:
        if score > v1_best:
            v1_best = score
            v1_dates.append(datetime.strptime(date_text, "%Y-%m"))
            v1_scores.append(score)
    ax.plot(
        v1_dates,
        v1_scores,
        color="#CBD5E1",
        linewidth=2.2,
        linestyle=(0, (4, 4)),
        alpha=0.8,
        zorder=3,
    )

    # Artificial Analysis anchors the human baseline at Elo 1,000.
    ax.axhline(
        1000,
        color="#FBBF24",
        linewidth=1.5,
        linestyle=(0, (5, 5)),
        alpha=0.9,
        label="Human baseline (1000)",
        zorder=2,
    )

    texts = []
    for date_text, _, model, score, _ in DATA:
        texts.append(
            ax.text(
                datetime.strptime(date_text, "%Y-%m"),
                score,
                model,
                color="#E2E8F0",
                fontsize=8.6,
                zorder=5,
            )
        )
    adjust_text(
        texts,
        ax=ax,
        expand=(1.18, 1.32),
        force_text=(0.48, 0.75),
        force_points=(0.35, 0.55),
        arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.65, alpha=0.75),
    )

    ax.set_title(
        "The Economic Work Curve",
        loc="left",
        fontsize=26,
        fontweight="bold",
        color="#F8FAFC",
        pad=22,
    )
    ax.text(
        0,
        1.015,
        "GDPval-AA v1 and v2 performance on economically valuable professional tasks",
        transform=ax.transAxes,
        fontsize=12,
        color="#94A3B8",
    )
    ax.set_xlabel("Model release date", fontsize=11, color="#CBD5E1", labelpad=12)
    ax.set_ylabel("GDPval-AA Elo rating", fontsize=11, color="#CBD5E1", labelpad=12)
    ax.set_ylim(800, 1880)
    ax.set_xlim(datetime(2025, 8, 15), datetime(2026, 6, 20))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.yaxis.set_major_locator(plt.MultipleLocator(100))
    ax.grid(True, color="#334155", linewidth=0.7, alpha=0.45)
    ax.tick_params(colors="#94A3B8")
    for spine in ax.spines.values():
        spine.set_color("#334155")

    company_handles = [
        mlines.Line2D(
            [],
            [],
            color="none",
            marker="o",
            markerfacecolor=color,
            markeredgecolor="#F8FAFC",
            markersize=9,
            label=company,
        )
        for company, color in COLORS.items()
    ]
    version_handles = [
        mlines.Line2D(
            [],
            [],
            color="#CBD5E1",
            marker="D",
            markerfacecolor="none",
            markeredgewidth=1.8,
            linestyle=(0, (4, 4)),
            markersize=8,
            label="GDPval-AA v1",
        ),
        mlines.Line2D(
            [],
            [],
            color="#F8FAFC",
            marker="o",
            linestyle="-",
            markersize=8,
            label="GDPval-AA v2",
        ),
        mlines.Line2D(
            [],
            [],
            color="#FBBF24",
            linestyle=(0, (5, 5)),
            linewidth=1.5,
            label="Human baseline (1000)",
        ),
    ]
    legend = ax.legend(
        handles=company_handles + version_handles,
        ncol=4,
        loc="upper left",
        frameon=True,
        facecolor="#111827",
        edgecolor="#334155",
        fontsize=9,
    )
    for text in legend.get_texts():
        text.set_color("#E2E8F0")

    ax.text(
        1,
        -0.145,
        "Outlined diamonds/dashed frontier: GDPval-AA v1 • Solid circles/curve: v2 • * Fable 5 used Opus 4.8 fallback",
        transform=ax.transAxes,
        ha="right",
        fontsize=8.5,
        color="#64748B",
    )

    plt.tight_layout()
    output = "/home/chuck/.openclaw/workspace/gdpval_progress.png"
    plt.savefig(output, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(output)


if __name__ == "__main__":
    main()
