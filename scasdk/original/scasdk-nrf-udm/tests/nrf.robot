*** Settings ***
Documentation    SCAS tests for NRF
...
...               
Library          ../nfs/nrf/NRFClient.py

Suite Setup  Set Nrf    ${NRF_URL}    ${IS_HTTP2}

*** Variables ***
${NRF_URL}  http://localhost:8001
${IS_HTTP2}  ${False}

${NF1_uuid}    18085249-5a9c-44c0-bdd5-bd0fa5e80ebe
${NF2_uuid}    fa28c816-5d3d-4e4b-b065-15d03f789d87

${NF1_data}    data/nrf/nrf1.json
${NF2_data}    data/nrf/nrf2.json

${FORBIDDEN}   ${403}
${CREATED}     ${201}

*** Test Cases ***
TC DISC AUTH SLICE
    ${nf1_result}=  Register Nf  nf_uuid=${NF1_uuid}  body_json=${NF1_data}
    Should Be Equal  ${nf1_result}  ${CREATED}
    ${nf2_result}=  Register Nf  nf_uuid=${NF2_uuid}  body_json=${NF2_data}
    Should Be Equal  ${nf2_result}  ${CREATED}
    ${result_code}=  Discover Nf  requester_uuid=${NF1_uuid}  requester_json=${NF1_data}   target_uuid=${NF2_uuid}   target_json=${NF2_data}
    Should Be Equal  ${result_code}  ${FORBIDDEN}
    [Teardown]  Run Keywords  Deregister Nf  nf_uuid=${NF1_uuid}  body_json=${NF1_data}
    ...         AND           Deregister Nf  nf_uuid=${NF2_uuid}  body_json=${NF2_data} 

