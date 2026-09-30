REQUIRE amf_sync_failure.synchronization_failure.cause == 21
REQUIRE amf_sync_failure.synchronization_failure.auts_present == true
REQUIRE amf_sync_failure.resynchronization_request.present == true
REQUIRE amf_sync_failure.resynchronization_request.auts == amf_sync_failure.synchronization_failure.auts
REQUIRE amf_sync_failure.resynchronization_request.rand == amf_sync_failure.initial_authentication_vector.rand


MFOTL CASE A """
ResynchronizationRequest()
IMPLIES
EVENTUALLY[0,{TIMER_MS}] AusfAuthenticationResponse()
"""

MFOTL CASE B """
SyncFailure()
IMPLIES
NOT EVENTUALLY[0,{TIMER_MS}] AuthenticationRequest()
"""