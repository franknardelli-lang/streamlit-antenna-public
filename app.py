import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

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


# --- Streamlit UI ---

st.set_page_config(page_title="Wireless Link Budget Calculator", layout="wide")
st.title("📡 Wireless Link Budget Calculator")

# Sidebar input parameters
st.sidebar.header("Input Parameters")

f_mhz = st.sidebar.number_input("Frequency (MHz)", value=2400.0, step=10.0)
n = st.sidebar.slider("Path Loss Exponent (n)", 2.0, 6.0, 2.0, 0.1)
pt = st.sidebar.number_input("Tx Power (dBm)", value=20.0)
gt = st.sidebar.number_input("Tx Antenna Gain (dBi)", value=2.0)
gr = st.sidebar.number_input("Rx Antenna Gain (dBi)", value=2.0)
ltx = st.sidebar.number_input("Tx Losses (dB)", value=1.0)
lrx = st.sidebar.number_input("Rx Losses (dB)", value=1.0)
loth = st.sidebar.number_input("Other Losses (dB)", value=0.0)
fm = st.sidebar.number_input("Fade Margin (dB)", value=10.0)
sens = st.sidebar.number_input("Rx Sensitivity (dBm)", value=-90.0)
d0_m = st.sidebar.number_input("Reference Distance (m)", value=1.0, step=0.1)

model_type = st.sidebar.radio("Model Type", ["Classic (1 km)", "Log-distance (d₀)"], index=1)

# --- Calculate results ---

if model_type.startswith("Classic"):
    d_km, lp, C, d0_out, pl_d0 = compute_distance_classic(
        f_mhz, n, pt, gt, gr, ltx, lrx, loth, fm, sens
    )
    model_str = "Classic model (reference 1 km)"
else:
    d_km, lp, C, d0_out, pl_d0 = compute_distance_logdist(
        f_mhz, n, pt, gt, gr, ltx, lrx, loth, fm, sens, d0_m
    )
    model_str = f"Log-distance model (reference d₀ = {d0_out:.2f} m)"

# Convert distances
d_m = d_km * 1000
d_mi = d_km * 0.621371
d_ft = d_m * 3.28084

# --- Display results ---

col1, col2 = st.columns([1, 1.5])
with col1:
    st.markdown("### Results")
    st.text(f"{model_str}")
    st.text(f"Reference path loss PL(d₀): {pl_d0:.2f} dB\n")
    st.text(f"Distance: {d_km:.3f} km")
    st.text(f"          {d_m:.1f} m")
    st.text(f"          {d_mi:.3f} miles")
    st.text(f"          {d_ft:.0f} ft\n")
    st.text(f"Path Loss: {lp:.2f} dB")
    st.text(f"C constant: {C:.2f} dB")

# --- Distance vs n Plot ---

n_values = np.arange(2.0, 6.1, 0.1)
d_meters = []

for n_val in n_values:
    if model_type.startswith("Classic"):
        d_km2, _, _, _, _ = compute_distance_classic(f_mhz, n_val, pt, gt, gr, ltx, lrx, loth, fm, sens)
    else:
        d_km2, _, _, _, _ = compute_distance_logdist(f_mhz, n_val, pt, gt, gr, ltx, lrx, loth, fm, sens, d0_m)
    d_meters.append(d_km2 * 1000)

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(n_values, d_meters, marker="o", color="blue", label="Distance vs n")
ax.axvline(n, color="red", linestyle="--", label="Current n")
ax.set_xlabel("Path-loss exponent n")
ax.set_ylabel("Distance (m)")
ax.grid(True)
ax.legend()
ax.set_title(f"Distance vs n ({model_type})")

with col2:
    st.pyplot(fig)
