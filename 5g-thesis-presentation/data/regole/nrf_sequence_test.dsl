SEQUENCE {
    nrf.discovery.request AS request
    nrf.discovery.response AS response
}

REQUIRE response.status == 403
