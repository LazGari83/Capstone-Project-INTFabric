# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# Welcome to your new notebook
# Type here in the cell editor to add code!


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## PRJ003 🔶 INT Project (Sprint 3): Getting data into Fabric 
# # 
# # > The code in this notebook is written as part of Week 3 of the Intermediate Project, in [Fabric Dojo](https://skool.com/fabricdojo/about). The intention is first to get the functionality working, in a way that's understandable for the community. Then, in future weeks, we will layer in things like testing, error-handling, more defensive coding patterns to make our extraction more robust.
# # 
# #  Data extraction strategy
# # In this notebook we will: 
# # - Step 0: Solution Step Up - importing packages, helper functions, defining metadata 
# # 
# # - Step 1: get AKV secret from Azure Key Vault (secure storage of Google Developers project key for querying YouTube Data V3 API)
# # - Step 2: get overall channel information for a YouTube channel, and write it to a Lakehouse Files area (our RAW layer)
# # - Step 3: get all videos on a channel (and write to RAW layer) 
# # - Step 4: get statistics for all videos on a channel (and write to RAW layer) 
# # 
# # This notebook is dynamic: it can be run in DEV, TEST and PROD, thanks to the use of Variable libraries. 
# # 
# # #### Step 0: Solution Set up
# # 
# # Import packages:


# CELL ********************

import notebookutils 
import requests 
from datetime import datetime
import os
import json

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # In this solution, we're using Variable Libraries for store different variable values that we need in different deployment workspaces (DEV, TEST, PROD). 
# # 
# # Let's get the ABFS path for the Lakehouse we are going to write our RAW data to... 
# # 
# # This will vary depending on the current deployment stage. 

# CELL ********************

variables = notebookutils.variableLibrary.getLibrary("vl-int-variables")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Define some helper functions (that we'll use across multiple steps): 

# CELL ********************

def get_data_from_endpoint(BASE_URL, base_params, additional_params = ""): 
    """Construct a GET request and return the JSON results"""
    
    params = base_params + additional_params

    full_URI = f'{BASE_URL}?key={api_key}&{params}'

    response = requests.get(full_URI) 

    json_data = response.json()

    return json_data

def get_data_with_pagination(BASE_URL, base_params, additional_params = ""):
    """Construct a GET request and return the JSON results, with Pagination"""
    all_items = []
    next_page_token = None
    params = base_params + additional_params

    while True:
        if next_page_token:
            additional_params_plus_token = additional_params + f'&pageToken={next_page_token}'
        else:
            additional_params_plus_token = additional_params

        json_data = get_data_from_endpoint(BASE_URL, base_params, additional_params_plus_token)

        json_data_items = json_data.get("items",{})

        all_items.extend(json_data_items)

        next_page_token = json_data.get('nextPageToken', None)

        if not next_page_token:
            break
    print("Total items: ",len(all_items))
    return all_items

def construct_abfs_write_path(write_location): 
    """Constructs an ABFS path to write RAW JSON files into a Lakehouse
    It uses variables (from the Variable Library), that the path is dynamic across deployment environments
    """
    
    # 'variables' is the values from the Variable Library 
    ws_name = variables.RAW_LH_WORKSPACE_NAME
    lh_name = variables.RAW_LH_NAME

    formatted_date = datetime.now().strftime("%Y%m%d")

    file_name = f"{formatted_date}-{id}.json" 

    abfs_path = f"abfss://{ws_name}@onelake.dfs.fabric.microsoft.com/{lh_name}.Lakehouse/Files/{write_location}{file_name}"
    
    return abfs_path

def write_json_to_location(json_data, location, id):  
    """Write JSON files to RAW Lakehouse area"""

    abfs_path = construct_abfs_write_path(location)

    json_string = json.dumps(json_data, indent=2)

    notebookutils.fs.put(abfs_path, json_string, overwrite=True)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Defining some metadata for scalability
# # For now, we will just use a Python object to store the metadata, but in later weeks, we will store this metadata (& add to it!)

# CELL ********************

METADATA = {
    "yt-channels": {
        "base_url": "https://www.googleapis.com/youtube/v3/channels", 
        "base_params": "part=snippet,statistics,contentDetails&id=UCrvoIYkzS-RvCEb0x7wfmwQ",  
        "write_location": "youtube_data_v3/channels/"
    },
    "yt-playlistItems":{
        "base_url": "https://www.googleapis.com/youtube/v3/playlistItems", 
        "base_params": "part=snippet&maxResults=50", 
        "write_location": "youtube_data_v3/playlistItems/"        
    },
    "yt-videos": {
        "base_url": "https://www.googleapis.com/youtube/v3/videos", 
        "base_params": "part=statistics&maxresults=50", 
        "write_location": "youtube_data_v3/videos/"
    }

}

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Step 1: Get secret from Azure Key Vault

# CELL ********************

def get_secret_from_akv()-> str:
    """Get API key from Azure Key Vault"""

    akv_name= 'https://cs-int-restapi-keys.vault.azure.net/'
    secret_name= 'data-v3-api-key'

    api_key = notebookutils.credentials.getSecret(akv_name,secret_name)

    return api_key

api_key = get_secret_from_akv()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Step 2: Get Channel Statistics

# CELL ********************

id = 'yt-channels'

md = METADATA.get(id)

channel_json_data = get_data_from_endpoint(md["base_url"], md["base_params"])

write_json_to_location(channel_json_data, md["write_location"], id)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
