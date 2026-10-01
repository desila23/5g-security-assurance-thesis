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


        # --------------------------------------------------
        # NRF
        # --------------------------------------------------

        if event.kind == "request":
            path = event.fields.get("path") or ""

            if path.startswith("/nnrf-disc/"):
                event.message_type = "nrf.discovery.request"
                by_correlation[key] = "nrf.discovery"

        elif event.kind == "response":
            base_type = by_correlation.get(key)

            if base_type == "nrf.discovery":
                event.message_type = "nrf.discovery.response"

    return events