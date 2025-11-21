import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button, RadioButtons
import math

# --- Calculation functions ---

def compute_distance_classic(f_mhz, n, pt, gt, gr, ltx, lrx, loth, fm, sens):
    """Classic model (reference 1 km, 32.44 constant)."""
    k = 32.44
    C = pt + gt + gr - (ltx + lrx + loth) - fm - sens - k - 20 * math.log10(f_mhz)
    d_km = 10 ** (C / (10 * n))
    lp = k + 20 * math.log10(f_mhz) + 10 * n * math.log10(d_km)
    pl_d0 = k + 20 * math.log10(f_mhz)  # FSPL at 1 km
    return d_km, lp, C, 1000.0, pl_d0


def compute_distance_logdist(f_mhz, n, pt, gt, gr, ltx, lrx, loth, fm, sens, d0_m):
    """Log-distance model anchored at d0 (usually 1 m)."""
    c = 3e8
    f_hz = f_mhz * 1e6
    pl_d0 = 20 * math.log10(4 * math.pi * d0_m * f_hz / c)
    C = pt + gt + gr - (ltx + lrx + loth) - fm - sens - pl_d0
    d_m = d0_m * 10 ** (C / (10 * n))
    lp = pl_d0 + 10 * n * math.log10(max(d_m / d0_m, 1e-12))
    return d_m / 1000.0, lp, C, d0_m, pl_d0


# --- Figure setup ---
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
ax.axis("off")


# --- Default parameters ---
params = {
    "Frequency (MHz)": 2400.0,
    "Path Loss Exponent (n)": 2.0,
    "Tx Power (dBm)": 20.0,
    "Tx Antenna Gain (dBi)": 2.0,
    "Rx Antenna Gain (dBi)": 2.0,
    "Tx Losses (dB)": 1.0,
    "Rx Losses (dB)": 1.0,
    "Other Losses (dB)": 0.0,
    "Fade Margin (dB)": 10.0,
    "Rx Sensitivity (dBm)": -90.0,
    "Reference Distance (m)": 1.0,
}


# --- Input boxes with perfectly aligned labels ---
boxes = {}
LABEL_X = 0.05
BOX_X   = 0.25
BOX_W   = 0.15
BOX_H   = 0.045
ROW_DY  = 0.065
START_Y = 0.9

for i, (label, default) in enumerate(params.items()):
    # Compute box placement (in figure coords)
    y_box = START_Y - i * ROW_DY
    axbox = plt.axes([BOX_X, y_box - 0.025, BOX_W, BOX_H])
    box = TextBox(axbox, "", initial=str(default))
    boxes[label] = box

    # Draw the label in *figure* coordinates, vertically centered on the box
    fig.text(
        LABEL_X,
        y_box - 0.025 + BOX_H / 2.0,
        label,
        ha="left",
        va="center",
        fontsize=10,
        transform=fig.transFigure
    )


# --- Updated layout positions for results, plot, and controls ---
output_ax = plt.axes([0.45, 0.55, 0.5, 0.38])   # Results text area (moved up)
output_ax.axis("off")
output_text = output_ax.text(0, 1, "", va="top", ha="left", fontsize=11, family="monospace")

plot_ax = plt.axes([0.47, 0.35, 0.5, 0.25])     # Plot area closer to results
plot_ax.set_xlabel("Path-loss exponent n")
plot_ax.set_ylabel("Distance (m)")
plot_ax.grid(True)

# Buttons underneath the plot
button_calc_ax = plt.axes([0.45, 0.20, 0.15, 0.06])
calc_button = Button(button_calc_ax, "Calculate", color="lightblue", hovercolor="skyblue")

radio_ax = plt.axes([0.65, 0.18, 0.25, 0.10])   # Radio buttons next to Calculate button
radio = RadioButtons(radio_ax, ["Classic (1 km)", "Log-distance (d₀)"], active=1)


# --- Helpers ---

