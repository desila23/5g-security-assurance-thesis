# 5G SCAS Test Suite – Robot Framework

This repository provides a **Robot Framework–based test suite** for executing **3GPP SCAS (Security Assurance Specifications) tests** against multiple **5G Core Network Functions**, currently:

- **NRF** (Network Repository Function)
- **UDM** (Unified Data Management)

The project is implemented in **Python** and uses Robot Framework to automate security tests, leveraging **JSON-based metadata** and reusable Python clients to interact with 5G Core Network APIs.


## Repository Structure

```text
.
├── data
│   ├── nrf
│   │   ├── nrf1.json
│   │   └── nrf2.json
│   ├── udm
│   │   └── client.json
│   └── ue
│       └── subscriber.json
├── nfs
│   ├── nrf
│   │   ├── __init__.py
│   │   └── NRFClient.py
│   └── udm
│       ├── __init__.py
│       └── UDMClient.py
├── scasutils
│   ├── crypto
│   │   ├── cryptomanager.py
│   │   ├── keys.py
│   │   ├── lte.py
│   │   ├── milenage.py
│   │   ├── octet_string.py
│   │   └── util.py
│   ├── errors.py
│   ├── log_utils.py
│   ├── nas.py
│   ├── ngap.py
│   └── singleton.py
├── tests
│   ├── nrf.robot
│   └── udm.robot
├── requirements.txt
└── README.md
```
## Components Overview

### Robot Test Suites

- `tests/nrf.robot`: SCAS test cases targeting the NRF.

- `tests/udm.robot`: SCAS test cases targeting the UDM.

### Metadata (`data/`)


- `data/nrf/*.json` Metadata and configuration for NRF-related tests.
    
    - NRF endpoints

    - Test parameters

    - Configuration and security-related inputs

- `data/udm/client.json` Client and configuration parameters used for UDM test scenarios.

- `data/ue/subscriber.json` Subscriber-related data used in UDM authentication and authorization tests.

### Network Function Clients (`nfs/`)

- `nfs/NRFClient.py`: Python client implementing interactions with the NRF.

- `nfs/UDMClient.py`: Python client implementing interactions with the UDM.

### SCAS Utilities (`scasutils/`)

Reusable utilities shared across test suites, including:

- Cryptographic primitives (e.g., Milenage, key derivation)

- NAS and NGAP helpers

- Logging and error handling

- Common SCAS-related abstractions


## Requirements
### System Requirements
- **Python 3.8 or newer**

- **pip**

- **Virtual environment support**

### Ubuntu-specific requirement

If you are using Ubuntu, install the required package for virtual environments:
```sh
sudo apt update
sudo apt install python3-venv
```
## Installation
### 1. Create a virtual environment
```
python3 -m venv .venv
```

### 2. Activate the virtual environment
```
source .venv/bin/activate
```

### 3. Install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Robot Framework Variables

Each Robot test suite exposes configurable variables that can be adapted to the target 5G Core deployment.
Default values are defined directly in the corresponding `*.robot` files.

### NRF test suite

```
*** Variables ***
${NRF_URL}      http://nrf-nnrf.default
${IS_HTTP2}     ${False}

${NF1_uuid}     18085249-5a9c-44c0-bdd5-bd0fa5e80ebe
${NF2_uuid}     fa28c816-5d3d-4e4b-b065-15d03f789d87

```

#### Variable Description
- `NRF_URL`: Base URL of the NRF nnrf interface

- `IS_HTTP2`: Boolean flag indicating whether the NRF interface uses HTTP/2.

- `NF1_uuid`, `NF2_uuid`: UUIDs of Network Functions used within the test scenarios.


### UDM test suite

```
*** Variables ***
${UDM_URL}  http://free5gc-free5gc-udm-service.default
${IS_HTTP2}  ${True}


${udm_config_path}  data/udm/client.json
${subscriber_config_path}  data/ue/subscriber.json

```

#### Variable Description
The UDM test suite exposes variables related to:

- The UDM service endpoint
- The UE / subscriber identity
- Client and authentication parameters used during UDM procedures

These variables are used together with metadata files located in:
- `data/udm/client.json`
- `data/ue/subscriber.json`

##### UDM Endpoint Configuration
- Variables defining the base URL and protocol used to reach the UDM service (e.g., nudm interfaces).

##### UE / Subscriber Identification
- Variables identifying the subscriber under test (e.g., SUPI / SUCI, subscription identifiers).

##### Client / Authentication Parameters
- Variables describing the client invoking UDM services.
- Used during authentication, authorization, and subscription-related SCAS test cases.

---
The exact variable names and default values are documented directly in
tests/udm.robot, which should be consulted when adapting the tests to a specific deployment.

### Overriding variables at runtime

Variables can be overridden directly from the command line when executing Robot Framework:
```
robot \
  --variable UDM_URL:http://<udm-address> \
  --variable IS_HTTP2:True \
  tests/udm.robot
```

This allows the same test suite to be reused across different 5G Core deployments without modifying the test files.

## UDM Prerequisites and Configuration Notes
Before executing the UDM SCAS tests, the following mandatory configuration steps must be completed:

### Subscriber Provisioning

The subscriber parameters used by the test suite must be provisioned in the Core Network database before running the tests.

In particular:

- The subscriber identity (e.g., SUPI / IMSI)

- Authentication parameters

- Subscription data

must match the values defined in: `data/ue/subscriber.json`

If the subscriber is not present or is inconsistently configured, the UDM tests will fail.

### Core Network Public Key Configuration
The Core Network public key used for subscriber identity protection must be configured in the UDM client metadata.

The user is required to add the Core Network public key inside: `data/udm/client.json`


This key is used during UDM-related procedures that involve:

- SUCI generation

- Subscriber identity protection mechanisms

- Cryptographic validation steps required by SCAS test cases

Ensure that the public key matches the one configured in the Core Network.

## Running the SCAS Tests

### Run NRF SCAS tests
```
robot tests/nrf.robot
```

### Run UDM SCAS tests
```
robot tests/udm.robot
```

### Run all test suites
```
robot tests/
```

### Optional: Specify an output directory

```
robot --outputdir results tests/nrf.robot
```

After execution, Robot Framework will generate:

- `report.html`

- `log.html`

- `output.xml`

These files provide detailed information about test execution, logs, and results.


