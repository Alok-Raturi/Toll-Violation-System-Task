import os
from azure.cosmos import CosmosClient


COSMOS_DB_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT") 
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")
# COSMOS_DB_ENDPOINT = "https://tollviolationdbmsraturi.documents.azure.com:443/"
# COSMOS_DB_KEY = "P7olAQdlT2QI6rz2Ny3IUbt3La9WRT2llypjBzyTqM8qmS82gjHWfJzKWd7reUvEIuT1GKYquOo8ACDbKF2GGg=="

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)