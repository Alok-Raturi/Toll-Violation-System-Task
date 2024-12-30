import os
from azure.cosmos import CosmosClient

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"

# COSMOS_DB_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT") 
# COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")


COSMOS_DB_ENDPOINT = "https://tolldbmsmadhur.documents.azure.com:443/" 
COSMOS_DB_KEY = "vAsPEHdnFZe6T2ce1QkzTd0elMos0IGKgQ91hisomwmhBCJVsCrVusd3gv2mCqmCZbW43HdRRADPACDbPhLmlw=="

client = CosmosClient(COSMOS_DB_ENDPOINT, COSMOS_DB_KEY)

database = client.get_database_client(DATABASE_NAME)

transaction_container = database.get_container_client(TRANSACTION_CONTAINER)
fastag_container = database.get_container_client(FASTAG_CONTAINER)
challan_container = database.get_container_client(CHALLAN_CONTAINER)
user_container = database.get_container_client(USER_CONTAINER)
vehicle_container = database.get_container_client(VEHICLE_CONTAINER)