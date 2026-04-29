#!/usr/bin/env python3
import argparse, json, os, time
from pathlib import Path
from gateway.platforms.feishu import _init_registration, _begin_registration

parser=argparse.ArgumentParser()
parser.add_argument('account_id')
parser.add_argument('--domain', default='feishu')
parser.add_argument('--out-dir', required=True)
args=parser.parse_args()
out=Path(args.out_dir); out.mkdir(parents=True, exist_ok=True); os.chmod(out,0o700)
_init_registration(args.domain)
begin=_begin_registration(args.domain)
payload={
 'account_id': args.account_id,
 'domain': args.domain,
 'device_code': begin['device_code'],
 'qr_url': begin['qr_url'],
 'user_code': begin.get('user_code',''),
 'interval': begin.get('interval') or 5,
 'expire_in': begin.get('expire_in') or 600,
 'created_at': time.time(),
}
path=out/f'{args.account_id}.pending.json'
tmp=path.with_suffix('.pending.json.tmp')
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
os.chmod(tmp,0o600); tmp.replace(path); os.chmod(path,0o600)
print(json.dumps({'account_id': args.account_id, 'qr_url': payload['qr_url'], 'user_code': payload['user_code'], 'pending_path': str(path), 'expire_in': payload['expire_in']}, ensure_ascii=False))
