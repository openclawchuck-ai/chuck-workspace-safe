from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text


DATA = [
    ("2024-02", "Google", "Gemini 1.5 Pro", 4.6),
    ("2024-05", "OpenAI", "GPT-4o", 2.7),
    ("2024-08", "xAI", "Grok 2", 3.9),
    ("2024-10", "Anthropic", "Claude 3.5 Sonnet", 4.1),
    ("2024-12", "Google", "Gemini 2.0 Flash Thinking", 6.6),
    ("2024-12", "OpenAI", "o1", 8.0),
    ("2025-01", "DeepSeek", "DeepSeek-R1", 9.4),
    ("2025-02", "Anthropic", "Claude 3.7 Sonnet Thinking", 8.9),
    ("2025-03", "Google", "Gemini 2.5 Pro", 21.6),
    ("2025-04", "OpenAI", "GPT-4.1", 5.4),
    ("2025-04", "OpenAI", "o3", 20.3),
    ("2025-05", "Anthropic", "Claude Opus 4", 10.7),
    ("2025-05", "DeepSeek", "DeepSeek-R1-0528", 14.0),
    ("2025-07", "xAI", "Grok 4 Heavy", 44.4),
    ("2025-08", "OpenAI", "GPT-5", 24.8),
    ("2025-09", "Anthropic", "Claude Sonnet 4.5", 13.7),
    ("2025-11", "Google", "Gemini 3 Pro", 45.8),
    ("2025-11", "Anthropic", "Claude Opus 4.5", 43.2),
    ("2025-12", "DeepSeek", "DeepSeek-V3.2", 40.8),
    ("2025-12", "OpenAI", "GPT-5.2 Pro", 36.6),
    ("2026-02", "Anthropic", "Claude Opus 4.6", 53.0),
    ("2026-02", "Google", "Gemini 3.1 Pro", 51.4),
    ("2026-03", "OpenAI", "GPT-5.4 Pro", 58.7),
    ("2026-04", "Anthropic", "Claude Opus 4.7", 54.7),
    ("2026-04", "OpenAI", "GPT-5.5 Pro", 57.2),
    ("2026-05", "Anthropic", "Claude Opus 4.8", 57.9),
    ("2026-06", "Anthropic", "Claude Mythos 5", 64.5),
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
    fig.patch.set_facecolor("#090E1A")
    ax.set_facecolor("#0D1424")

    dates = [datetime.strptime(row[0], "%Y-%m") for row in DATA]
    nums = mdates.date2num(dates)
    scores = np.array([row[3] for row in DATA])

    for company, color in COLORS.items():
        rows = [row for row in DATA if row[1] == company]
        company_dates = [datetime.strptime(row[0], "%Y-%m") for row in rows]
        company_scores = [row[3] for row in rows]
        ax.scatter(
            company_dates,
            company_scores,
            s=105,
            color=color,
            edgecolor="#F8FAFC",
            linewidth=0.8,
            alpha=0.95,
            label=company,
            zorder=4,
        )

    # Quadratic least-squares curve, suited to the visibly accelerating trajectory.
    centered = nums - nums.min()
    coefficients = np.polyfit(centered, scores, 2)
    curve_dates = np.linspace(nums.min(), nums.max(), 400)
    curve_scores = np.polyval(coefficients, curve_dates - nums.min())
    ax.plot(
        mdates.num2date(curve_dates),
        curve_scores,
        color="#F8FAFC",
        linewidth=2.8,
        alpha=0.9,
        label="Quadratic best fit",
        zorder=3,
    )
    ax.fill_between(
        mdates.num2date(curve_dates),
        curve_scores,
        0,
        color="#8B5CF6",
        alpha=0.07,
        zorder=1,
    )

    texts = []
    for date_text, _, model, score in DATA:
        texts.append(
            ax.text(
                datetime.strptime(date_text, "%Y-%m"),
                score,
                model,
                color="#E2E8F0",
                fontsize=7.4,
                zorder=5,
            )
        )
    adjust_text(
        texts,
        ax=ax,
        expand=(1.12, 1.22),
        force_text=(0.35, 0.55),
        force_points=(0.25, 0.4),
        arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.55, alpha=0.7),
    )

    ax.set_title(
        "The Intelligence Curve",
        loc="left",
        fontsize=26,
        fontweight="bold",
        color="#F8FAFC",
        pad=22,
    )
    ax.text(
        0,
        1.015,
        "Humanity’s Last Exam scores across major frontier-model releases",
        transform=ax.transAxes,
        fontsize=12,
        color="#94A3B8",
    )
    ax.set_xlabel("Model release date", fontsize=11, color="#CBD5E1", labelpad=12)
    ax.set_ylabel("Humanity’s Last Exam score (%)", fontsize=11, color="#CBD5E1", labelpad=12)
    ax.set_ylim(0, 70)
    ax.set_xlim(datetime(2024, 1, 1), datetime(2026, 7, 15))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
    ax.grid(True, color="#334155", linewidth=0.7, alpha=0.45)
    ax.tick_params(colors="#94A3B8")
    for spine in ax.spines.values():
        spine.set_color("#334155")

    legend = ax.legend(
        ncol=3,
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
        -0.14,
        "Tool-enabled scores used where available • Some historical results use text-only HLE subsets",
        transform=ax.transAxes,
        ha="right",
        fontsize=8.5,
        color="#64748B",
    )

    plt.tight_layout()
    output = "/home/chuck/.openclaw/workspace/ai_hle_intelligence_progress.png"
    plt.savefig(output, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(output)


if __name__ == "__main__":
    main()
