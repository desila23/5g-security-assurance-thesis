REQUIRE resstar_verification_failure.authentication_vector.rand == resstar_verification_failure.authentication_request.rand
REQUIRE resstar_verification_failure.authentication_vector.autn == resstar_verification_failure.authentication_request.autn
REQUIRE resstar_verification_failure.authentication_reject.present == true

IF resstar_verification_failure.identity_path == direct_suci {
    REQUIRE resstar_verification_failure.registration_request.identity_type == SUCI
}

IF resstar_verification_failure.identity_path == guti_then_suci {
    REQUIRE resstar_verification_failure.registration_request.identity_type == 5G_GUTI
    REQUIRE resstar_verification_failure.identity_request.requested_identity == SUCI
    REQUIRE resstar_verification_failure.identity_response.identity_type == SUCI
}

IF resstar_verification_failure.failure_source == local {
    REQUIRE resstar_verification_failure.res_star_verification.hres_star != resstar_verification_failure.res_star_verification.hxres_star
}

IF resstar_verification_failure.failure_source == ausf {
    REQUIRE resstar_verification_failure.res_star_verification.hres_star == resstar_verification_failure.res_star_verification.hxres_star
    REQUIRE resstar_verification_failure.authentication_response.res_star == resstar_verification_failure.ausf_confirmation_request.res_star
    REQUIRE resstar_verification_failure.ausf_confirmation_response.auth_result == AUTHENTICATION_FAILURE
}