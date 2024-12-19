from azure.cosmos import CosmosClient


COSMOS_DB_ENDPOINT = "https://tolldbmsalokraturi.documents.azure.com:443/" 
COSMOS_DB_KEY = "alXy359h9FQ89VUqbn5dA98qLB9GX3fGz7dKwttGOm6i4GFblOYaNmDcdfEWmyLFaXeu6RtUiDESACDbcwoJfA=="  

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)