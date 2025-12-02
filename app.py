import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="Patient Vital Signs Dashboard",
    layout="wide",
    page_icon="🏥"
)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned_patient_vitals.csv", parse_dates=["charttime"])
    return df

df = load_data()

# --- Sidebar ---
st.sidebar.title("⚙️ Controls")

hadm_ids = df["hadm_id"].unique()
selected_hadm = st.sidebar.selectbox("Select Admission (hadm_id)", hadm_ids)

patient_df = df[df["hadm_id"] == selected_hadm].sort_values("charttime")

# Filters (optional enhancements)
age_min, age_max = int(df["age"].min()), int(df["age"].max())
age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

df_filtered = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]

# --- HEADER ---
st.title("🏥 Patient Vital Signs Monitoring Dashboard")
st.markdown("A premium healthcare analytics dashboard with vital trends, correlations, and event analysis.")

# ============================================================
# 🔵 KPI CARDS (in a clean 3 or 4-column layout)
# ============================================================

st.markdown("### 📌 Key Vital Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Heart Rate (mean)", value=f"{patient_df['HR'].mean():.1f} bpm")

with col2:
    st.metric(label="SPO₂ (mean)", value=f"{patient_df['SPO2'].mean():.1f} %")

with col3:
    st.metric(label="RR (mean)", value=f"{patient_df['RR'].mean():.1f} breaths/min")

with col4:
    st.metric(label="SBP (mean)", value=f"{patient_df['SBP'].mean():.1f} mmHg")

st.markdown("---")

# ============================================================
# 🔵 TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Vital Trends", 
    "💛 HR vs SPO₂", 
    "🕒 HR Hourly Pattern",
    "🚨 Event Analysis",
    "📂 Raw Data"
])

# ============================================================
# 📈 TAB 1 — Multi-Vital Time Trends
# ============================================================

with tab1:
    st.subheader(f"📈 Time Series Trends for Admission {selected_hadm}")

    fig, ax = plt.subplots(figsize=(14,5))
    ax.plot(patient_df["charttime"], patient_df["HR"], label="HR", linewidth=2)
    ax.plot(patient_df["charttime"], patient_df["SPO2"], label="SPO2", linewidth=2)
    ax.plot(patient_df["charttime"], patient_df["RR"], label="RR", linewidth=2)
    ax.plot(patient_df["charttime"], patient_df["SBP"], label="SBP", linewidth=2)

    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)

# ============================================================
# 💛 TAB 2 — HR vs SPO2
# ============================================================

with tab2:
    st.subheader("💛 SPO₂ vs Heart Rate (Color-Graded)")

    fig2, ax2 = plt.subplots(figsize=(10,6))
    sns.scatterplot(
        data=df_filtered,
        x="SPO2",
        y="HR",
        hue="HR",
        palette="plasma",
        s=60,
        alpha=0.7,
        ax=ax2
    )
    ax2.set_title("SPO₂ vs Heart Rate")
    ax2.grid(alpha=0.3)
    st.pyplot(fig2)

# ============================================================
# 🕒 TAB 3 — Hourly HR Pattern
# ============================================================

with tab3:
    st.subheader("🕒 Average Heart Rate by Hour of Day")

    fig3, ax3 = plt.subplots(figsize=(10,5))
    sns.lineplot(data=df, x="hour", y="HR", estimator="mean", ci=None, ax=ax3)
    ax3.set_title("Heart Rate Circadian Pattern")
    ax3.set_xlabel("Hour")
    ax3.set_ylabel("HR (bpm)")
    ax3.grid(alpha=0.3)
    st.pyplot(fig3)

# ============================================================
# 🚨 TAB 4 — Event-Based HR Analysis
# ============================================================

with tab4:
    st.subheader("🚨 Heart Rate vs Hours to Clinical Event")

    event_df = df.dropna(subset=["eventtime"])

    fig4, ax4 = plt.subplots(figsize=(10,6))
    sns.scatterplot(
        data=event_df,
        x="hrs_to_firstevent",
        y="HR",
        alpha=0.5,
        s=60,
        color="red",
        ax=ax4
    )

    ax4.axvline(0, color='black', linestyle='--', linewidth=2, label='Event Time')
    ax4.set_xlabel("Hours to Event")
    ax4.set_ylabel("HR (bpm)")
    ax4.grid(alpha=0.3)
    ax4.legend()

    st.pyplot(fig4)

# ============================================================
# 📂 TAB 5 — Raw Data Table
# ============================================================

with tab5:
    st.subheader("📂 Raw Data for Selected Admission")
    st.dataframe(patient_df)
