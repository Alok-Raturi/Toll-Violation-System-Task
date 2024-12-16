from azure.cosmos import CosmosClient


COSMOS_DB_ENDPOINT = "https://tollviolationdetectionsystemdbaccount.documents.azure.com:443/" 
COSMOS_DB_KEY = ""  

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)






