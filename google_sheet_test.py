import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from the JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name("gcloud_key.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the sheet using the sheet ID (replace with your actual ID)
sheet_id = "1AeSgOlCwnXP21J7NagaMYUINDv5MPaNBgHsxI1q-xls"
sheet = client.open_by_key(sheet_id).sheet1

# Insert test data into row 2
sheet.insert_row(["Test", "This is a sample tweet", "Positive", 0.85, "EV"], index=2)

# Read all rows
data = sheet.get_all_records()
print("Data from sheet:")
for row in data:
    print(row)