REQUIRE initial_auth.response.status_code == 200
REQUIRE resynchronization.response.status_code == 200

REQUIRE initial_auth.response.body.authenticationVector.rand == resynchronization.request.body.resynchronizationInfo.rand

REQUIRE initial_auth.response.body.authenticationVector.rand != resynchronization.response.body.authenticationVector.rand
REQUIRE initial_auth.response.body.authenticationVector.autn != resynchronization.response.body.authenticationVector.autn
REQUIRE initial_auth.response.body.authenticationVector.xresStar != resynchronization.response.body.authenticationVector.xresStar
REQUIRE initial_auth.response.body.authenticationVector.kausf != resynchronization.response.body.authenticationVector.kausf

REQUIRE initial_auth.response.mac_verification.match == true
REQUIRE resynchronization.response.mac_verification.match == true