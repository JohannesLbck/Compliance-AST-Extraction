import pandas as pd
import matplotlib.pyplot as plt


def build_study_execution_df(df, columns_config):
    """Return a dataframe with only study execution columns that exist in df."""
    study_execution_columns = [
        col for col in columns_config["study_execution"] if col in df.columns
    ]
    return df[study_execution_columns].copy()


def study_execution_vis(study_execution_df):
    """Create pie charts for first 3 columns and swapped-axis bar chart for the rest."""
    if study_execution_df.empty:
        print("No study execution data available for plotting.")
        return

    plot_df = study_execution_df.copy()

    # Keep charts readable: collapse highly variable free-text columns.
    for col in plot_df.columns:
        non_null_unique = plot_df[col].dropna().nunique()
        if non_null_unique > 8:
            plot_df[col] = plot_df[col].apply(
                lambda value: "No response" if pd.isna(value) else "Text response"
            )
        else:
            plot_df[col] = plot_df[col].fillna("No response")

    pie_columns = list(plot_df.columns[:3])
    bar_columns = list(plot_df.columns[3:])

    if pie_columns:
        fig, axes = plt.subplots(1, len(pie_columns), figsize=(6 * len(pie_columns), 6))
        if len(pie_columns) == 1:
            axes = [axes]

        for idx, col in enumerate(pie_columns):
            counts = plot_df[col].value_counts()
            axes[idx].pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
            axes[idx].set_title(f"Q{idx + 1}")

        plt.tight_layout()
        plt.show()

    if bar_columns:
        bar_df = plot_df[bar_columns]
        counts_df = bar_df.apply(lambda col: col.value_counts()).T.fillna(0)

        ax = counts_df.plot(kind="barh", stacked=True, figsize=(14, 7))
        ax.set_title("Study Execution Responses (Stacked Horizontal)")
        ax.set_xlabel("Count")
        ax.set_ylabel("Study Execution Question")
        ax.set_yticks(range(len(counts_df.index)))
        ax.set_yticklabels([f"Q{i+4}" for i in range(len(counts_df.index))])
        ax.legend(title="Response", bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        plt.show()


def run_study_execution_analysis(df, columns_config):
    """Build and visualize study execution analysis."""
    study_execution_df = build_study_execution_df(df, columns_config)
    print(study_execution_df.head())
    study_execution_vis(study_execution_df)
