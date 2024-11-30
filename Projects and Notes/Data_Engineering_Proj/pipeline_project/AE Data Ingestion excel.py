import requests # Import the requests library to make HTTP requests
import pandas as pd # Import the pandas library for the data manipulation and analysis
from sqlalchemy import create_engine #Import in order to Write the DataFrame to a PostgreSQL table

def get_adverse_events(drug_name, skip=0) :  # sourcery skip: assign-if-exp
    #Define the URL for the FDA API request
    url = f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:{drug_name}+AND+receivedate:[20220101+TO+20220105]&limit=100&skip={skip}"
    response = requests.get(url)    # Make a GET request to the FDA API
    if response.status_code == 200:     #Check if the request was successful (status code 200)
        return response.json()      #Return the response data as a JSON object
    else:
        return None     # Return None if the requests was not successful

# sourcery skip: hoist-statement-from-loop
statins = ["atorvastatin", "rosuvastatin", "simvastatin", "pravastatin", "lovastatin"]
#List of statin drugs to search for adverse events

all_data = []       #Initialize an empty list to store all adverse event data

for statin in statins:  #Loop through each statin in the list
    skip = 0        #Initialize the skip parameter to 0 for pagination
    while True:     #Infinite loop to keep fetching data until no more results
        data = get_adverse_events(statin, skip)     #Get adverse events data for the current statin
        if not data or 'results' not in data:       #Check if there is no data or no results
            break       #Exit the loop if no more data
        for event in data['results']:       #Loop through each event in the results
            adverse_event = {
                'Drug': statin.capitalize(),        #Capitalize drug name
                'Reaction': event['patient']['reaction'][0]['reactionmeddrapt'] if 'reaction' in event ['patient'] else None,
                #Get the reaction type if available
                'Outcome': event['patient']['reaction'][0].get('reactionoutcome', None),
                #Get the reaction outcome if available
                'Date': event['receivedate'],       #include the receive date
                'Age': event['patient'].get ('patientonsetage', None),
                #Get the patients age if available
                'Age Unit': event['patient'].get ('patientonsetageunit', None),
                #Get the age unit (e.g., years, months) if available
                'Gender': event['patient'].get('patientsex', None),     #Get the patients gender if available
            }
            all_data.append(adverse_event)      #Add the adverse event data to the list
        skip += 100 #Increment the skp parameter to get the next set of results (we already got these, so it's skipping what we got and is going to the next batch)
df = pd.DataFrame(all_data) #Create a DataFrame from the list of adverse event data

#Save the DataFrame to an Excel file
df.to_excel('adverse_events_statins.xlsx', index=False)