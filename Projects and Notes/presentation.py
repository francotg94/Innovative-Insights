import plotly.express as px
import pandas as pd

data = {
    "Assay": ["Assay A", "Assay B", "Assay C", "Assay D"],
    "Count": [120, 85, 60, 40]
}

df = pd.DataFrame(data)

fig = px.bar(df, x="Assay", y="Count",
            title="Samples per Assay (Last 30 Days)",
            color="Count", text="Count")

fig.update_traces(textposition="outside")
fig.show()
