import os
import matplotlib.pyplot as plt
import numpy as np


def plot_and_save_osa_trace(
    wavelengths_nm: np.ndarray,
    powers_dbm: np.ndarray,
    trace_name: str = "Trace A",
    output_image_path: str = "osa_spectrum.png",
    output_csv_path: str = None,
    show_plot: bool = True,
):
    """Plot optical spectrum analyzer trace data and save it to file.

    :param wavelengths_nm: Array of wavelength values in nanometers.
    :param powers_dbm: Array of power values in dBm.
    :param trace_name: Title/label for the trace (e.g., 'Trace A').
    :param output_image_path: File path to save the generated plot image.
    :param output_csv_path: Optional file path to export raw (Wavelength, Power) data to CSV.
    :param show_plot: If True, opens an interactive window displaying the plot.
    """
    # 1. Identify peak signal for visual annotation
    peak_idx = np.argmax(powers_dbm)
    peak_wl = wavelengths_nm[peak_idx]
    peak_pwr = powers_dbm[peak_idx]

    # 2. Configure Matplotlib plot style
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    # 3. Plot spectrum line
    ax.plot(wavelengths_nm, powers_dbm, color="#0055ff", linewidth=1.2, label=trace_name)

    # 4. Highlight the Peak Power point
    ax.plot(peak_wl, peak_pwr, marker="o", color="red", markersize=5, label="Peak")

    # Add peak annotation text box
    annotation_text = f"Peak: {peak_pwr:.2f} dBm\n@ {peak_wl:.3f} nm"
    ax.annotate(
        annotation_text,
        xy=(peak_wl, peak_pwr),
        xytext=(15, -25),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="red", lw=1),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="red", alpha=0.8),
        fontsize=9,
        fontweight="bold",
    )

    # 5. Set axis labels and titles
    ax.set_title(f"Yokogawa AQ6370B Optical Spectrum - {trace_name}", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Wavelength (nm)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Power Level (dBm)", fontsize=11, fontweight="bold")

    # Set dynamic limits with padding
    ax.set_xlim(wavelengths_nm[0], wavelengths_nm[-1])
    ax.set_ylim(np.min(powers_dbm) - 5, max(peak_pwr + 5, -10))

    # Grid and Legend
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()

    # 6. Save image to disk
    plt.savefig(output_image_path, dpi=300, bbox_inches="tight")
    print(f"Plot successfully saved to: {os.path.abspath(output_image_path)}")

    # 7. Optional: Save to CSV
    if output_csv_path:
        data = np.column_stack((wavelengths_nm, powers_dbm))
        header = "Wavelength_nm,Power_dBm"
        np.savetxt(output_csv_path, data, delimiter=",", header=header, comments="", fmt="%.6f")
        print(f"Raw data exported to: {os.path.abspath(output_csv_path)}")

    # 8. Display interactive window
    if show_plot:
        plt.show()
    else:
        plt.close(fig)


# ==========================================
# Example Usage with Simulated OSA Data
# ==========================================
if __name__ == "__main__":
    # Generate mock spectrum data (e.g., 1050 nm laser peak with noise background)
    wl = np.linspace(1000.0, 1100.0, 1001)
    noise_floor = -65.0 + np.random.normal(0, 0.5, len(wl))

    # Add a Gaussian peak centered around 1050 nm
    laser_signal = 10.0 * np.exp(-((wl - 1050.0) ** 2) / (2 * (0.2**2)))
    power = noise_floor + laser_signal

    # Call plotting function
    plot_and_save_osa_trace(
        wavelengths_nm=wl,
        powers_dbm=power,
        trace_name="Trace A (1050nm Source)",
        output_image_path="osa_trace_capture.png",
        output_csv_path="osa_trace_data.csv",
        show_plot=True,
    )