import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import colors
import numpy as np
from plot_utils import extract_segments, extract_results, extract_times
from matplotlib.lines import Line2D


JOBS_COLORS = {
    "blackscholes": "#CCA000",
    "canneal": "#CCCCAA",
    "dedup": "#CCACCA",
    "ferret": "#AACCCA",
    "freqmine": "#0CCA00",
    "radix": "#00CCA0",
    "vips": "#CC0A00",
}
jobs_lines = [
    Line2D([0], [0], color=color, label=name, lw=4)
    for name, color in JOBS_COLORS.items()
]
bar_lines = [
    Line2D(
        [0],
        [0],
        marker="s",
        color="w",
        label="Latency",
        markerfacecolor="r",
        markersize=10,
    ),
    Line2D(
        [0],
        [0],
        marker="^",
        color="w",
        label="QPS",
        markerfacecolor="limegreen",
        markersize=10,
    ),
]

for part, interval in [(3, 10000)]:
    for i in range(1, 4):
        # Extract the data for the run
        runs_segments = extract_segments(part)
        jobs = runs_segments[i]
        runs_data = extract_results(part, interval)
        data = runs_data[i]
        runs_times = extract_times(part)
        (starttime, endtime) = runs_times[i]
        time = [time - starttime for _, _, time in data]  # Time values
        qps = [qps for qps, _, _ in data]
        latency = [latency for _, latency, _ in data]

        # Generate subplots
        f, (jobs_ax, lat_ax) = plt.subplots(
            2,
            1,
            sharex=True,
            gridspec_kw={"height_ratios": [1, 3], "hspace": 0.1},
        )

        # Subplot 1 - CPU cores usage
        for job in jobs.values():
            for segment in job.segments:
                jobs_ax.plot(
                    [float(segment.start) - starttime, float(segment.end) - starttime],
                    [int(segment.core), int(segment.core)],
                    color=JOBS_COLORS[job.name],
                    linewidth=20,
                    solid_capstyle="butt",
                )
        jobs_ax.legend(jobs_lines, JOBS_COLORS.keys())
        jobs_ax.tick_params("x", labelbottom=True)
        padding = 10
        # jobs_ax.xlim(0, endtime - starttime + padding)
        jobs_ax.set_yticks([0, 1, 2, 3])
        jobs_ax.set_ylim(-0.5, 3.5)
        jobs_ax.set_ylabel("CPU Cores")

        plt.suptitle(
            f"Plot {i}A\nMemcached and PARSEC - 95th percentile latency and QPS vs. Time",
            y=0.97,
            fontsize=16,
        )
        jobs_ax.set_title(
            f"Dynamic Scheduling policy with a 5s QPS interval",
            y=1.01,
            fontsize=12,
        )

        # Modify x-axis tick labels to seconds
        def format_seconds(x, pos):
            seconds = int(x / 1000)  # Convert milliseconds to seconds
            return f"{seconds}"

        # Modify y-axis QPS ticks
        def format_qps(x, pos):
            if x == 0:
                return "0"
            return f"{x/1000:.0f}K"

        lat_ax.bar(
            time,
            latency,
            width=interval,
            align="center",
            color=[(min(l, 1), 0, 0) for l in latency],
            zorder=3,
            label="Latency",
        )
        lat_ax.axhline(y=1, color="#555", linestyle="--", linewidth=1, label="1ms SLO")

        qps_ax = lat_ax.twinx()
        qps_ax.scatter(
            time,
            qps,
            color="limegreen",
            label="QPS",
            s=20,
            marker=".",
        )

        lat_ax.grid(True, linestyle="--", linewidth=0.5, which="major")
        lat_ax.xaxis.grid(
            True, linestyle="--", color="#e1e1e1", linewidth=0.5, which="minor"
        )

        lat_ax.set_xlabel("Time [s]")
        lat_ax.set_ylabel("95th Percentile Latency [ms]")
        qps_ax.set_ylabel("QPS")

        lat_ax.set_xlim(0, 900_000)
        lat_ax.set_ylim(0, 1.6)
        qps_ax.set_ylim(0, 120_000)

        lat_ax.locator_params(axis="x", nbins=9)
        lat_ax.locator_params(axis="y", nbins=8)
        # qps_ax.locator_params(axis="y", nbins=8)
        qps_ax.set_yticks(np.linspace(0, 120_000, 9))

        lat_ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_seconds))
        qps_ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_qps))

        jobs_ax.xaxis.set_minor_locator(ticker.MultipleLocator(25_000))
        lat_ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
        qps_ax.yaxis.set_minor_locator(ticker.MultipleLocator(5000))

        lat_ax.legend(loc="upper left")
        qps_ax.legend(loc="upper right")

        size = (lat_ax.bbox.width, lat_ax.bbox.height)
        plt.show()
        
        f, (cores_ax, fake_ax) = plt.subplots(
            2,
            1,
            gridspec_kw={"height_ratios": [3, 1], "hspace": 0.1},
        )
        plt.suptitle(
            f"Plot {i}B\nMemcached and PARSEC - Memcached cores and QPS vs. Time",
            y=0.97,
            fontsize=16,
        )
        cores_ax.set_title(
            f"Using our scheduling policy with a 5s interval",
            y=1.01,
            fontsize=12,
        )
        qps_ax = cores_ax.twinx()

        memcached_cores = np.full_like(time, 2)
        cores_ax.plot(time, memcached_cores, label="Memcached Cores")
        qps_ax.scatter(
            time,
            qps,
            color="limegreen",
            label="QPS",
            s=20,
            marker=".",
        )

        cores_ax.set_xlabel("Time [s]")
        cores_ax.set_ylabel("Memcached Cores")
        qps_ax.set_ylabel("QPS")

        cores_ax.set_xlim(0, 900_000)
        cores_ax.set_ylim(0, 4)
        qps_ax.set_ylim(0, 120_000)

        qps_ax.set_yticks(np.linspace(0, 120_000, 9))

        cores_ax.locator_params(axis="x", nbins=9)
        cores_ax.locator_params(axis="y", nbins=4)

        cores_ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_seconds))
        qps_ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_qps))

        cores_ax.xaxis.set_minor_locator(ticker.MultipleLocator(25_000))
        qps_ax.yaxis.set_minor_locator(ticker.MultipleLocator(5000))

        cores_ax.legend(loc="upper left")
        qps_ax.legend(loc="upper right")

        cores_ax.grid(True, linestyle="--", linewidth=0.5, which="major")
        cores_ax.xaxis.grid(
            True, linestyle="--", color="#e1e1e1", linewidth=0.5, which="minor"
        )

        fake_ax.axis("off")

        plt.show()

