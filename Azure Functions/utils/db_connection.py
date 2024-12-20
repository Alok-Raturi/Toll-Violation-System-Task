from azure.cosmos import CosmosClient


COSMOS_DB_ENDPOINT = "https://tolldbmsmadhur.documents.azure.com:443/" 
COSMOS_DB_KEY = "vAsPEHdnFZe6T2ce1QkzTd0elMos0IGKgQ91hisomwmhBCJVsCrVusd3gv2mCqmCZbW43HdRRADPACDbPhLmlw=="  

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)