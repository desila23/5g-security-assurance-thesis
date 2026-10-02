SEQUENCE {
    udm.generate_auth_data.request AS request
    udm.generate_auth_data.response AS response
}

REQUIRE response.status == 200
REQUIRE response.body.supi == expected.supi