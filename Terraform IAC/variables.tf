variable "subscription_id" {
  description = "The subscription ID in which the resources will be created."
  default = "8a228cff-023f-42af-818d-51a84a828d46"
  type = string
}

variable "tenant_id" {
  description = "The Tenant ID for the target Azure Account"
#  default = "46118836-cde0-431b-bb1e-b6ab7887003c"
  type = string
}
variable "client_id" {
  description = "Client ID for the Application"
#  default= "20c516e5-a70b-4ebc-bbed-4f2dd86c3141"
  type = string
}
variable "client_secret" {
  description = "Client Secret"
#  default="bH18Q~9cOEq7OH1m3jxXHSOwg_PjSYn38IM9Saik"
  type = string
}

variable "region" {
  description = "The region in which the resources will be created."
  default     = "East US"
  type = string
}


variable "database_resource_group" {
  description = "The name of the resource group in which the resources will be created."
  default     = "Toll-Violation-Detection-System-Alok-Raturi"
  type = string
}

variable "function_app_resource_group" {
  description = "The name of the resource group in which the resources will be created."
  default     = "Function-App-RG-Alok-Raturi"
  type = string
}

variable "communication_service_resource_group" {
  description = "The name of the resource group in which the resources will be created."
  default     = "Communication-Service-RG-Alok-Raturi"
  type = string
}


# DB Variables
variable "cosmosdb_account_name" {
  description = "The name of the Cosmos DB account."
  default     = "tollviolationdbmsraturi"
  type = string
}

variable "cosmosdb_database_name" {
  description = "The name of the Cosmos DB database."
  default     = "Toll-Violation-Detection-System-DB"
  type = string
}

variable "cosmosdb_container_name" {
  description = "The name of the Cosmos DB container."
  default     = ["Challan-Table", "User-Table", "Vehicle-Table","Fastag-Table","Transaction-Table"]
  type =list(string)
}

# Communication Service Variable
variable "communication_service_name" {
  description = "The name of the communication service."
  default     = "Communication-Service-For-Toll"
  type = string
}

variable "email_communication_service_name" {
  description = "The name of the email communication service."
  default     = "Toll-Communication-Service"
  type = string
}

variable "email_communication_service_domain_name" {
  description = "The name of the email communication service domain."
  default     = "AzureManagedDomain"
  type = string
}

variable "data_location_for_communication_service" {
  description = "The data location for the communication service."
  default     = "United States"
  type = string
}


# Function App Variables
variable "function_app_log_storage_name"{
    description = "The name of the storage account for function app logs."
    default     = "raturi012953storage"
    type = string
}

variable "function_app_service_plan"{
    description = "The name of the function app service plan."
    default = "Function-App-Service-Plan"
    type = string
}

variable "function_app_application_insights_name"{
    description = "The name of the function app application insights."
    default = "Function-App-Application-Insights"
    type = string
}

variable "function_app_container"{
    description = "The name of the function app container."
    default = "raturifunctionapp"
    type = string
}

variable "python_version" {
    description = "The python version for the function app."
    default = "3.12"
    type = string  
}

# PUBLIC and Private key
variable "PRIVATE_KEY" {
  type = string
}

# Blob URL for the function code
variable "blob_url" {
description = "Blob link for Function Deployment"
type = string
}