import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ---------------------🔐 Optional Password Gate ---------------------
st.set_page_config(page_title="AI Change Mgmt Dashboard", layout="wide")

st.sidebar.title("📊 Navigation")
require_auth = st.sidebar.checkbox("🔐 Enable login protection", value=False)

if require_auth:
    default_password = "demo"
    password = st.sidebar.text_input("Enter password", type="password")
    if password != default_password:
        st.warning("🔐 Protected mode is enabled. Enter the correct password to proceed.")
        st.stop()

page = st.sidebar.radio("Go to:", [
    "Overview KPIs",
    "Maintenance Insights",
    "ADKAR Analysis",
    "Change Timeline",
    "Smart Summary"
])

# ---------------------📂 Load Data ---------------------
maintenance_df = pd.read_csv('data/machine_maintenance_logs.csv')
survey_df = pd.read_csv('data/organizational_readiness_survey.csv')
milestone_df = pd.read_csv('data/change_milestones.csv')


# ADKAR Columns
adkar_columns = ['awareness', 'desire', 'knowledge', 'ability', 'reinforcement']
for col in adkar_columns:
    survey_df[col] = pd.to_numeric(survey_df[col], errors='coerce')

# ---------------------📈 PAGE: KPIs ---------------------
if page == "Overview KPIs":
    st.title("🔧 Change Management Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Machine Failures", int(maintenance_df['failure'].sum()))
    col2.metric("Avg Run Hours", f"{maintenance_df['run_hours'].mean():.2f}")
    col3.metric("Avg Temperature (°C)", f"{maintenance_df['temperature_c'].mean():.1f}")

# ---------------------📉 PAGE: Maintenance Insights ---------------------
elif page == "Maintenance Insights":
    st.title("📉 Maintenance Monitoring & Failure Prediction")

    sample_machine = st.selectbox("Select Machine:", maintenance_df['machine_id'].unique())
    df_filtered = maintenance_df[maintenance_df['machine_id'] == sample_machine]
    df_filtered['date'] = pd.to_datetime(df_filtered['date'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['temperature_c'],
                             mode='lines+markers', name='Temperature (°C)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df_filtered['date'], y=df_filtered['vibration_level'],
                             mode='lines+markers', name='Vibration Level', line=dict(color='blue')))
    fig.update_layout(title='Temperature & Vibration Trends',
                      xaxis_title='Date', yaxis_title='Value', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    # Predictive Maintenance Model
    X = maintenance_df[['run_hours', 'temperature_c', 'vibration_level']]
    y = maintenance_df['failure']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    st.success(f"🔍 Model Accuracy: {accuracy * 100:.2f}%")

    machine_df = maintenance_df[maintenance_df['machine_id'] == sample_machine]
    avg_vals = machine_df[['run_hours', 'temperature_c', 'vibration_level']].mean().values.reshape(1, -1)
    failure_prob = model.predict_proba(avg_vals)[0][1]
    st.info(f"Failure Probability for {sample_machine}: **{failure_prob:.2%}**")

# ---------------------📘 PAGE: ADKAR Analysis ---------------------
elif page == "ADKAR Analysis":
    st.title("📘 ADKAR Change Readiness Analysis")

    uploaded_file = st.file_uploader("📤 Upload new ADKAR survey CSV", type=["csv"])
    if uploaded_file:
        survey_df = pd.read_csv(uploaded_file)
        for col in adkar_columns:
            survey_df[col] = pd.to_numeric(survey_df[col], errors='coerce')
        st.success("✅ Survey data uploaded successfully!")

    departments = survey_df['department'].unique()
    selected_depts = st.multiselect("Filter Departments:", departments, default=list(departments))
    filtered_df = survey_df[survey_df['department'].isin(selected_depts)]

    adkar_avg = filtered_df.groupby("department")[adkar_columns].mean().reset_index()
    adkar_melt = adkar_avg.melt(id_vars="department", var_name="Dimension", value_name="Score")

    fig = px.bar(adkar_melt, x="Dimension", y="Score", color="department", barmode="group",
                 title="Average ADKAR Scores by Department")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚠️ Departments Needing Attention (Score < 3.0)")
    adkar_avg_clean = adkar_avg.dropna(subset=adkar_columns)
    needs_help = adkar_avg_clean[(adkar_avg_clean[adkar_columns] < 3.0).any(axis=1)]
    if not needs_help.empty:
        st.dataframe(needs_help.style.highlight_min(subset=adkar_columns, axis=1), use_container_width=True)
    else:
        st.success("✅ All departments meet the minimum threshold.")

    st.download_button("⬇️ Download ADKAR Summary", adkar_avg.to_csv(index=False),
                       file_name="adkar_summary.csv", mime="text/csv")

# ---------------------📆 PAGE: Timeline ---------------------
elif page == "Change Timeline":
    st.title("📆 Change Initiative Timeline")
    try:
        milestone_df = pd.read_csv('../../data/raw/change_milestones.csv')
        milestone_df['start_date'] = pd.to_datetime(milestone_df['start_date'])
        milestone_df['end_date'] = pd.to_datetime(milestone_df['end_date'])
        fig = px.timeline(milestone_df, x_start="start_date", x_end="end_date",
                          y="milestone", color="status")
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("📂 Please place a valid change_milestones.csv in /data/raw/")

# ---------------------🧠 PAGE: Smart Summary ---------------------
elif page == "Smart Summary":
    st.title("🧠 AI-Generated Smart Insights")

    adkar_avg = survey_df.groupby("department")[adkar_columns].mean().reset_index()
    lowest_adkar = adkar_avg[adkar_columns].mean().idxmin()
    lowest_score = adkar_avg[lowest_adkar].mean()

    X = maintenance_df[['run_hours', 'temperature_c', 'vibration_level']]
    y = maintenance_df['failure']
    model = LogisticRegression().fit(X, y)
    risk_df = maintenance_df.groupby("machine_id")[X.columns].mean().reset_index()
    risk_df['risk'] = model.predict_proba(risk_df[X.columns])[:, 1]
    riskiest = risk_df.sort_values("risk", ascending=False).iloc[0]

    st.markdown(f"""
- 🔥 Highest failure risk: **{riskiest['machine_id']}** with probability **{riskiest['risk']:.2%}**
- ❗ Lowest ADKAR dimension: **{lowest_adkar.capitalize()}** (avg score: {lowest_score:.2f})
""")

    st.subheader("📄 Executive Summary")
    summary = f"""
Out of {survey_df['department'].nunique()} departments surveyed, the weakest readiness factor is "{lowest_adkar.capitalize()}" with an average score of {lowest_score:.2f}.

The machine most at risk of failure is "{riskiest['machine_id']}" with a predicted failure probability of {riskiest['risk']:.2%}.

Milestones for the change initiative can be tracked in the timeline view. Address ADKAR gaps and machine risks for smoother transformation.
"""
    st.text_area("Copy this:", summary, height=200)
