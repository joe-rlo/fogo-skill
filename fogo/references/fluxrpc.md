# FluxRPC Reference

FluxRPC is a high-performance RPC layer for Fogo, designed for both consumer apps and high-frequency trading.

## Key Features

- **Validator-Decoupled**: Runs separately from validator nodes, avoiding bottlenecks
- **Edge Caching**: Frequent requests served instantly via cache
- **Chaos-Proof**: Resilient during market volatility and bot surges
- **Bandwidth-Based Pricing**: Pay only for actual usage

## Quick Start

1. Sign up at FluxRPC portal
2. Generate API keys
3. Configure endpoint in your app

## Making RPC Calls

FluxRPC uses standard Solana JSON-RPC interface.

### TypeScript Example

```typescript
import { Connection } from '@solana/web3.js';

const connection = new Connection('https://your-fluxrpc-endpoint.fogo.io', {
  httpHeaders: {
    'Authorization': `Bearer ${YOUR_API_KEY}`
  }
});

// Standard Solana RPC calls work
const balance = await connection.getBalance(publicKey);
const block = await connection.getBlock(slot);
const accountInfo = await connection.getAccountInfo(publicKey);
```

### Go Example

```go
import (
    "github.com/gagliardetto/solana-go/rpc"
)

client := rpc.New("https://your-fluxrpc-endpoint.fogo.io")
// Add auth headers as needed
```

## Common RPC Methods

All standard Solana RPC methods are supported:

- `getAccountInfo` - Get account data
- `getBalance` - Get SOL/FOGO balance
- `getBlock` - Get block data
- `getTransaction` - Get transaction details
- `sendTransaction` - Submit transaction
- `simulateTransaction` - Simulate without submitting

## Yellowstone gRPC Streaming

Subscribe to real-time updates:

- Block updates
- Transaction logs
- Account changes

See FluxRPC docs for gRPC setup.

## Lantern (Edge Cache)

Lantern is an optional local cache layer:

- Drop-in front of any FluxRPC endpoint
- Run via Docker or CLI
- Caches frequent requests locally

### Docker Setup

```bash
docker run -d \
  -p 8899:8899 \
  -e UPSTREAM_RPC=https://your-fluxrpc-endpoint.fogo.io \
  fluxrpc/lantern:latest
```

Then connect to `http://localhost:8899`.

## Rate Limits & Pricing

- Generous free tier for development
- Scale-based pricing for production
- Bandwidth-based (no request count limits)

See FluxRPC portal for current pricing.
