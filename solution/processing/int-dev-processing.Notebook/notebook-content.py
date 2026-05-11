# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1a5c8fd8-1de4-463a-896a-ccb21938415e",
# META       "default_lakehouse_name": "int_dev_datastores",
# META       "default_lakehouse_workspace_id": "9bf29555-8d19-4361-90b4-35ce4fb3e1e6",
# META       "known_lakehouses": [
# META         {
# META           "id": "1a5c8fd8-1de4-463a-896a-ccb21938415e"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # #### PRJ003 🔶 INT Project (Sprint 3): Getting data into Fabric 
# # 
# # > The code in this notebook is written as part of Week 3 of the Intermediate Project, in [Fabric Dojo](https://skool.com/fabricdojo/about). The intention is first to get the functionality working, in a way that's understandable for the community. Then, in future weeks, we will layer in things like testing, error-handling, more defensive coding patterns to make our extraction more robust.
# # 
# # #### Data extraction strategy
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
