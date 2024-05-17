import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import colors
import numpy as np
from plot_utils import extract_segments, extract_results, extract_times, count_cores
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

for part, interval in [(4, 5000)]:
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
        if part==3:
            title = "Dynamic Scheduling policy with a 10s QPS interval"
        else:
            title = "Dynamic Scheduling policy with a 5s QPS interval"
        jobs_ax.set_title(
            title,
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
            s=150,
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
        if part==3:
            title="Using our scheduling policy with a 10s interval"
        else:
            title="Using our scheduling policy with a 5s interval"
        cores_ax.set_title(
            title,
            y=1.01,
            fontsize=12,
        )
        qps_ax = cores_ax.twinx()

        memcached_times, memcached_cores = count_cores(part, i)
        memcached_times = [time - starttime for time in memcached_times]
        for i, c in enumerate(list(memcached_cores[:-1])):
            memcached_cores.insert(2*i+1, c)
        for i, t in enumerate(list(memcached_times[:-1])):
            memcached_times.insert(2*i+1, memcached_times[2*i+1]-1)
        cores_ax.plot(memcached_times, memcached_cores, label="Memcached Cores")
        qps_ax.scatter(
            time,
            qps,
            color="limegreen",
            label="QPS",
            s=150,
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
