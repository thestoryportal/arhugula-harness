"""Append a land-event line to .harness/state.jsonl. Usage: python3 _append_state.py U-CP-NN"""
import json, hashlib, uuid, datetime, sys, pathlib

unit = sys.argv[1]
p = pathlib.Path(__file__).parent / "state.jsonl"
last = json.loads(p.read_text().splitlines()[-1])
entry = {
    "action_id": str(uuid.uuid4()),
    "actor": "phase-7-implementation",
    "idempotency_key": hashlib.md5(f"land:{unit}".encode()).hexdigest(),
    "prior_event_hash": last["response_hash"],
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
entry["response_hash"] = hashlib.sha256(
    json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
with p.open("a") as f:
    f.write(json.dumps(entry) + "\n")
print(f"appended {unit} {entry['response_hash']}")
