---
name: fogo
description: "Build and deploy applications on Fogo, a high-performance Layer 1 blockchain with full Solana (SVM) compatibility. Use when working with Fogo blockchain development including: (1) Deploying Solana programs to Fogo, (2) Configuring Anchor or Solana CLI for Fogo, (3) Integrating Fogo Sessions for gasless UX, (4) Using Fogo RPC endpoints, (5) Working with FOGO/fUSD tokens, (6) Connecting to testnet/mainnet, or any Fogo-related blockchain development tasks."
---

# Fogo Development

Fogo is a Layer 1 blockchain built for DeFi with full Solana Virtual Machine (SVM) compatibility. It features 40ms block times and multi-local consensus for minimal latency.

## Quick Reference

### RPC Endpoints

```
Mainnet: https://mainnet.fogo.io
Testnet: https://testnet.fogo.io
```

### Key Tokens

| Token | Mint Address |
|-------|-------------|
| FOGO SPL | `So11111111111111111111111111111111111111112` |
| fUSD | `fUSDNGgHkZfwckbr5RLLvRbvqvRcTLdH9hcHJiq4jry` |

### Resources

- Faucet: https://faucet.fogo.io
- Explorer: https://fogoscan.com
- Docs: https://docs.fogo.io

## Deploying Programs

Fogo is 100% SVM-compatible. Any Solana program deploys without modification.

### Solana CLI

```bash
# Configure for Fogo
solana config set --url https://mainnet.fogo.io  # or https://testnet.fogo.io

# Deploy program
solana program deploy <PATH_TO_PROGRAM_SO>
```

### Anchor

Update `Anchor.toml`:

```toml
[provider]
cluster = "https://mainnet.fogo.io"  # or https://testnet.fogo.io
```

Then build and deploy:

```bash
anchor build
anchor deploy
```

## Fogo Sessions Integration

Fogo Sessions provide gasless, no-approve UX via account abstraction and paymasters. Users interact without signing individual transactions or paying gas.

**Key features:**
- Domain verification (XSS protection)
- Spending limits per token
- Session expiry with renewal

For complete integration guide, see [references/sessions.md](references/sessions.md).

### Quick Setup (React)

Install: `npm install @fogo/sessions-sdk-react`

```tsx
import { FogoSessionProvider, SessionButton } from '@fogo/sessions-sdk-react';
import { NATIVE_MINT } from '@solana/spl-token';

<FogoSessionProvider
  sponsor="8HnaXmgFJbvvJxSdjeNyWwMXZb85E35NM4XNg6rxuw3w"
  paymasterUrl="https://sessions-example.fogo.io/paymaster"
  domain={process.env.NODE_ENV === "production" ? undefined : "https://your-dev-domain.com"}
  endpoint="https://testnet.fogo.io/"
  tokens={[NATIVE_MINT.toBase58()]}
  defaultRequestedLimits={{
    [NATIVE_MINT.toBase58()]: 1_500_000_000n,
  }}
>
  <SessionButton />
  {/* Your app */}
</FogoSessionProvider>
```

### Using Sessions Programmatically

```tsx
import { useSession, SessionStateType, isEstablished } from '@fogo/sessions-sdk-react';

function MyComponent() {
  const session = useSession();
  
  if (session.type === SessionStateType.NotEstablished) {
    return <button onClick={() => session.establish()}>Connect</button>;
  }
  
  if (isEstablished(session)) {
    const { walletPublicKey, sessionPublicKey, sendTransaction, endSession } = session;
    
    // Send transaction (pass array of TransactionInstruction)
    await sendTransaction([instruction1, instruction2]);
  }
}
```

## Wallet & Token Operations

### Create Keypair

```bash
solana-keygen new --outfile ~/fogo-wallet.json
solana-keygen pubkey ~/fogo-wallet.json
```

### Transfer Tokens

```bash
# Native FOGO
solana --keypair ~/fogo-wallet.json transfer <DEST_ADDRESS> <AMOUNT>

# FOGO SPL tokens
spl-token --keypair ~/fogo-wallet.json transfer So11111111111111111111111111111111111111112 <DEST_ADDRESS> <AMOUNT>

# fUSD
spl-token --keypair ~/fogo-wallet.json transfer fUSDNGgHkZfwckbr5RLLvRbvqvRcTLdH9hcHJiq4jry <DEST_ADDRESS> <AMOUNT>
```

### Get Testnet Tokens

Visit https://faucet.fogo.io and select:
- **FOGO (native)**: For transaction fees (developers)
- **FOGO**: SPL tokens for Fogo Sessions users
- **fUSD**: Stablecoin SPL tokens

## Ecosystem Integrations

| Service | Purpose | Docs |
|---------|---------|------|
| Pyth Lazer | Low-latency price feeds | https://docs.pyth.network/lazer |
| Wormhole | Cross-chain bridges | https://portalbridge.com |
| Metaplex | NFTs & tokens | Full SVM compatibility |
| Squads | Multisig wallets | Full SVM compatibility |
| FluxRPC | High-performance RPC | See [references/fluxrpc.md](references/fluxrpc.md) |
| Goldsky | Indexing | See Goldsky docs |

## Architecture Notes

- **Client**: Firedancer-based (high-performance Solana-compatible)
- **Block time**: 40ms target
- **Consensus**: Multi-local with zone rotation across epochs
- **Compatibility**: Full SVM execution layer compatibility

## Example Projects

- NextJS Sessions: https://github.com/fogo-foundation/sessions-example
- Vite Sessions: https://github.com/fogo-foundation/sessions-example-vite
