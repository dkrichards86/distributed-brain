# One-Time Passwords (HOTP / TOTP)

Algorithms that generate short-lived numeric codes from a shared secret, enabling two-factor authentication without transmitting the secret over the network.

## Why it matters

Passwords alone are vulnerable to phishing, reuse, and interception. OTPs add a second factor that can't be reused and expires quickly — even if an attacker intercepts one, it's useless moments later. Unlike SMS codes, TOTP works offline and doesn't depend on cellular service.

## How it works

Both HOTP and TOTP use **HMAC-SHA1** to derive a code from a shared secret and a counter value. The same inputs always produce the same output, so client and server can independently generate identical codes without communicating.

### HOTP (HMAC-based OTP)

Uses a manually incremented counter shared between client and server.

1. Both sides keep a counter in sync
2. To generate: `HMAC-SHA1(secret, counter)` → truncate to 6 digits
3. Each generated code increments the counter

**Problem:** If you generate codes without using them (testing, curiosity), the counter drifts. The server needs a "look-ahead window" to handle drift, adding complexity.

### TOTP (Time-based OTP)

Replaces the manual counter with the current timestamp: `counter = floor(unix_timestamp / 30)`.

Both sides compute the same counter value from their clocks — no manual synchronization needed. Codes rotate every 30 seconds.

**Clock tolerance:** Servers typically accept codes from the current window ± 1 window to handle minor clock drift (up to ~30 seconds off).

**Security properties:**
- Codes are time-limited — interception gives an attacker 30–60 seconds
- HMAC is one-way — knowing a code reveals nothing about the secret or future codes
- Works fully offline — the phone only needs the secret and the current time

### Setup and implementation

The shared secret is exchanged at enrollment via a QR code containing the secret (base32-encoded), issuer name, and account ID.

**Truncation process:** The 20-byte HMAC output is converted to 6 digits via dynamic truncation — the last nibble of the hash selects an offset, 4 bytes are extracted at that offset, converted to decimal, and taken modulo 10^6.

Most implementations support SHA1/SHA256/SHA512 and 6 or 8 digit codes. 6-digit SHA1 is the dominant standard for compatibility.

### HOTP vs. TOTP

| | HOTP | TOTP |
|---|---|---|
| Counter | Manual, per-use | Time-based (Unix timestamp / 30) |
| Synchronization | Can drift, needs look-ahead | Automatic via clocks |
| Offline use | Yes | Yes |
| Use case | Hardware tokens without clocks | Authenticator apps (Google Authenticator, Authy) |

TOTP is the right choice for virtually all software 2FA implementations.

## Key tradeoffs

- **TOTP vs. SMS 2FA** — TOTP is more secure (no SIM swap vulnerability, works offline) but slightly higher setup friction; SMS is lower friction but weaker security
- **30-second window** — balances usability (enough time to type) with security (short exposure window for intercepted codes); shorter windows improve security but frustrate users on slow connections
- **Clock accuracy dependency** — TOTP requires reasonably accurate clocks on both client and server; the ±1 window tolerance handles minor drift, but large clock skew breaks authentication
- **Shared secret storage** — the secret must be stored securely on both sides; if the server's secret store is compromised, all TOTP codes for those accounts can be forged
