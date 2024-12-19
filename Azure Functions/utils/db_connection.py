from azure.cosmos import CosmosClient


COSMOS_DB_ENDPOINT = "https://tolldbmsalokraturi.documents.azure.com:443/" 
COSMOS_DB_KEY = ""  

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)