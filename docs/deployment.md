# Deployment & SCADA Integration Guide
## Enterprise On-Premise / Edge Architecture

### 1. Edge Hardware Prerequisites
- **Server:** Industrial Edge IPC (Intel Xeon 8-Core or AMD EPYC, 32GB RAM, 512GB NVMe SSD).
- **Operating System:** Linux (Ubuntu 22.04 LTS / RHEL 9) or Windows Server 2022.
- **Runtime:** Python 3.10+ with Uvicorn ASGI Server and FastAPI.

### 2. OT / SCADA Integration Protocols
- **OPC-UA / Modbus TCP:** Connects to surface SRP VFD controllers to read motor current, SPM, and polished rod load cell telemetry.
- **Historian Ingestion (OSIsoft PI / Aspen InfoPlus.21):** Syncs 1-minute averaged flowline temperatures, casing pressures, and steam injection records.
- **RESTful Gateway:** Exposes THERMOLIFT X endpoints to OIL central control room supervisory consoles.

### 3. Security & Air-Gap Compliance
- Read-only SCADA gateway to prevent unauthorized remote writes to surface variable speed drives.
- Role-based access control (RBAC) ensuring only certified production engineers can approve simulated dispatches.
