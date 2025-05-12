# AI-Powered Change Management Dashboard

This is a Streamlit web app designed to manage and visualize predictive maintenance and organizational change readiness using the ADKAR model in an automotive industry setting.

## Features

- 📊 Real-time KPIs and metrics
- 📉 Temperature & vibration trend charts (Plotly interactive)
- 🤖 Predictive Maintenance with Logistic Regression
- 📘 ADKAR readiness tracking with department filters
- 📤 CSV upload for dynamic survey updates
- 📆 Gantt chart for change milestones
- 🧠 Smart insight summary & auto-generated executive text
- ⬇️ Export ADKAR summary as CSV

## File Structure

```
dashboards/streamlit_app/app.py         # Main Streamlit application
data/raw/                               # Contains CSV input files
environment/requirements.txt            # Python dependencies
README.md                               # This file
```

## How to Run Locally

```bash
pip install -r environment/requirements.txt
streamlit run dashboards/streamlit_app/app.py
```

## Deployment

Push to GitHub, then deploy directly to [Streamlit Cloud](https://streamlit.io/cloud) with this app path:
```
dashboards/streamlit_app/app.py
```

## Sample Data Required

- `machine_maintenance_logs.csv`
- `organizational_readiness_survey.csv`
- `change_milestones.csv`

Place these in `data/raw/` before starting the app.

---