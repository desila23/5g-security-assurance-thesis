SEQUENCE {
    nas.registration_request AS registration_request

    OPTIONAL {
        nas.identity_request AS identity_request
        nas.identity_response AS identity_response
    }

    ausf.authentication.response AS authentication_vector
    nas.authentication_request AS authentication_request
    nas.authentication_response AS authentication_response

    OPTIONAL {
        ausf.confirmation.request AS ausf_confirmation_request
        ausf.confirmation.response AS ausf_confirmation_response
    }

    nas.authentication_reject AS authentication_reject
}


REQUIRE authentication_vector.rand == authentication_request.rand
REQUIRE authentication_vector.autn == authentication_request.autn
REQUIRE authentication_reject.present == true


IF case.identity_path == direct_suci {
    REQUIRE registration_request.identity_type == SUCI
}


IF case.identity_path == guti_then_suci {
    REQUIRE registration_request.identity_type == 5G_GUTI
    REQUIRE identity_request.requested_identity == SUCI
    REQUIRE identity_response.identity_type == SUCI
}


IF case.failure_source == local {
    REQUIRE hres_star.value != authentication_vector.hxres_star
}


IF case.failure_source == ausf {
    REQUIRE hres_star.value == authentication_vector.hxres_star
    REQUIRE authentication_response.res_star == ausf_confirmation_request.res_star
    REQUIRE ausf_confirmation_response.auth_result == AUTHENTICATION_FAILURE
}
