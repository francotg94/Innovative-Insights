import requests  # For making HTTP requests
import pandas as pd  # For data manipulation and analysis
from sqlalchemy import create_engine  # For saving the DataFrame to PostgreSQL
from dotenv import load_dotenv #utilizing .env file to import PostgreSQL credentials
import os

# Load environment variables from the .env file
load_dotenv()

# Access variables
DB_URL = os.getenv("DB_URL")
BASE_URL = os.getenv("BASE_URL")
DATE_RANGE = os.getenv("DATE_RANGE")
LIMIT = int(os.getenv("LIMIT"))
STATINS = ["atorvastatin", "rosuvastatin", "simvastatin", "pravastatin", "lovastatin"]

def get_adverse_events(drug_name, skip=0):
    # sourcery skip: remove-unnecessary-else
    """
    Fetch adverse events for a specific drug from the FDA API.
    """
    url = f"{BASE_URL}?search=patient.drug.medicinalproduct:{drug_name}+AND+receivedate:{DATE_RANGE}&limit={LIMIT}&skip={skip}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def fetch_all_events(statins):
    """
    Fetch adverse event data for all drugs in the statins list.
    """
    all_data = []

    for statin in statins:
        print(f"Fetching data for {statin}...")
        skip = 0
        while True:
            data = get_adverse_events(statin, skip)
            if not data or 'results' not in data:
                break
            for event in data['results']:
                adverse_event = {
                    'Drug': statin.capitalize(),
                    'Reaction': event['patient']['reaction'][0]['reactionmeddrapt'] if 'reaction' in event['patient'] else None,
                    'Outcome': event['patient']['reaction'][0].get('reactionoutcome', None) if 'reaction' in event['patient'] else None,
                    'Date': event.get('receivedate', None),
                    'Age': event['patient'].get('patientonsetage', None),
                    'Age Unit': event['patient'].get('patientonsetageunit', None),
                    'Gender': event['patient'].get('patientsex', None),
                }
                all_data.append(adverse_event)
            skip += LIMIT

    return pd.DataFrame(all_data)

def save_to_postgresql(df, db_url, table_name):
    """
    Save the DataFrame to a PostgreSQL database table.
    """
    try:
        # Create a SQLAlchemy engine
        engine = create_engine(db_url)

        # Write the DataFrame to the PostgreSQL table
        df.to_sql(table_name, engine, index=False, if_exists='replace')  # Use 'append' to add to the table
        print(f"Data successfully saved to table '{table_name}' in the database.")
    except Exception as e:
        print(f"Failed to save data to database: {e}")

if __name__ == "__main__":
    # Fetch adverse events for all statins
    df = fetch_all_events(STATINS)
    print(f"Fetched {len(df)} adverse events.")

    # Save the data to PostgreSQL
    if not df.empty:
        save_to_postgresql(df, DB_URL, "adverse_events")
    else:
        print("No data to save.")