# import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker
# import numpy as np
# from plot_utils import extract_segments, extract_results, extract_times
# from matplotlib.lines import Line2D

# JOBS_COLORS = {
#     "blackscholes": "#CCA000",
#     "canneal": "#CCCCAA",
#     "dedup": "#CCACCA",
#     "ferret": "#AACCCA",
#     "freqmine": "#0CCA00",
#     "radix": "#00CCA0",
#     "vips": "#CC0A00",
# }
# jobs_lines = [
#     Line2D([0], [0], color=color, label=name, lw=4)
#     for name, color in JOBS_COLORS.items()
# ]

# event_lines = [
#     Line2D([0], [0], color='black', linestyle='-', lw=2, label='Job Start/Resume'),
#     Line2D([0], [0], color='red', linestyle=':', lw=2, label='Job Pause'),
#     Line2D([0], [0], color='blue', linestyle='--', lw=2, label='Job End'),
# ]

# def format_seconds(x, pos):
#     seconds = int(x / 1000)  # Convert milliseconds to seconds
#     return f"{seconds}"

# def format_qps(x, pos):
#     if x == 0:
#         return "0"
#     return f"{x/1000:.0f}K"

# def plot_jobs(axes, jobs, starttime, endtime):
#     height_step = 0.2  # Step to separate job periods visually
#     for idx, (job_name, job) in enumerate(jobs.items()):
#         for segment in job.segments:
#             start_time = float(segment.start) - starttime
#             end_time = float(segment.end) - starttime
#             axes.axvspan(start_time, end_time, color=JOBS_COLORS[job_name], alpha=0.3, ymin=0, ymax=height_step * (idx + 1))
#             axes.axvline(x=start_time, color='black', linestyle='-')
#             if start_time != end_time:
#                 axes.axvline(x=end_time, color='blue', linestyle='--')

