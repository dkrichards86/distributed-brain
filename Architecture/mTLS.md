# mTLS (Mutual TLS)

A variant of TLS where both the client and server authenticate each other with certificates, not just the server authenticating to the client.

## Why it matters

Standard TLS only proves the server's identity to the client — the client can verify it's talking to the right server, but the server has no cryptographic proof of who the client is. In a microservices architecture where services communicate over a shared network, any compromised service (or any process that can reach the network) could call any other service. mTLS closes this gap: every service proves its identity on every connection, making lateral movement within the cluster significantly harder.

## How it works

TLS handshake with mutual authentication:

1. **Client connects** — initiates TLS, server presents its certificate
2. **Server requests client certificate** — unlike standard TLS, the server sends a `CertificateRequest` message
3. **Client presents its certificate** — signed by a trusted Certificate Authority (CA)
4. **Both verify** — each side verifies the other's certificate against its trust store (the CA cert)
5. **Session established** — encrypted, and both sides are authenticated

All subsequent traffic on the connection is encrypted and tied to these verified identities.

### Certificate issuance in practice

Each service needs a certificate identifying it. In a Kubernetes cluster with a [service mesh](Service%20Mesh.md):

- The mesh control plane (Istio's Citadel, Linkerd's identity service) runs an internal CA
- When a pod starts, its [sidecar](Sidecar.md) requests a certificate from the control plane, presenting a Kubernetes service account token as proof of identity
- The control plane issues a short-lived certificate (typically 24 hours) identifying the pod's service account
- The sidecar handles TLS termination for all traffic; the application itself speaks plain HTTP to its sidecar

Short certificate lifetimes reduce the blast radius of a leaked certificate — it expires quickly without needing explicit revocation.

### SPIFFE

SPIFFE (Secure Production Identity Framework For Everyone) is a standard for workload identity in dynamic infrastructure. A SPIFFE identity is a URI embedded in the certificate's Subject Alternative Name field: `spiffe://trust-domain/path/to/workload`. Service meshes issue SPIFFE-compatible certificates so identities are portable across mesh implementations.

### Without a service mesh

mTLS can be implemented directly in application code or via a sidecar without a full mesh. The challenge is certificate distribution and rotation at scale — why most teams reach for a service mesh rather than managing it themselves.

## Key tradeoffs

- **Certificate management overhead** — every service needs a certificate, and certificates must be rotated before expiry; automating this correctly is non-trivial without a control plane
- **Debugging complexity** — TLS handshake failures are harder to diagnose than plain connection errors; certificate expiry or misconfigured trust stores cause opaque failures
- **Performance** — TLS adds CPU cost (asymmetric crypto on handshake, symmetric crypto on data); within a cluster, the handshake cost is amortized over connection lifetime; modern hardware makes per-byte encryption negligible

## Related concepts

- [Service Mesh](Service%20Mesh.md) — service meshes automate mTLS across the entire cluster; the control plane handles certificate issuance and rotation, the sidecar handles termination
- [Sidecar](Sidecar.md) — the sidecar terminates mTLS connections so the application doesn't need to implement TLS directly
- [One-Time Passwords](../Engineering/One-Time%20Passwords.md) — a different authentication mechanism; mTLS authenticates services via certificates, OTPs authenticate humans via time-bounded codes
- [API Gateway](API%20Gateway.md) — the gateway may terminate external TLS and re-establish mTLS to backend services, or enforce mTLS between clients and the gateway itself
