REQUIRE suci_deconcealment.response.status_code == 200
REQUIRE suci_deconcealment.test_input.original_supi == suci_deconcealment.response.body.supi