# for part, interval in [(3, 10000)]:
#     for i in range(1, 4):
#         # Extract the data for the run
#         runs_segments = extract_segments(part)
#         jobs = runs_segments[i]
#         runs_data = extract_results(part, interval)
#         data = runs_data[i]
#         runs_times = extract_times(part)
#         (starttime, endtime) = runs_times[i]
#         time = [time - starttime for _, _, time in data]  # Time values
#         qps = [qps for qps, _, _ in data]
#         latency = [latency for _, latency, _ in data]

#         # Generate subplots for job running periods, 1A and 1B
#         fig, axes = plt.subplots(2, 1, figsize=(12, 12), sharex=True, gridspec_kw={'height_ratios': [2, 2]})

#         # Plot 1A: Latency and QPS
#         plot_jobs(axes[0], jobs, starttime, endtime)
        
#         axes[0].bar(
#             time,
#             latency,
#             width=interval,
#             align="center",
#             color=[(min(l, 1), 0, 0) for l in latency],
#             zorder=3,
#             label="Latency",
#         )
#         axes[0].axhline(y=1, color="#555", linestyle="--", linewidth=1, label="1ms SLO")

#         qps_ax = axes[0].twinx()
#         qps_ax.scatter(
#             time,
#             qps,
#             color="limegreen",
#             label="QPS",
#             s=20,
#             marker=".",
#         )

#         axes[0].set_ylabel("95th Percentile Latency [ms]")
#         qps_ax.set_ylabel("QPS")
#         axes[0].set_xlim(0, 900_000)
#         axes[0].set_ylim(0, 1.6)
#         qps_ax.set_ylim(0, 120_000)
#         qps_ax.set_yticks(np.linspace(0, 120_000, 9))

#         axes[0].xaxis.set_major_formatter(ticker.FuncFormatter(format_seconds))
#         qps_ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_qps))

#         axes[0].grid(True, linestyle="--", linewidth=0.5, which="major")
#         axes[0].xaxis.grid(True, linestyle="--", color="#e1e1e1", linewidth=0.5, which="minor")

#         # Plot 1B: Memcached cores and QPS
#         cores_ax = axes[1]
#         qps_ax2 = cores_ax.twinx()

#         memcached_cores = np.full_like(time, 2)
#         cores_ax.plot(time, memcached_cores, label="Memcached Cores", color='blue')
#         qps_ax2.scatter(
#             time,
#             qps,
#             color="limegreen",
#             label="QPS",
#             s=20,
#             marker=".",
#         )

#         cores_ax.set_xlabel("Time [s]")
#         cores_ax.set_ylabel("Memcached Cores")
#         qps_ax2.set_ylabel("QPS")
#         cores_ax.set_xlim(0, 900_000)
#         cores_ax.set_ylim(0, 4)
#         qps_ax2.set_ylim(0, 120_000)
#         qps_ax2.set_yticks(np.linspace(0, 120_000, 9))

#         cores_ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_seconds))
#         qps_ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_qps))

#         cores_ax.grid(True, linestyle="--", linewidth=0.5, which="major")
#         cores_ax.xaxis.grid(True, linestyle="--", color="#e1e1e1", linewidth=0.5, which="minor")

#         fig.suptitle(f"Run {i}", fontsize=16)
#         axes[0].set_title("Plot A: 95th Percentile Latency and QPS vs. Time")
#         cores_ax.set_title("Plot B: Memcached Cores and QPS vs. Time")

#         # Add legends
#         handles, labels = axes[0].get_legend_handles_labels()
#         handles.extend(event_lines)
#         handles.extend(jobs_lines)
#         labels.extend([line.get_label() for line in event_lines])
#         labels.extend([line.get_label() for line in jobs_lines])
#         axes[0].legend(handles=handles, labels=labels, loc='upper right')

#         plt.tight_layout(rect=[0, 0, 1, 0.96])
#         plt.show()

