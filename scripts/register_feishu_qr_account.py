#!/usr/bin/env python3
"""Register one Feishu/Lark bot via QR flow and save credentials without printing secrets."""
import argparse
import json
import os
from pathlib import Path

from gateway.platforms.feishu import qr_register


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("account_id")
    parser.add_argument("--domain", default="feishu", choices=["feishu", "lark"])
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)

    print(f"Starting Feishu QR registration for account_id={args.account_id!r}", flush=True)
    result = qr_register(initial_domain=args.domain, timeout_seconds=args.timeout)
    if not result:
        print(f"Registration failed or timed out for {args.account_id}", flush=True)
        return 2

    payload = {
        "account_id": args.account_id,
        "domain": result.get("domain") or args.domain,
        "app_id": result.get("app_id"),
        "app_secret": result.get("app_secret"),
        "bot_name": result.get("bot_name"),
        "bot_open_id": result.get("bot_open_id"),
        "route_profile": args.account_id,
    }
    if not payload["app_id"] or not payload["app_secret"]:
        print(f"Registration returned incomplete credentials for {args.account_id}", flush=True)
        return 3

    out_path = out_dir / f"{args.account_id}.json"
    tmp_path = out_path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.chmod(tmp_path, 0o600)
    tmp_path.replace(out_path)
    os.chmod(out_path, 0o600)
    print(f"Registration saved for {args.account_id}: {out_path} (secret not printed)", flush=True)
    if payload.get("bot_name"):
        print(f"Bot name: {payload['bot_name']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
