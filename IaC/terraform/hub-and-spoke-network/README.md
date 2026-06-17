# Lab Scenario: Azure Hub-and-Spoke Network Topology

## 1. Architectural Overview
This infrastructure deployment establishes a secure, enterprise-grade **Hub-and-Spoke network topology** within a single Azure Resource Group. The design centralizes external ingress, security auditing, and management operations into a core network while completely isolating application workloads within a dedicated, peered network.

```
                  [ Public Internet ]
                           │
                           ▼ (SSH via Public IP)
┌──────────────────────────────────────────────────────────────┐
│ HUB VNET (10.0.0.0/16)                                       │
│                                                              │
│  ┌──────────────────────┐        ┌──────────────────────┐    │
│  │ GatewaySubnet        │        │ snet-management      │    │
│  │ (10.0.1.0/24)        │        │ (10.0.2.0/24)        │    │
│  │ [Reserved for VPN]   │        │ [vm-management]      │────┼┐
│  └──────────────────────┘        └──────────────────────┘    ││
└──────────────────────────────────────────────────────────────┘│
                               │                                │
                               ▼ (Bi-directional Peering)       │
┌──────────────────────────────────────────────────────────────┐│
│ SPOKE VNET (10.1.0.0/16)                                     ││
│                                                              ││
│  ┌──────────────────────┐        ┌──────────────────────┐    ││
│  │ snet-frontend        │        │ snet-backend         │    ││
│  │ (10.1.1.0/24)        │        │ (10.1.2.0/24)        │    ││
│  │ [Web/App Tier]       │───────>│ [vm-backend]         │<───┼┘
│  └──────────────────────┘        └──────────────────────┘    │(Blocked by NSG)
└──────────────────────────────────────────────────────────────┘
```

### Network Component Specifications
* **The Hub (`vnet-hub` | `10.0.0.0/16`):** Functions as the single, audited "front door" to the cloud environment.
  * `GatewaySubnet` (`10.0.1.0/24`): Explicitly provisioned and reserved for future hybrid connectivity (e.g., ExpressRoute or Site-to-Site VPN).
  * `snet-management` (`10.0.2.0/24`): Houses administrative components and secure jump boxes.
* **The Spoke (`vnet-spoke-app` | `10.1.0.0/16`):** Contains the isolated production application workloads divided into distinct architectural tiers.
  * `snet-frontend` (`10.1.1.0/24`): Dedicated to web and presentation tier services.
  * `snet-backend` (`10.1.2.0/24`): Dedicated to data tier, databases, or private microservices.
* **Connectivity:** Bi-directional **Virtual Network Peering** links `vnet-hub` and `vnet-spoke-app`, permitting low-latency, private IP communication across network boundaries without passing through the public internet.

---

## 2. Security & Traffic Control Isolation
Security is enforced at the network layer using micro-segmentation principles:
* **Zero Public Exposure:** No resources inside the Spoke network (`vnet-spoke-app`) are allocated Public IP addresses.
* **Micro-Segmentation:** A Network Security Group (NSG) is bound directly to `snet-backend`. It implements a strict rule engine that **only permits inbound traffic originating from the `snet-frontend` subnet prefix (`10.1.1.0/24`)**, actively dropping all other direct communication attempts (including management traffic coming from the Hub).

---

## 3. Deployment Validation Plan
To safely and cost-effectively verify the routing, peering, and firewall boundaries, the configuration includes two minimalist Linux Virtual Machines:

1. **`vm-management` (The Jump Box):** Deployed inside the Hub's `snet-management` subnet. Configured with a **Public IP** to allow an encrypted SSH connection from your local workstation.
2. **`vm-backend` (The Target Workload):** Deployed inside the Spoke's `snet-backend` subnet. Configured with **only a Private IP** to simulate a locked-down production server.

### Execution Steps
* **Test 1 (Peering Verification):** Establish an SSH session from your laptop to the Public IP of `vm-management`. From that terminal, attempt to SSH into the Private IP of `vm-backend` (`10.1.2.X`). *Expected Outcome: Success (Confirms that VNet peering routes traffic across networks).*
* **Test 2 (NSG Enforcement Verification):** From the `vm-management` terminal, attempt to execute a non-SSH request (such as a ping, curl, or custom port probe) directly to `vm-backend`. *Expected Outcome: Connection Timeout / Dropped Packets (Confirms the backend NSG successfully shields the data tier from unauthorized tiers).*