"""Reject incomplete or mislabeled measurements without fabricating missing values."""
import argparse
import csv
import json
from pathlib import Path
from statistics import median

FIELDS = {
    "environment": ["evidence_level", "cluster", "genesis_hash", "runtime_version", "toolchain_manifest"],
    "experiment": ["mode", "parameter_set", "asset", "mint", "leaf_count", "scenario", "fixture_id", "command"],
    "outcome": ["expected", "observed", "test_passed", "error_code", "failure_stage", "verifier_reached"],
    "transport": ["version", "transaction_index", "transaction_count_for_operation", "transaction_bytes", "instruction_data_bytes", "signature_or_witness_bytes", "merkle_proof_bytes", "transaction_signature", "confirmation_status"],
    "resources": ["compute_limit", "compute_consumed", "sha256_syscall_count", "allocated_account_bytes", "logical_authority_bytes", "storage_deposit_lamports", "storage_refund_lamports", "actual_transaction_fee_lamports"],
}
LEVELS = {"host_reference", "local_svm", "local_validator", "devnet_simulation", "devnet_confirmed"}


def validate(record, root=None):
    errors = []
    for key in ["schema_version", "run_id", "operation_id", "observed_at_utc", "commit", "program_binary_sha256", "evidence_paths", *FIELDS]:
        if key not in record:
            errors.append(f"missing {key}")
    if errors:
        return errors
    if record["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for key in ["run_id", "operation_id", "observed_at_utc", "commit"]:
        if not isinstance(record[key], str) or not record[key].strip() or "TO_BE" in record[key]:
            errors.append(f"{key} must identify an actual attempt")
    for section, fields in FIELDS.items():
        obj = record[section]
        if not isinstance(obj, dict):
            errors.append(f"{section} must be an object")
            continue
        for field in fields:
            if field not in obj:
                errors.append(f"missing {section}.{field}; use null if unmeasured")
    if errors:
        return errors
    env, outcome, transport, resources = (record[k] for k in ("environment", "outcome", "transport", "resources"))
    level = env["evidence_level"]
    if level not in LEVELS:
        errors.append("unknown evidence_level; theoretical estimates are not measurements")
    if not isinstance(outcome["test_passed"], bool):
        errors.append("outcome.test_passed must be an observed boolean")
    if outcome["verifier_reached"] is not None and not isinstance(outcome["verifier_reached"], bool):
        errors.append("outcome.verifier_reached must be boolean or null")
    for section in (transport, resources):
        for key, val in section.items():
            if key.endswith("bytes") or key in {"compute_limit", "compute_consumed", "sha256_syscall_count", "transaction_index", "transaction_count_for_operation"}:
                if val is not None and (type(val) is not int or val < 0):
                    errors.append(f"{key} must be a nonnegative integer or null")
            if key.endswith("lamports") and val is not None:
                if not isinstance(val, str) or not val.isdecimal():
                    errors.append(f"{key} must be a decimal string or null")
    if level == "host_reference":
        for key in ["compute_limit", "compute_consumed", "actual_transaction_fee_lamports", "storage_deposit_lamports", "storage_refund_lamports"]:
            if resources[key] is not None:
                errors.append(f"host_reference cannot claim onchain {key}")
        if transport["transaction_signature"] is not None or transport["confirmation_status"] is not None:
            errors.append("host_reference cannot claim network confirmation")
    if level == "devnet_confirmed":
        if env["cluster"] != "devnet":
            errors.append("devnet_confirmed must identify devnet")
        if not transport["transaction_signature"] or transport["confirmation_status"] not in {"confirmed", "finalized"}:
            errors.append("devnet_confirmed requires transaction identifier and confirmation")
    if level == "devnet_simulation" and transport["confirmation_status"] in {"confirmed", "finalized"}:
        errors.append("simulation is not network confirmation")
    if level != "host_reference" and not record["program_binary_sha256"]:
        errors.append("runtime measurement requires exact program binary digest")
    paths = record["evidence_paths"]
    if not isinstance(paths, list) or not paths or any(not isinstance(p, str) for p in paths):
        errors.append("evidence_paths must reference raw evidence")
    elif root:
        base = Path(root).resolve()
        for path in paths:
            resolved = (base / path).resolve()
            if not resolved.is_relative_to(base) or not resolved.is_file():
                errors.append(f"raw evidence not available: {path}")
    if resources["compute_consumed"] is not None and resources["compute_limit"] is not None:
        if outcome["observed"] == "success" and resources["compute_consumed"] > resources["compute_limit"]:
            errors.append("successful attempt consumed more than requested compute")
    return errors


def summarize(records, output):
    groups = {}
    for record in records:
        env, ex = record["environment"], record["experiment"]
        key = (record["commit"], record["program_binary_sha256"], env["evidence_level"], env["runtime_version"], ex["mode"], ex["asset"], ex["leaf_count"], ex["scenario"], record["transport"]["version"])
        groups.setdefault(key, []).append(record)
    headers = ["commit", "program_binary_sha256", "evidence_level", "runtime_version", "mode", "asset", "leaf_count", "scenario", "transport_version", "sample_count", "passed_count", "cu_measured_count", "cu_min", "cu_median", "cu_max", "tx_bytes_measured_count", "tx_bytes_min", "tx_bytes_median", "tx_bytes_max"]
    with Path(output).open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        for key, entries in sorted(groups.items(), key=lambda item: str(item[0])):
            row = [*key, len(entries), sum(e["outcome"]["test_passed"] for e in entries)]
            for section, metric in [("resources", "compute_consumed"), ("transport", "transaction_bytes")]:
                values = [e[section][metric] for e in entries if e[section][metric] is not None]
                row.extend([len(values), min(values) if values else None, median(values) if values else None, max(values) if values else None])
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl")
    parser.add_argument("--root", default=".")
    parser.add_argument("--summary")
    args = parser.parse_args()
    records, failures = [], []
    for line_number, line in enumerate(Path(args.jsonl).read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            errors = validate(record, args.root)
            if errors:
                failures.append({"line": line_number, "errors": errors})
            records.append(record)
        except (ValueError, TypeError) as error:
            failures.append({"line": line_number, "errors": [str(error)]})
    print(json.dumps({"records": len(records), "valid": not failures, "errors": failures}, indent=2))
    if failures:
        raise SystemExit(1)
    if args.summary:
        summarize(records, args.summary)
