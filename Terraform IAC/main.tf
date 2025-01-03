provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  subscription_id = var.subscription_id
  tenant_id = var.tenant_id
  client_id = var.client_id
  client_secret = var.client_secret
}

# Resource Group
resource "azurerm_resource_group" "cosmos_database_resource_group" {
  name     = var.database_resource_group
  location = var.region
}

resource "azurerm_resource_group" "function_app_resource_group" {
  name     = var.function_app_resource_group
  location = var.region
}

resource "azurerm_resource_group" "communication_service_resource_group" {
  name     = var.communication_service_resource_group
  location = var.region
}

# Database Cosmos DB Account
resource "azurerm_cosmosdb_account" "toll_database_account" {
  name                = var.cosmosdb_account_name
  location            = azurerm_resource_group.cosmos_database_resource_group.location
  resource_group_name = azurerm_resource_group.cosmos_database_resource_group.name
  offer_type          = "Standard"

  capabilities {
    name = "EnableServerless"
  }

  consistency_policy {
      consistency_level = "Session"
  }

  geo_location {
    location          = "Central India"
    failover_priority = 0
  }
}

# Database
resource "azurerm_cosmosdb_sql_database" "toll_violation_database_system" {
  name                = var.cosmosdb_database_name
  resource_group_name = azurerm_cosmosdb_account.toll_database_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.toll_database_account.name
}

# Database SQL Containers
resource "azurerm_cosmosdb_sql_container" "challan_container_table" {
  name                  = var.cosmosdb_container_name[0]
  resource_group_name = azurerm_cosmosdb_account.toll_database_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.toll_database_account.name
  database_name         = azurerm_cosmosdb_sql_database.toll_violation_database_system.name
  partition_key_paths   = ["/vehicleId"]

}

resource "azurerm_cosmosdb_sql_container" "user_container_table" {
  name                  = var.cosmosdb_container_name[1]
  resource_group_name = azurerm_cosmosdb_account.toll_database_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.toll_database_account.name
  database_name         = azurerm_cosmosdb_sql_database.toll_violation_database_system.name
  partition_key_paths   = ["/email"]
  unique_key{
    paths=["/email"]
  }
}

resource "azurerm_cosmosdb_sql_container" "vehicle_container_table" {
  name                  = var.cosmosdb_container_name[2]
  resource_group_name = azurerm_cosmosdb_account.toll_database_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.toll_database_account.name
  database_name         = azurerm_cosmosdb_sql_database.toll_violation_database_system.name
  partition_key_paths   = ["/email"]
}

resource "azurerm_cosmosdb_sql_container" "fastag_container_table" {
  name                  = var.cosmosdb_container_name[3]
  resource_group_name = azurerm_cosmosdb_account.toll_database_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.toll_database_account.name
  database_name         = azurerm_cosmosdb_sql_database.toll_violation_database_system.name
  partition_key_paths   = ["/vehicleId"]
  unique_key {
    paths = ["/vehicleId"]
  }
}

resource "azurerm_cosmosdb_sql_container" "transaction_container_table" {
  name                  = var.cosmosdb_container_name[4]
  resource_group_name = azurerm_cosmosdb_account.toll_database_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.toll_database_account.name
  database_name         = azurerm_cosmosdb_sql_database.toll_violation_database_system.name
  partition_key_paths   = ["/tagId"]
}


# Communication Service
resource "azurerm_communication_service" "communication_service_for_alerts" {
  name                = var.communication_service_name
  resource_group_name = azurerm_resource_group.communication_service_resource_group.name
  data_location       = var.data_location_for_communication_service
}

resource "azurerm_email_communication_service" "toll_email_communication_service" {
  name                = "Toll-Email-Communication-Service"
  resource_group_name = azurerm_resource_group.communication_service_resource_group.name
  data_location       = var.data_location_for_communication_service
}

resource "azurerm_email_communication_service_domain" "toll_email_communication_service_domain" {
  name             = var.email_communication_service_domain_name
  email_service_id = azurerm_email_communication_service.toll_email_communication_service.id
  domain_management = "AzureManaged"
}

# Function App and Azure functions + a storage account for logs
resource "azurerm_storage_account" "function_app_storage_account" {
  name                     = var.function_app_log_storage_name
  resource_group_name      = azurerm_resource_group.function_app_resource_group.name
  location                 = azurerm_resource_group.function_app_resource_group.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  public_network_access_enabled = true
  allow_nested_items_to_be_public = true
}

resource "azurerm_service_plan" "function_app_service_plan" {
  name                = var.function_app_service_plan
  resource_group_name = azurerm_resource_group.function_app_resource_group.name
  location            = azurerm_resource_group.function_app_resource_group.location
  os_type             = "Linux"
  sku_name            = "Y1"
}

resource "azurerm_application_insights" "function_app_application_insights" {
  name                = var.function_app_application_insights_name
  location            = azurerm_resource_group.function_app_resource_group.location
  resource_group_name = azurerm_resource_group.function_app_resource_group.name
  application_type    = "web"
}

resource "azurerm_linux_function_app" "function_app_toll_violation_system"{
  name                = var.function_app_container
  resource_group_name = azurerm_resource_group.function_app_resource_group.name
  location            = azurerm_resource_group.function_app_resource_group.location

  storage_account_name       = azurerm_storage_account.function_app_storage_account.name
  storage_account_access_key = azurerm_storage_account.function_app_storage_account.primary_access_key

  service_plan_id            = azurerm_service_plan.function_app_service_plan.id

  app_settings = {
    "COSMOS_DB_ENDPOINT": "${azurerm_cosmosdb_account.toll_database_account.endpoint}",
    "COSMOS_DB_KEY": "${azurerm_cosmosdb_account.toll_database_account.primary_key}",
    "CONNECTION_STRING": "${azurerm_communication_service.communication_service_for_alerts.primary_connection_string}",
    "SENDER_DOMAIN": "${azurerm_email_communication_service_domain.toll_email_communication_service_domain.from_sender_domain}",
    "SENDER_DOMAIN_MAIL": "${azurerm_email_communication_service_domain.toll_email_communication_service_domain.mail_from_sender_domain}",
    "PRIVATE_KEY": var.PRIVATE_KEY
    "WEBSITE_RUN_FROM_PACKAGE" = var.blob_url
  }

  site_config {
    cors {
      allowed_origins = [ "*" ]
      support_credentials = false
    }
    application_stack {
      python_version = "3.12"
    }
    application_insights_connection_string = "${azurerm_application_insights.function_app_application_insights.connection_string}"
    application_insights_key = "${azurerm_application_insights.function_app_application_insights.instrumentation_key}"
  }

}

# outputs
output "function_app_name"{
  value = azurerm_linux_function_app.function_app_toll_violation_system.name
}
