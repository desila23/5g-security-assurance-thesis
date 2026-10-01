import subprocess

from pathlib import Path


# TEMPO
def seconds_to_milliseconds(timestamp):
    return round(timestamp * 1000)



# FORMULA MFOTL
def build_monpoly_formula(formula_template, timer_duration_ms):
    return formula_template.replace(
        "{TIMER_MS}", 
        str(timer_duration_ms)
    )


def write_monpoly_formula(formula_template, formula_output_file, timer_duration_ms):
        formula = build_monpoly_formula(formula_template, timer_duration_ms)

        formula_output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(formula_output_file, "w", encoding="utf-8") as f:
            f.write(formula + "\n")



# MONPOLY LOG
def add_log_event(events, timestamp, event_name):
    if timestamp is None:
        return

    events.append({
        "timestamp": seconds_to_milliseconds(timestamp),
        "event": event_name
    })



def generate_temporal_log_from_match(match, event_mapping):
    log_events = []

    for alias, event_name in event_mapping.items():
        event = match.bindings.get(alias)

        if event is None:
            continue

        add_log_event(
            log_events,
            event.timestamp,
            event_name
        )

    log_events.sort(
        key=lambda item: item["timestamp"]
    )

    lines = [
        f"@{item['timestamp']} {item['event']}"
        for item in log_events
    ]

    return "\n".join(lines) + "\n"



def write_monpoly_log(log_content, log_file):
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_content)



# ESECUZIONE DI MONPOLY
def run_monpoly(signature_file, formula_file, log_file):
    command = [
        "monpoly",
        "-sig", str(signature_file),
        "-formula", str(formula_file),
        "-log", str(log_file),
        "-negate"        
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.strip()


# VERIFICATION
def build_temporal_verification(monpoly_output):
    violation_found = bool(monpoly_output)

    return {
        "engine": "Monpoly",
        "verification_mode": "negated_policy",
        "violation_found": violation_found,
        "monpoly_output": monpoly_output,
        "overall_verdict": "FAIL" if violation_found else "PASS"        
    }


