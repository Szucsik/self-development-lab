resource "azurerm_resource_group" "vnet-hub-rg" {
  name     = "vnet-hub-rg-tst"
  location = "West Europe"
}

resource "azurerm_network_security_group" "vnet-hub-nsg" {
  name                = "vnet-hub-nsg-tst"
  location            = azurerm_resource_group.vnet-hub-rg.location
  resource_group_name = azurerm_resource_group.vnet-hub-rg.name
}

resource "azurerm_virtual_network" "vnet-hub" {
  name                = "vnet-hub-tst"
  location            = azurerm_resource_group.vnet-hub-rg.location
  resource_group_name = azurerm_resource_group.vnet-hub-rg.name
  address_space       = ["10.0.0.0/16"]
  dns_servers         = ["10.0.0.4", "10.0.0.5"]

  subnet {
    name             = "gateway"
    address_prefixes = ["10.0.1.0/24"]
  }

  subnet {
    name             = "snet-management"
    address_prefixes = ["10.0.2.0/24"]
    security_group   = azurerm_network_security_group.vnet-hub-nsg.id
  }

  tags = {
    environment = "TST"
  }
}

resource "azurerm_resource_group" "vnet-spoke-rg" {
  name     = "vnet-spoke-rg-tst"
  location = "West Europe"
}

resource "azurerm_network_security_group" "vnet-spoke-nsg" {
  name                = "vnet-nsg-tst"
  location            = azurerm_resource_group.vnet-spoke-rg.location
  resource_group_name = azurerm_resource_group.vnet-spoke-rg.name
}

resource "azurerm_virtual_network" "vnet-spoke" {
  name                = "vnet-spoke-tst"
  location            = azurerm_resource_group.vnet-spoke-rg.location
  resource_group_name = azurerm_resource_group.vnet-spoke-rg.name
  address_space       = ["10.1.0.0/16"]
  dns_servers         = ["10.1.0.4", "10.1.0.5"]

  subnet {
    name             = "frontend"
    address_prefixes = ["10.1.1.0/24"]
  }

  subnet {
    name             = "backend"
    address_prefixes = ["10.1.2.0/24"]
    security_group   = azurerm_network_security_group.vnet-spoke-nsg.id
  }

  tags = {
    environment = "TST"
  }
}