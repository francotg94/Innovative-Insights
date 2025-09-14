import pandas as pd 
import matplotlib.pyplot as plt 

# Simulate some tidy lab data
data = {'Assay Type': ['Lipid Panel', 'Metabolic', 'CBC', 'Thyroid'],
        'Tests Performed': [150, 210, 180, 95]}
df = pd.DataFrame(data)

# Create a bar plot from the DataFrame
plt.bar(df['Assay Type'], df['Tests Performed'], color='skyblue')

# Add labels and a title for clarity
plt.xlabel('Assay Type')
plt.ylabel('Number of Tests')
plt.title('Lab Tests Performed This Week')

# Display the plot
plt.show()