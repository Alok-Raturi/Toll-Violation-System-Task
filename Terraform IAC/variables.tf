variable "subscription_id" {
  description = "The subscription ID in which the resources will be created."
  default = "414bc6d2-a97f-40e9-a40f-63e7d46d0e7a"
  type = string
}

variable "region" {
  description = "The region in which the resources will be created."
  default     = "West Europe"
  type = string
}

variable "resource_group_name" {
  description = "The name of the resource group in which the resources will be created."
  default     = "Toll-Violation-Detection-System"
  type = string
}

# DB Variables
variable "cosmosdb_account_name" {
  description = "The name of the Cosmos DB account."
  default     = "tolldatabasesystem"
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
    default     = "backendlogsstorage"
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
    default = "backendfunctionapplication"
    type = string
}

variable "python_version" {
    description = "The python version for the function app."
    default = "3.12"
    type = string  
}


