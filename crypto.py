import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time


# Title and intro
st.title('Cryptocurrency Gainers and Losers')
st.markdown('This app shows the top gainers and losers in cryptocurrency based on 24-hour volume.')

# Load and parse the HTML file
# The URL of the webpage you want to scrape
url = 'https://coinmarketcap.com/gainers-losers/'

# Fetch the HTML content
response = requests.get(url)
html_content = response.text

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Function to parse a table
def parse_table(table):
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue  # Skip header or empty row
        data.append([col.text.strip() for col in cols])
    return pd.DataFrame(data, columns=['Rank', 'Name', 'Symbol', 'Volume', 'Price', 'Change'])


table = soup.find('table', class_='cmc-table')  # Adjust class name or use other attributes to find the exact table

# Extract table headers
headers = [header.get_text().strip() for header in table.find_all('th')]

# Extract table rows
rows = []
for row in table.find('tbody').find_all('tr'):
    rows.append([val.text.strip() for val in row.find_all(['td', 'th'])])

# Create a DataFrame
df_gainers = pd.DataFrame(rows, columns=headers)

# Locate the "Top Losers" table
top_losers_heading = soup.find('h3', string='Top Losers')
top_losers_table = top_losers_heading.find_next('table')

# Parse the table
data = []
for row in top_losers_table.find_all('tr')[1:]:  # Skip the header row
    cols = row.find_all('td')
    rank = cols[0].text.strip()
    name = cols[1].text.strip()
    price_change = cols[3].text.strip()  # Assuming the price change is in the 4th column
    data.append({
        'Rank': rank,
        'Name': name,
        'Price Change': price_change
    })

# Convert to DataFrame for better display and manipulation
df_losers = pd.DataFrame(data)

# Sidebar filters for gainers and losers
st.sidebar.header('Filters')
top_gainers_filter = st.sidebar.selectbox('Top Gainers Filter', ['Top 5', 'Top 10'])
top_losers_filter = st.sidebar.selectbox('Top Losers Filter', ['Top 5', 'Top 10'])

# Filter data based on selection
top_gainers = df_gainers.head(5 if top_gainers_filter == 'Top 5' else 10)
top_losers = df_losers.head(5 if top_losers_filter == 'Top 5' else 10)

# Display the tables in Streamlit
st.header('Top Gainers')
st.dataframe(top_gainers)

st.header('Top Losers')
st.dataframe(top_losers)

# Refresh the app periodically
refresh_rate = 60 * 60 * 24  # Refresh every hour (in seconds)
while True:
    time.sleep(refresh_rate)  
    st.rerun()
