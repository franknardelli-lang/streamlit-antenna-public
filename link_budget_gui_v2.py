import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button, RadioButtons
import math

def compute_distance_classic(f_mhz, n, pt, gt, gr, ltx, lrx, loth, fm, sens):
    """Classic model anchored at 1 km (32.44 constant)."""
    k = 32.44
    C = pt + gt + gr - (ltx + lrx + loth) - fm - sens - k - 20 * math.log10(f_mhz)
    d_km = 10 ** (C / (10 * n))
    lp = k + 20 * math.log10(f_mhz) + 10 * n * math.log10(d_km)
    return d_km, lp, C

def compute_distance_logdist(f_mhz, n, pt, gt, gr, ltx, lrx, loth, fm, sens, d0_m):
    """Log-distance model anchored at d0 (usually 1 m)."""
    c = 3e8
    f_hz = f_mhz * 1e6
    pl_d0 = 20 * math.log10(4 * math.pi * d0_m * f_hz / c)  # FSPL at d0
    C = pt + gt + gr - (ltx + lrx + loth) - fm - sens - pl_d0
    d_m = d0_m * 10 ** (C / (10 * n))
    lp = pl_d0 + 10 * n * math.log10(max(d_m / d0_m, 1e-12))
    return d_m / 1000.0, lp, C  # return in km for consistency

# --- GUI setup ---
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
ax.axis("off")

# --- Parameters ---
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

boxes = {}
start_y = 0.9
dy = 0.065

for i, (label, default) in enumerate(params.items()):
    y = start_y - i * dy
    ax.text(0.05, y, label, va="center", ha="left", fontsize=10)
    axbox = plt.axes([0.25, y - 0.025, 0.15, 0.045])
    box = TextBox(axbox, "", initial=str(default))
    boxes[label] = box

# --- Model selector ---
radio_ax = plt.axes([0.05, 0.05, 0.15, 0.12])
radio = RadioButtons(radio_ax, ["Classic (1 km)", "Log-distance (d₀)"], active=1)

# --- Output panel ---
output_ax = plt.axes([0.45, 0.15, 0.5, 0.75])
output_ax.axis("off")
output_text = output_ax.text(0, 1, "", va="top", ha="left", fontsize=11, family="monospace")

# --- Calculate button ---
button_ax = plt.axes([0.25, 0.05, 0.15, 0.06])
calc_button = Button(button_ax, "Calculate", color="lightblue", hovercolor="skyblue")

def on_calculate(event):
    try:
        vals = {k: float(box.text) for k, box in boxes.items()}
        if "Classic" in radio.value_selected:
            d_km, lp, C = compute_distance_classic(
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
            ref_str = "Reference distance = 1 km (FSPL constant 32.44)"
        else:
            d_km, lp, C = compute_distance_logdist(
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
            ref_str = f"Reference distance d₀ = {vals['Reference Distance (m)']} m"

        d_m = d_km * 1000
        d_mi = d_km * 0.621371
        d_ft = d_m * 3.28084

        text = (
            f"=== Results ===\n"
            f"Model: {radio.value_selected}\n"
            f"{ref_str}\n\n"
            f"Distance: {d_km:.3f} km\n"
            f"          {d_m:.1f} m\n"
            f"          {d_mi:.3f} miles\n"
            f"          {d_ft:.0f} ft\n\n"
            f"Path Loss: {lp:.2f} dB\n"
            f"C constant: {C:.2f} dB\n"
        )
        output_text.set_text(text)
        fig.canvas.draw_idle()
    except Exception as e:
        output_text.set_text(f"Error: {e}")
        fig.canvas.draw_idle()

calc_button.on_clicked(on_calculate)

plt.show()
