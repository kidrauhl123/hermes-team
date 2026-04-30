# Feishu/Lark QR onboarding pitfalls from live multi-account setup

Context: adding a 5th Feishu bot account to an existing unified `~/.hermes/profiles/feishu` multi-account gateway.

## What happened

- `scripts/begin_feishu_qr_account.py` and `scripts/poll_feishu_qr_account.py` can hang when run through the normal Python/urllib path in this environment; the command timed out without producing the QR payload.
- `curl` against `https://accounts.feishu.cn/oauth/v1/app/registration` sometimes succeeds with verbose `-4`, but repeated simple `curl -sS ... --data ...` calls through helper wrappers also timed out.
- A direct Python `urllib.request` call with forced IPv4 via `socket.getaddrinfo` and `Connection: close` returned a QR code quickly.
- Polling after the user said they created the app repeatedly returned:

```json
{"error":"invalid_grant","error_description":"The device_code is invalid. Please restart the device authorization flow.","code":20079}
```

Treat this as terminal for that QR flow: immediately generate a fresh begin link rather than continuing to poll.

## Useful begin snippet

```python
from pathlib import Path
import urllib.request, urllib.parse, json, socket, time, os

orig = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

body = urllib.parse.urlencode({
    'action': 'begin',
    'archetype': 'PersonalAgent',
    'auth_method': 'client_secret',
    'request_user_info': 'open_id',
}).encode()
req = urllib.request.Request(
    'https://accounts.feishu.cn/oauth/v1/app/registration',
    data=body,
    headers={'Content-Type': 'application/x-www-form-urlencoded', 'Connection': 'close'},
)
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read().decode())
qr = d.get('verification_uri_complete', '')
qr += ('&' if '?' in qr else '?') + 'from=hermes&tp=hermes'
```

Save pending state with mode `0600` under the isolated/current profile, e.g. `$HERMES_HOME/feishu-accounts/5.pending.json`, containing `device_code`, `qr_url`, `user_code`, `interval`, `expire_in`, and `created_at`.

## User-facing behavior

When the user is waiting for QR scan links, keep the response extremely short and put the link/code first. They may miss messages; on “没看见/再来”, immediately generate a new begin link and do not lecture.

Format:

```md
**链接：** <qr_url>
**验证码：** `<user_code>`
**有效期：** 约 10 分钟
```

After user confirms creation, poll immediately. If `invalid_grant` appears, say the flow expired/invalid and generate a fresh link in the same turn if possible.
