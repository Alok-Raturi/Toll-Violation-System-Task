import os
from azure.cosmos import CosmosClient


COSMOS_DB_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT") 
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)