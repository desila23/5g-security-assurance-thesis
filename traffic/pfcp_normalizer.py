from typing import Any

from traffic.models import MessageEvent

from utils.tshark_utils import parse_tshark_timestamp


PFCP_SESSION_ESTABLISHMENT_REQUEST = 50
PFCP_SESSION_ESTABLISHMENT_RESPONSE = 51


def _first(value: Any):
    if isinstance(value, list):
        return value[0] if value else None

    return value


def _to_list(value: Any) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _deduplicate_f_teids(teids: list, ipv4_addresses: list) -> list[dict]:
    if len(teids) != len(ipv4_addresses):
        raise RuntimeError(
            "Mismatch between PFCP F-TEIDs and IPv4 addresses: "
            f"{len(teids)} TEIDs, "
            f"{len(ipv4_addresses)} IPv4 addresses"
        )

    result = []
    seen = set()

    for teid, ipv4 in zip(teids, ipv4_addresses):
        key = str(teid), str(ipv4)
        
        if key in seen:
            continue

        seen.add(key)

        result.append({
            "teid": str(teid),
            "ipv4": str(ipv4)
        })

    return result


def _semantic_message_type(message_type: int) -> str:
    if message_type == PFCP_SESSION_ESTABLISHMENT_REQUEST:
        return "pfcp.session_establishment_request"

    if message_type == PFCP_SESSION_ESTABLISHMENT_RESPONSE:
        return "pfcp.session_establishment_response"

    return f"pfcp.message.{message_type}"


def normalize_pfcp_events(packets: list[dict]) -> list[MessageEvent]:
    events = []

    for packet in packets:
        layers = packet.get("layers", {})

        frame = layers.get("frame", {})
        ip = layers.get("ip", {})
        pfcp = layers.get("pfcp", {})

        message_type_raw = _first(pfcp.get("pfcp_pfcp_msg_type"))

        if message_type_raw is None:
            continue

        message_type_number = int(message_type_raw)

        teids = _to_list(
            pfcp.get("pfcp_pfcp_f_teid_teid")
        )

        ipv4_addresses = _to_list(
            pfcp.get("pfcp_pfcp_f_teid_ipv4_addr")
        )

        f_teids = []

        if teids or ipv4_addresses:
            f_teids = _deduplicate_f_teids(
                teids,
                ipv4_addresses
            )

        fields = {
            "message_type": message_type_number
        }

        if f_teids:
            fields["f_teids"] = f_teids

        cause = _first(pfcp.get("pfcp_pfcp_cause"))

        if cause is not None:
            fields["cause"] = int(cause)

        seid = _first(pfcp.get("pfcp_pfcp_seid"))

        if seid is not None:
            fields["seid"] = seid

        seqno = _first(pfcp.get("pfcp_pfcp_seqno"))

        if seqno is not None:
            fields["seqno"] = int(seqno)

        event = MessageEvent(
            frame_number=int(frame["frame_frame_number"]),
            timestamp=parse_tshark_timestamp(frame["frame_frame_time_epoch"]),
            protocol="pfcp",
            kind="message",
            src=_first(ip.get("ip_ip_src")),
            dst=_first(ip.get("ip_ip_dst")),
            message_type=_semantic_message_type(message_type_number),
            correlation={
                "seid": seid,
                "seqno": int(seqno)
                if seqno is not None
                else None
            },
            fields=fields
        )

        events.append(event)

    events.sort(
        key=lambda event: (
            event.timestamp,
            event.frame_number
        )
    )

    return events