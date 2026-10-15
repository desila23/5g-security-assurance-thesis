SEQUENCE {
    ausf.authentication.response AS initial_vector
    nas.authentication_request AS initial_auth
    nas.authentication_failure AS sync_failure
    ausf.resynchronization.request AS resync
    ausf.authentication.response AS new_vector
    nas.authentication_request AS subsequent_auth_request
}

REQUIRE initial_auth.rand == initial_vector.rand
REQUIRE sync_failure.cause == 21
REQUIRE resync.auts == sync_failure.auts
REQUIRE resync.rand == initial_auth.rand
