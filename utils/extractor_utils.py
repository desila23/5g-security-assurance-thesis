from utils.verifier_utils import load_test_config, parse_arguments

def load_extractor_context(base_dir, description):
    args = parse_arguments(description)

    test_config = load_test_config(
        base_dir,
        args.test,
        args.case
    )

    pcap_file = base_dir / test_config["pcap"]

    output_file = base_dir / test_config["evidence"]

    return {
        "test_id": args.test,
        "case_id": args.case,
        "config": test_config,
        "pcap_file": pcap_file,
        "output_file": output_file        
    }