def calculate_current():
    """Compute current selection."""
    vals = {k: float(box.text) for k, box in boxes.items()}
    if "Classic" in radio.value_selected:
        d_km, lp, C, d0_m, pl_d0 = compute_distance_classic(
            vals["Frequency (MHz)"],
            vals["Path Loss Exponent (n)"],
            vals["Tx Power (dBm)"],
            vals["Tx Antenna Gain (dBi)"],
            vals["Rx Antenna Gain (dBi)"],
            vals["Tx Losses (dB)"],
            vals["Rx Losses (dB)"],
            vals["Other Losses (dB)"],
            vals["Fade Margin (dB)"],
            vals["Rx Sensitivity (dBm)"],
        )
        model_str = "Classic model (reference 1 km)"
    else:
        d_km, lp, C, d0_m, pl_d0 = compute_distance_logdist(
            vals["Frequency (MHz)"],
            vals["Path Loss Exponent (n)"],
            vals["Tx Power (dBm)"],
            vals["Tx Antenna Gain (dBi)"],
            vals["Rx Antenna Gain (dBi)"],
            vals["Tx Losses (dB)"],
            vals["Rx Losses (dB)"],
            vals["Other Losses (dB)"],
            vals["Fade Margin (dB)"],
            vals["Rx Sensitivity (dBm)"],
            vals["Reference Distance (m)"],
        )
        model_str = f"Log-distance model (reference d₀ = {d0_m:.2f} m)"
    return vals, model_str, d_km, lp, C, d0_m, pl_d0


# --- Main event handler ---
def on_calculate(event):
    try:
        vals, model_str, d_km, lp, C, d0_m, pl_d0 = calculate_current()
        d_m = d_km * 1000
        d_mi = d_km * 0.621371
        d_ft = d_m * 3.28084

        # --- Update text results ---
        text = (
            f"=== Results ===\n"
            f"{model_str}\n"
            f"Reference path loss PL(d₀): {pl_d0:.2f} dB\n\n"
            f"Distance: {d_km:.3f} km\n"
            f"          {d_m:.1f} m\n"
            f"          {d_mi:.3f} miles\n"
            f"          {d_ft:.0f} ft\n\n"
            f"Path Loss: {lp:.2f} dB\n"
            f"C constant: {C:.2f} dB\n"
        )
        output_text.set_text(text)

        # --- Automatically update the plot ---
        n_values = [x / 10 for x in range(20, 61)]  # 2.0 → 6.0
        d_meters = []
        for n in n_values:
            if "Classic" in radio.value_selected:
                d_km2, _, _, _, _ = compute_distance_classic(
                    vals["Frequency (MHz)"], n,
                    vals["Tx Power (dBm)"], vals["Tx Antenna Gain (dBi)"],
                    vals["Rx Antenna Gain (dBi)"], vals["Tx Losses (dB)"],
                    vals["Rx Losses (dB)"], vals["Other Losses (dB)"],
                    vals["Fade Margin (dB)"], vals["Rx Sensitivity (dBm)"])
            else:
                d_km2, _, _, _, _ = compute_distance_logdist(
                    vals["Frequency (MHz)"], n,
                    vals["Tx Power (dBm)"], vals["Tx Antenna Gain (dBi)"],
                    vals["Rx Antenna Gain (dBi)"], vals["Tx Losses (dB)"],
                    vals["Rx Losses (dB)"], vals["Other Losses (dB)"],
                    vals["Fade Margin (dB)"], vals["Rx Sensitivity (dBm)"],
                    vals["Reference Distance (m)"])
            d_meters.append(d_km2 * 1000)

        plot_ax.clear()
        plot_ax.plot(n_values, d_meters, marker="o", color="blue", label="Distance vs n")
        plot_ax.axvline(vals["Path Loss Exponent (n)"], color="red", linestyle="--", label="Current n")
        plot_ax.set_xlabel("Path-loss exponent n")
        plot_ax.set_ylabel("Distance (m)")
        plot_ax.grid(True)
        plot_ax.legend()
        plot_ax.set_title(f"Distance vs n ({radio.value_selected})")

        fig.canvas.draw_idle()
    except Exception as e:
        output_text.set_text(f"Error: {e}")
        fig.canvas.draw_idle()


calc_button.on_clicked(on_calculate)

plt.show()
