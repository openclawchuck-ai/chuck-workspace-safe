from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from scipy.optimize import curve_fit


DATA = [
    ("2024-05", "OpenAI", "GPT-4o", 4.90, "Scale"),
    ("2025-05", "Anthropic", "Claude Sonnet 4", 42.70, "Scale"),
    ("2025-08", "OpenAI", "GPT-5 High", 41.78, "Scale"),
    ("2025-11", "Google", "Gemini 3 Pro", 43.30, "Scale"),
    ("2025-11", "Anthropic", "Claude Opus 4.5", 45.89, "Scale"),
    ("2025-12", "DeepSeek", "DeepSeek-V3.2", 15.56, "Scale"),
    ("2025-12", "OpenAI", "GPT-5.2 Thinking", 55.60, "Vendor"),
    ("2026-02", "Anthropic", "Claude Opus 4.6", 51.90, "Scale"),
    ("2026-02", "Google", "Gemini 3.1 Pro", 46.10, "Scale"),
    ("2026-02", "OpenAI", "GPT-5.3 Codex", 56.80, "Vendor"),
    ("2026-03", "OpenAI", "GPT-5.4", 59.10, "Scale"),
    ("2026-04", "Anthropic", "Claude Opus 4.7", 64.30, "Vendor"),
    ("2026-04", "OpenAI", "GPT-5.5", 58.60, "Vendor"),
    ("2026-05", "Anthropic", "Claude Opus 4.8", 69.20, "Vendor"),
    ("2026-06", "Anthropic", "Claude Mythos 5", 80.30, "Vendor"),
]

COLORS = {
    "OpenAI": "#10A37F",
    "Google": "#4285F4",
    "Anthropic": "#D97757",
    "DeepSeek": "#38BDF8",
}


def main():
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(16, 9), dpi=180)
    fig.patch.set_facecolor("#080D18")
    ax.set_facecolor("#0C1423")

    # Plot companies separately while using marker shape to distinguish source.
    for date_text, company, model, score, source in DATA:
        date = datetime.strptime(date_text, "%Y-%m")
        marker = "o" if source == "Scale" else "D"
        face = COLORS[company] if source == "Scale" else "none"
        ax.scatter(
            date,
            score,
            s=120 if source == "Scale" else 112,
            marker=marker,
            facecolor=face,
            edgecolor=COLORS[company] if source == "Vendor" else "#F8FAFC",
            linewidth=2.2 if source == "Vendor" else 0.9,
            alpha=0.98,
            zorder=4,
        )

    # Exponential fit to the cumulative capability frontier: the highest score
    # available at each point in time, regardless of evaluation source.
    sorted_rows = sorted(DATA, key=lambda row: datetime.strptime(row[0], "%Y-%m"))
    frontier_dates = []
    frontier_scores = []
    best = -np.inf
    for date_text, _, _, score, _ in sorted_rows:
        date = datetime.strptime(date_text, "%Y-%m")
        if score > best:
            best = score
            frontier_dates.append(date)
            frontier_scores.append(score)

    frontier_nums = mdates.date2num(frontier_dates)
    x_months = (frontier_nums - frontier_nums.min()) / 30.4375
    frontier_scores = np.array(frontier_scores)

    def exponential(x, floor, amplitude, rate):
        return floor + amplitude * np.exp(rate * x)

    params, _ = curve_fit(
        exponential,
        x_months,
        frontier_scores,
        p0=(0.0, 5.0, 0.08),
        maxfev=20000,
    )
    curve_nums = np.linspace(frontier_nums.min(), mdates.date2num(datetime(2026, 6, 1)), 400)
    curve_months = (curve_nums - frontier_nums.min()) / 30.4375
    curve_scores = exponential(curve_months, *params)
    ax.plot(
        mdates.num2date(curve_nums),
        curve_scores,
        color="#F8FAFC",
        linewidth=2.8,
        alpha=0.92,
        zorder=3,
    )
    ax.fill_between(
        mdates.num2date(curve_nums),
        np.clip(curve_scores, 0, 90),
        0,
        color="#8B5CF6",
        alpha=0.065,
        zorder=1,
    )

    texts = []
    for date_text, _, model, score, _ in DATA:
        texts.append(
            ax.text(
                datetime.strptime(date_text, "%Y-%m"),
                score,
                model,
                color="#E2E8F0",
                fontsize=8.1,
                zorder=5,
            )
        )
    adjust_text(
        texts,
        ax=ax,
        expand=(1.16, 1.28),
        force_text=(0.42, 0.65),
        force_points=(0.30, 0.45),
        arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.6, alpha=0.75),
    )

    ax.set_title(
        "The Software Engineering Curve",
        loc="left",
        fontsize=26,
        fontweight="bold",
        color="#F8FAFC",
        pad=22,
    )
    ax.text(
        0,
        1.015,
        "SWE-bench Pro performance across major frontier-model releases",
        transform=ax.transAxes,
        fontsize=12,
        color="#94A3B8",
    )
    ax.set_xlabel("Model release date", fontsize=11, color="#CBD5E1", labelpad=12)
    ax.set_ylabel("SWE-bench Pro resolved (%)", fontsize=11, color="#CBD5E1", labelpad=12)
    ax.set_ylim(0, 88)
    ax.set_xlim(datetime(2024, 3, 1), datetime(2026, 7, 15))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
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
    source_handles = [
        mlines.Line2D([], [], color="#F8FAFC", marker="o", linestyle="none", markersize=8, label="Scale run"),
        mlines.Line2D(
            [],
            [],
            color="#F8FAFC",
            marker="D",
            markerfacecolor="none",
            markeredgewidth=1.8,
            linestyle="none",
            markersize=8,
            label="Vendor scaffold",
        ),
        mlines.Line2D([], [], color="#F8FAFC", linewidth=2.5, label="Frontier exponential fit"),
    ]
    legend = ax.legend(
        handles=company_handles + source_handles,
        ncol=4,
        loc="upper left",
        frameon=True,
        facecolor="#111827",
        edgecolor="#334155",
        fontsize=8.8,
    )
    for text in legend.get_texts():
        text.set_color("#E2E8F0")

    ax.text(
        1,
        -0.14,
        "Solid circles: Scale leaderboard • Outlined diamonds: vendor launch scaffold • Trend follows the cumulative performance frontier",
        transform=ax.transAxes,
        ha="right",
        fontsize=8.5,
        color="#64748B",
    )

    plt.tight_layout()
    output = "/home/chuck/.openclaw/workspace/swebench_pro_progress.png"
    plt.savefig(output, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(output)


if __name__ == "__main__":
    main()
