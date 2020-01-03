#!/usr/bin/env python
# coding: utf-8

# In[1]:


# setting up the imports required for the notebook
import pandas as pd
import requests
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import io
import folium
from geopy.geocoders import Nominatim
get_ipython().run_line_magic('matplotlib', 'inline')

#setting up the page which needs to be scraped from wikipedia using wikipedia library as wp
my_url = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
page_soup = soup(page_html,"html.parser")

print(page_soup)


# In[2]:


# Using pandas dataframe to get all the tables on webpage
dfs = pd.read_html('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M')

# finding out number of tables in the dfs and glimpse of what it stores
for df in dfs :
    print(df.head(5))


# In[3]:


# From above results we find that the first dataframe is the table we need
df = dfs[0]
df.head(10)

# Now we need to filter out the rows which have not assigned in Borough and Neighbourhood
df = df[df.Borough != 'Not assigned']
df.head(10)


# In[4]:


# Now we have the rows which were not helpful deleted from the table
#Now we would group them by Boroughs and join the neighbourhoods by , 
df = df.groupby(['Postcode','Borough'])['Neighborhood'].apply(', '.join).reset_index()
df.columns = ['Postcode','Borough','Neighbourhood']
df.head(5)


# In[5]:


df.shape


# In[6]:


# getting the geospatial data for the Boroughs 
geo_url = "http://cocl.us/Geospatial_data"
s = requests.get(geo_url).content
geo_data = pd.read_csv(io.StringIO(s.decode('utf-8')))

# Checking the dataframe made for columns names and data
geo_data.head(5)

# Changing column name of postal code to postcode for merge with original df
geo_data.columns = ['Postcode','Latitude','Longitude']

geo_data.head(5)
df = pd.merge(geo_data,df , on ='Postcode')
df.head(5)


# In[7]:


# Reordering the columns in datafrmae
df = df[['Postcode','Borough','Neighbourhood','Latitude','Longitude']]
df.head(5)


# In[8]:


# Finding out unique boroughs and number of neighbourhoods in dataframe
print('The dataframe has {} boroughs and {} neighbourhoods.'.format(
        len(df['Borough'].unique()),
        df.shape[0]))


# In[9]:


# Finding Toronto coordinates
address = 'Toronto'
geolocator = Nominatim(user_agent = "Toronto_explorer")
location = geolocator.geocode(address)
latitude_toronto = location.latitude
longitude_toronto = location.longitude

# Print the coordiantes of the Toronto city
print('The geographical coordinates of Toronto city are Latitude:{} and Longitude:{}'.
     format(latitude_toronto,longitude_toronto))


# In[10]:


# creating map of Toronto using latitude and longitude in dataframe
#latitude_toronto = 43.651070
#longitude_toronto = -79.347015
map_toronto = folium.Map(Location =[latitude_toronto,longitude_toronto], zoom_start=10)

# adding markers to map made above 
for lat, lon, borough, neighbourhood  in zip(df['Latitude'],df['Longitude'],df['Borough'],df['Neighbourhood']):
    label = '{},{}'.format(neighbourhood,borough)
    label = folium.Popup(label,parse_html= True)
    folium.CircleMarker(
        [lat,lon],
        radius = 5,
        popup = label,
        color = 'red',
        fill = True,
        fill_color = 'lightred',
        fill_opacity = 0.6,
        parse_html= False).add_to(map_toronto)
    
    
map_toronto

