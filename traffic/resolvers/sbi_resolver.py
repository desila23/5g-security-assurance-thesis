from traffic.models import MessageEvent


def resolve_sbi_message_types(events: list[MessageEvent]) -> list[MessageEvent]:
    """
    Assegna un message_type semantico agli eventi HTTP/2 appartenenti alle API SBI 5G.

    Per ora supporta:
        - NRF Discovery
        - AUSF Authentication / Resynchronization
    """

    by_correlation = {}

    for event in events:
        if event.protocol != "http2":
            continue

        key = (
            event.correlation.get("tcp_stream"),
            event.correlation.get("http2_stream_id")
        )

        body = event.fields.get("body")


        # --------------------------------------------------
        # SBI request classification
        # --------------------------------------------------

        if event.kind == "request":
            path = event.fields.get("path") or ""

            # NRF
            if path.startswith("/nnrf-disc/"):
                event.message_type = "nrf.discovery.request"
                by_correlation[key] = "nrf.discovery"
                continue

            # UDM
            if (
                path.startswith("/nudm-ueau/")
                and path.endswith("/security-information/generate-auth-data")
            ):
                event.message_type = "udm.generate_auth_data.request"
                by_correlation[key] = "udm.generate_auth_data"
                continue

        # --------------------------------------------------
        # SBI response classification
        # --------------------------------------------------
    
        if event.kind == "response":
            base_type = by_correlation.get(key)
    
            # NRF
            if base_type == "nrf.discovery":
                event.message_type = "nrf.discovery.response"
        
            # UDM
            elif base_type == "udm.generate_auth_data":
                event.message_type = "udm.generate_auth_data.response"

        # ------------------------------
        # AUSF
        # ------------------------------

        if isinstance(body, dict):
            # resynchronization request:
            # {
            #   "supiOrSuci": "...",
            #   "servingNetworkName": "...",
            #   "resynchronizationInfo": {
            #       "rand": "...",
            #       "auts": "..."
            #   }
            # }

            resync_info = body.get("resynchronizationInfo")

            if isinstance(resync_info, dict):
                event.message_type = "ausf.resynchronization.request"
                event.fields["rand"] = resync_info.get("rand")
                event.fields["auts"] = resync_info.get("auts")
                continue


            # AUSF confirmation request
            res_star = body.get("resStar")

            if res_star is not None:
                event.message_type = "ausf.confirmation.request"
                event.fields["res_star"] = res_star
                continue


            # AUSF confirmation response
            auth_result = body.get("authResult")

            if auth_result is not None:
                event.message_type = "ausf.confirmation.response"
                event.fields["auth_result"] = auth_result
                continue


            # AUSF authentication vector:
            # {
            #   "authType": "5G_AKA",
            #   "5gAuthData": {
            #       "rand": "...",
            #       ...
            #   }
            # }

            auth_data = body.get("5gAuthData")

            if (
                body.get("authType") == "5G_AKA"
                and isinstance(auth_data, dict)
            ):
                event.message_type = "ausf.authentication.response"

                event.fields["rand"] = auth_data.get("rand")

                continue


    return events