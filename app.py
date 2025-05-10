
import streamlit as st
import numpy as np

st.set_page_config(page_title="MRO Duration & CBA Dashboard", layout="centered")
st.title("🛩️ MRO Duration Predictor & CBA Tool")

# ------------------------------------------------------------
# SECTION 1: MRO DURATION PREDICTION (Based on Regression Model)
# ------------------------------------------------------------
st.header("📈 Predict MRO Duration")

with st.form("prediction_form"):
    st.subheader("✈️ Aircraft & MRO Inputs")
    aircraft_type = st.selectbox("Aircraft Type", ["777", "787", "A350"])
    mro_region = st.selectbox("MRO Region", ["Middle East", "East Asia", "SE Asia", "USA"])
    age = st.number_input("Aircraft Age (Years)", min_value=0.0, max_value=40.0, value=12.0)
    age_squared = age ** 2
    cumulative_fc = st.number_input("Cumulative Flight Cycles", min_value=5000, max_value=60000, value=20000)
    avg_annual_cycles = st.number_input("Average Annual Flight Cycles", min_value=100, max_value=2000, value=1200)
    avg_annual_hours = st.number_input("Average Annual Flight Hours", min_value=1000, max_value=7000, value=4200)
    avg_daily_utilisation = st.number_input("Average Daily Utilisation (hrs)", min_value=1.0, max_value=24.0, value=12.5)

    submitted = st.form_submit_button("Predict MRO Duration")

if submitted:
    age_x_util = age * avg_daily_utilisation
    age_x_787 = age if aircraft_type == "787" else 0
    age_x_A350 = age if aircraft_type == "A350" else 0
    fc_x_me = cumulative_fc if mro_region == "Middle East" else 0
    util_x_787 = avg_daily_utilisation if aircraft_type == "787" else 0

    region_me = 1 if mro_region == "Middle East" else 0
    region_se = 1 if mro_region == "SE Asia" else 0
    region_usa = 1 if mro_region == "USA" else 0

    type_787 = 1 if aircraft_type == "787" else 0
    type_a350 = 1 if aircraft_type == "A350" else 0

    pred_duration = (
        18.54 + (-1.67)*age + 0.069*age_squared + 0.0007*cumulative_fc +
        -0.0078*avg_annual_cycles + 0.0014*avg_annual_hours + 0.731*avg_daily_utilisation +
        0.9049*type_787 + 0.0468*type_a350 + (-9.05)*region_me +
        -0.19*region_se + (-6.57)*region_usa + (-0.0376)*age_x_util +
        0.5442*age_x_787 + 0.2048*age_x_A350 + (-0.0006)*fc_x_me + (-0.6286)*util_x_787
    )

    st.success(f"✅ **Predicted MRO Duration: {pred_duration:.1f} days**")
    predicted_duration_days = round(pred_duration)

# ------------------------------------------------------------
# SECTION 2: COST-BENEFIT ANALYSIS DASHBOARD
# ------------------------------------------------------------
st.header("💰 Maintenance Cost-Benefit Analysis")

if 'predicted_duration_days' not in locals():
    predicted_duration_days = st.number_input("Enter Predicted Downtime (Days)", min_value=1, max_value=60, value=17)

col1, col2 = st.columns(2)
with col1:
    labor_hours = st.number_input("Total Labor Hours (C-Check)", value=5000)
    lost_rev_per_hr = st.number_input("Lost Revenue per Hour (USD)", value=21000)
    lease_rate_daily = st.number_input("Daily Lease Rate (USD)", value=85000)
with col2:
    half_life_value = st.number_input("Aircraft Half-Life Value (USD)", value=28970000)
    dep_rate = st.slider("Annual Depreciation Rate (%)", 2, 10, 5)
    labor_rate_map = {"Middle East": 75, "East Asia": 95, "SE Asia": 85, "USA": 120}
    labor_rate = labor_rate_map.get(mro_region, 100)

labor_cost = labor_hours * labor_rate
material_cost = 0.3 * labor_cost
maintenance_cost = labor_cost + material_cost

downtime_hours = predicted_duration_days * 24
opportunity_cost = downtime_hours * lost_rev_per_hr
lease_loss = predicted_duration_days * lease_rate_daily

annual_dep = half_life_value * (dep_rate / 100)
daily_dep = annual_dep / 365
residual_loss = predicted_duration_days * daily_dep

total_cost = maintenance_cost + opportunity_cost + lease_loss + residual_loss

st.subheader("📊 Summary")
st.markdown(f"**Maintenance Cost:** ${maintenance_cost:,.0f}")
st.markdown(f"**Opportunity Cost (Lost Revenue):** ${opportunity_cost:,.0f}")
st.markdown(f"**Lease Loss (Idle Asset):** ${lease_loss:,.0f}")
st.markdown(f"**Residual Value Loss:** ${residual_loss:,.0f}")
st.success(f"💥 **Total Estimated Cost: ${total_cost:,.0f}**")
