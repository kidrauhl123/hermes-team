#!/usr/bin/env python3
import argparse
import json
import os
import time
from pathlib import Path
from gateway.platforms.feishu import _poll_registration, probe_bot

parser = argparse.ArgumentParser()
parser.add_argument("account_id")
parser.add_argument("--out-dir", required=True)
parser.add_argument("--config", required=False)
parser.add_argument("--timeout", type=int, default=90)
args = parser.parse_args()

out = Path(args.out_dir)
pending_path = out / f"{args.account_id}.pending.json"
if not pending_path.exists():
    raise SystemExit(json.dumps({"ok": False, "error": "pending_not_found", "account_id": args.account_id}))

pending = json.loads(pending_path.read_text(encoding="utf-8"))
created = float(pending.get("created_at") or time.time())
expire_in = int(pending.get("expire_in") or 600)
remaining = int(created + expire_in - time.time())
if remaining <= 0:
    raise SystemExit(json.dumps({"ok": False, "error": "expired", "account_id": args.account_id}))

poll_timeout = max(1, min(args.timeout, remaining))
interval = int(pending.get("interval") or 5)
result = _poll_registration(
    device_code=str(pending["device_code"]),
    interval=interval,
    expire_in=poll_timeout,
    domain=str(pending.get("domain") or "feishu"),
)
if not result:
    raise SystemExit(json.dumps({"ok": False, "error": "not_ready", "account_id": args.account_id, "remaining": remaining}))

bot_info = None
try:
    bot_info = probe_bot(result["app_id"], result["app_secret"], result.get("domain") or "feishu")
except Exception:
    bot_info = None

payload = {
    "account_id": args.account_id,
    "app_id": result["app_id"],
    "app_secret": result["app_secret"],
    "domain": result.get("domain") or pending.get("domain") or "feishu",
    "open_id": result.get("open_id"),
    "bot": bot_info or {},
    "created_at": time.time(),
}
cred_path = out / f"{args.account_id}.json"
tmp = cred_path.with_suffix(".json.tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
os.chmod(tmp, 0o600)
tmp.replace(cred_path)
os.chmod(cred_path, 0o600)

if args.config:
    cfg = Path(args.config)
    text = cfg.read_text(encoding="utf-8")
    upper = args.account_id.upper()
    text = text.replace(f"REPLACE_WITH_{upper}_APP_ID", payload["app_id"])
    text = text.replace(f"REPLACE_WITH_{upper}_APP_SECRET", payload["app_secret"])
    cfg.write_text(text, encoding="utf-8")
    os.chmod(cfg, 0o600)

print(json.dumps({
    "ok": True,
    "account_id": args.account_id,
    "credential_path": str(cred_path),
    "config_updated": bool(args.config),
    "bot_name": (bot_info or {}).get("bot_name"),
    "domain": payload["domain"],
}, ensure_ascii=False))
