SEQUENCE {
    udm.generate_auth_data.request AS initial_request
    udm.generate_auth_data.response AS initial_response
    udm.generate_auth_data.request AS resync_request
    udm.generate_auth_data.response AS resync_response
}

REQUIRE initial_response.status == 200
REQUIRE resync_response.status == 200

REQUIRE initial_mac.match == true

REQUIRE initial_response.body.authenticationVector.rand == resync_request.body.resynchronizationInfo.rand

REQUIRE initial_response.body.authenticationVector.rand != resync_response.body.authenticationVector.rand
REQUIRE initial_response.body.authenticationVector.autn != resync_response.body.authenticationVector.autn
REQUIRE initial_response.body.authenticationVector.xresStar != resync_response.body.authenticationVector.xresStar
REQUIRE initial_response.body.authenticationVector.kausf != resync_response.body.authenticationVector.kausf