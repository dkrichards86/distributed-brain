# gRPC (Google Remote Procedure Call)

A high-performance open-source RPC framework that uses HTTP/2 for transport and Protocol Buffers for serialization, generating type-safe client/server code from a shared schema.

## Why it matters

REST over JSON is the default for inter-service communication, but it has real costs: text serialization is slow, field names are repeated on every message, there's no enforced contract, and streaming is bolted on awkwardly. gRPC addresses all of these — binary encoding via Protocol Buffers reduces payload size, the `.proto` contract is enforced at build time, and HTTP/2 enables native bidirectional streaming. It's the dominant choice for internal service-to-service communication in polyglot microservice environments.

## How it works

Services are defined in `.proto` files using the Protocol Buffer IDL. The `protoc` compiler generates client stub and server skeleton code for the target language. At runtime:

1. The client calls a generated stub method as if it were a local function call
2. The stub serializes the request using [Protocol Buffers](Protocol%20Buffers.md) and opens an HTTP/2 stream
3. HTTP/2 multiplexing means many concurrent RPC calls share one TCP connection without head-of-line blocking
4. The server deserializes the request, invokes the handler, and streams back the response

### Four call types

- **Unary** — single request, single response (standard request/response)
- **Server streaming** — single request, stream of responses (e.g., subscribing to events)
- **Client streaming** — stream of requests, single response (e.g., uploading a large dataset)
- **Bidirectional streaming** — both sides stream simultaneously (e.g., chat, real-time telemetry)

### Interceptors

Middleware for gRPC — applied on the client or server side to add logging, authentication, metrics, tracing, or retry logic uniformly across all methods.

## Key tradeoffs

- **Binary protocol is hard to debug** — you can't `curl` a gRPC endpoint and read the response; need tools like `grpcurl` or a gRPC reflection server to inspect traffic
- **Browser limitation** — browsers can't speak gRPC directly over HTTP/2; requires a gRPC-Web proxy (Envoy or grpc-gateway) that translates to HTTP/1.1
- **Schema management overhead** — `.proto` files must be versioned, distributed to all services, and kept in sync; breaking changes (removing or renumbering fields) affect all clients simultaneously
- **HTTP/2 everywhere** — some proxies and load balancers need explicit HTTP/2 support; L4 load balancers will route all requests on a connection to one backend, requiring L7 load balancing for per-request distribution

## Related concepts

- [Protocol Buffers](Protocol%20Buffers.md) — the serialization format gRPC uses; field numbering and schema evolution rules apply directly to gRPC service definitions
- [Thrift](Thrift.md) — Facebook's alternative to gRPC; similar IDL-driven approach with pluggable serialization
- [Service Discovery](../Architecture/Service%20Discovery.md) — gRPC clients need to resolve service names to live endpoints; gRPC integrates with Consul, etcd, and xDS (used by Envoy)
- [Service Mesh](../Architecture/Service%20Mesh.md) — service mesh sidecars (Envoy) are gRPC-aware and can load-balance at the individual RPC call level, not just the connection level
- [Load Balancing](../Architecture/Load%20Balancing.md) — gRPC's long-lived HTTP/2 connections require L7 load balancing to distribute individual RPCs across backend instances
- [Apache Arrow](Apache%20Arrow.md) — Arrow Flight is an RPC protocol built on gRPC designed for high-throughput bulk columnar data transfer
