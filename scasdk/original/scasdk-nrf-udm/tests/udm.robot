*** Settings ***
Documentation    SCAS tests for UDM
...
...               
Library          nfs.udm.UDMClient

Suite Setup  Run Keywords  Set Udm  ${UDM_URL}  ${IS_HTTP2}
             ...      AND  Config Udm Client  udm_config_path=${udm_config_path}
             ...      AND  Config Subscriber Data  subscriber_config_path=${subscriber_config_path}


*** Variables ***
${UDM_URL}  http://localhost:8000
${IS_HTTP2}  ${False}


${udm_config_path}  data/udm/client.json
${subscriber_config_path}  data/ue/subscriber.json


*** Test Cases ***
TC SYNCH FAIL HANDLING
    
    ${auth_vect1}=  Get Auth Vector  

    ${sqn}=  Get Sqn  auth_vect=${auth_vect1}

    ${usim_sqn}=  Set Variable  ${sqn + 1}

    ${resync_info}=  Gen Resynchronization Info  usim_sqn=${usim_sqn}  auth_vect=${auth_vect1}

    ${auth_vect2}=  Get Auth Vector  resync_info=${resync_info}

    Auth Vectors Shoud Not Be Equal  auth_vect1=${auth_vect1}  auth_vect2=${auth_vect2}


TC SYNCHRONIZE FAILURE HANDLING
    ${deconceal_available}=  Is Deconceal Available
    
    Skip If  condition= not ${deconceal_available}  msg=UDM does not support de-concealment

    ${supi}=  Get Supi

    ${suci}=  Conceal Supi  supi=${supi}

    ${received_supi}  Deconceal Suci  suci=${suci}

    Should Be Equal  first=${supi}  second=${received_supi}



    
    
    