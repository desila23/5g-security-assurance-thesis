import hashlib
import subprocess

from utils.json_utils import extract_json_objects


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)

    return sha256.hexdigest()


def get_tshark_version():
    result = subprocess.run(
        ["tshark", "--version"],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.splitlines()[0].strip()



def run_tshark(
    pcap_file,
    display_filter=None,
    fields=None,
    decode_as=None,
    verbose=False
):
    command = [
        "tshark",
        "-r", str(pcap_file)
    ]

    if display_filter is not None:
        command.extend([
            "-Y",
            display_filter
        ])

    if decode_as is not None:
        command.extend([
            "-d",
            decode_as
        ])


    # Modalità verbose: equivalente a tshark -V
    if verbose:
        command.append("-V")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    if fields is None:
        raise ValueError(
            "fields must be provided when verbose=False"
        )


    command.extend([
        "-T", "fields",
        "-E", "separator=\t"
    ])

    for field in fields:
        command.extend([
            "-e",
            field
        ])

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    rows = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        values = line.split("\t")

        row = {}

        for index, field in enumerate(fields):
            if index < len(values):
                row[field] = values[index]
            else:
                row[field] = ""

        rows.append(row)

    return rows



def decode_tcp_payload(payload_hex):
    if not payload_hex:
        return ""

    clean_hex = payload_hex.replace(":", "").replace(" ", "")

    try:
        payload_bytes = bytes.fromhex(clean_hex)
    except ValueError:
        return ""

    return payload_bytes.decode("utf-8", errors="ignore")


def extract_tcp_json_messages(pcap_file, display_filter):
    fields = [
        "frame.number",
        "frame.time_relative",
        "frame.time_epoch",
        "ip.src",
        "ip.dst",
        "tcp.stream",
        "tcp.srcport",
        "tcp.dstport",
        "tcp.payload"
    ]

    rows = run_tshark(
        pcap_file,
        display_filter,
        fields
    )

    messages = []

    for row in rows:
        payload_text = decode_tcp_payload(row["tcp.payload"])
        json_objects = extract_json_objects(payload_text)

        for body in json_objects:
            messages.append({
                "frame": int(row["frame.number"]),
                "timestamp_relative": float(row["frame.time_relative"]),
                "timestamp_epoch": float(row["frame.time_epoch"]),
                "ip_src": row["ip.src"],
                "ip_dst": row["ip.dst"],
                "tcp_stream": int(row["tcp.stream"]) if row["tcp.stream"] else None,
                "tcp_srcport": int(row["tcp.srcport"]) if row["tcp.srcport"] else None,
                "tcp_dstport": int(row["tcp.dstport"]) if row["tcp.dstport"] else None,
                "body": body
            })

    return messages


def compact_tcp_json_message(message, data_key=None, field_map=None):
    if message is None:
        return {
            "present": False
        }

    body = message["body"]
    nested_data = body.get(data_key, {}) if data_key else {}

    result = {
        "present": True,
        "frame": message["frame"],
        "timestamp_relative": message["timestamp_relative"],
        "timestamp_epoch": message["timestamp_epoch"],
        "ip_src": message["ip_src"],
        "ip_dst": message["ip_dst"],
        "tcp_stream": message["tcp_stream"]
    }

    if field_map:
        for output_field, source in field_map.items():
            source_type = source["source"]
            source_field = source["field"]

            if source_type == "body":
                result[output_field] = body.get(source_field)

            elif source_type == "nested":
                result[output_field] = nested_data.get(source_field)

            else:
                raise RuntimeError(
                    f"Unsupported source type: {source_type}"
                )

    return result