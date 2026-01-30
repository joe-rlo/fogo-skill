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
- Works with SPL tokens (use Wrapped SOL for "FOGO")

**🔥 Critical for Anchor Programs**: Use `anchor-lang = "0.31.1"` with `fogo-sessions-sdk = { version = "0.7.5", features = ["anchor"] }` to avoid Pubkey type mismatches.

For complete integration guide including Rust SDK patterns, see [references/sessions.md](references/sessions.md).

### Quick Setup (React)

Install: `npm install @fogo/sessions-sdk-react`

The `FogoSessionProvider` accepts these props:

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `network` | `Network.Testnet \| Network.Mainnet` | Yes | Target network |
| `domain` | `string` | No | Your registered domain (must match paymaster config) |
| `rpc` | `string` | No | Custom RPC endpoint |
| `paymaster` | `string` | No | Custom paymaster URL (omit to use Fogo's default) |
| `tokens` | `string[]` | No | Token mints the session can spend |
| `defaultRequestedLimits` | `Record<string, bigint>` | No | Spending limits per token (in lamports) |

**⚠️ CRITICAL: The `domain` must be registered with the Fogo paymaster.** See "Paymaster Setup" below.

```tsx
import { FogoSessionProvider, SessionButton, Network } from '@fogo/sessions-sdk-react';
import { NATIVE_MINT } from '@solana/spl-token';

<FogoSessionProvider
  network={Network.Testnet}
  domain="https://your-registered-domain.com"
  tokens={[NATIVE_MINT.toBase58()]}
  defaultRequestedLimits={{
    [NATIVE_MINT.toBase58()]: 1_500_000_000n,  // 1.5 FOGO (in lamports)
  }}
>
  <SessionButton />
  {/* Your app */}
</FogoSessionProvider>
```

**Do NOT use** `sponsor`, `paymasterUrl`, or `endpoint` props — these are outdated/non-existent in the published SDK. Use `network`, `domain`, `rpc`, and `paymaster` only.

Reference implementation: https://github.com/fogo-foundation/fogo-sessions/blob/main/apps/sessions-demo/src/config/server.ts

### Quick Setup (Anchor Program)

Add to your `Cargo.toml`:

```toml
[dependencies]
anchor-lang = "0.31.1"
anchor-spl = "0.31.1"
fogo-sessions-sdk = { version = "0.7.5", features = ["anchor", "token-program"] }
# DO NOT manually add solana-program - comes from anchor-lang
```

Then in your program:

```rust
use anchor_lang::prelude::*;
use fogo_sessions_sdk::session::Session;

#[program]
pub mod my_program {
    use super::*;
    
    pub fn my_instruction(ctx: Context<MyAccounts>) -> Result<()> {
        // Extract user from wallet OR session
        let user = Session::extract_user_from_signer_or_session(
            &ctx.accounts.signer_or_session,
            &crate::ID,
        ).map_err(ProgramError::from)?;
        
        // Validate user owns resources, then execute logic
        require_keys_eq!(ctx.accounts.user_resource.owner, user);
        // ... your logic
        Ok(())
    }
}

#[derive(Accounts)]
pub struct MyAccounts<'info> {
    /// Wallet or session account
    pub signer_or_session: Signer<'info>,
    // ... your other accounts
}
```

See [references/sessions.md](references/sessions.md) for complete patterns including token transfers.

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

## Paymaster Setup

**Every app using Fogo Sessions needs a paymaster configuration.** The paymaster sponsors user transactions so users don't pay gas. On mainnet, apps fund their own paymasters.

### How It Works

1. **Domain registration** — Fogo team registers your domain with the paymaster
2. **Sponsor wallet** — Each domain gets a sponsor pubkey; you fund it with FOGO
3. **Transaction variations** — You define which transactions the paymaster should sponsor (TOML config)
4. **Submission** — Send the TOML to the Fogo team; they load it into the paymaster

### Step 1: Register Your Domain

Contact the Fogo team to register your production domain. Until registered, the paymaster will reject all requests from your domain.

### Step 2: Find & Fund Your Sponsor Address

```bash
# Get your sponsor pubkey (replace domain with yours)
# Testnet:
curl "https://fogo-testnet.dourolabs-paymaster.xyz/api/sponsor_pubkey?domain=https://yourapp.example"

# Mainnet:
curl "https://fogo-mainnet.dourolabs-paymaster.xyz/api/sponsor_pubkey?domain=https://yourapp.example"
```

Returns a base58 pubkey. Fund it:

```bash
solana transfer <SPONSOR_PUBKEY> <AMOUNT> --allow-unfunded-recipient
```

**Note:** Transactions use your sponsor's FOGO for gas, priority fees, and rent. Rent is reclaimable only to the sponsor wallet when the token account closes. No one can extract FOGO from your paymaster.

### Step 3: Define Transaction Variations (TOML)

Each distinct on-chain action your users can take needs a "variation" — a set of constraints telling the paymaster what to sponsor.

```toml
[[domains]]
domain = "https://yourapp.example"
enable_session_management = true    # Pay for session create/revoke (almost always true)
enable_preflight_simulation = true  # Simulate before landing (saves gas on failures)

[[domains.tx_variations]]
version = "v1"
name = "MyAction"               # Unique name for this action
max_gas_spend = 150000          # Upper bound gas in lamports (excludes rent)

# Which program instruction to match
[[domains.tx_variations.instructions]]
program = "<YOUR_PROGRAM_ID>"   # Base58 program address
required = true                 # true = must be in every tx; false = optional

# Account constraints (optional)
[[domains.tx_variations.instructions.accounts]]
index = 0                       # Account index in the instruction
include = [{ NonFeePayerSigner = {} }]  # Must match one of these
exclude = []                    # Must NOT match any of these

# Data constraints — match instruction discriminator (optional)
[[domains.tx_variations.instructions.data]]
start_byte = 0
data_type = "U8"
constraint = { EqualTo = [{ U8 = 44 }] }  # First byte of Anchor discriminator
```

**Anchor discriminators:** First 8 bytes of `SHA256("global:<function_name>")`. Use the first byte for the `EqualTo` constraint.

```python
# Calculate discriminator
import hashlib
h = hashlib.sha256(b"global:my_function").digest()
first_byte = h[0]  # Use this in EqualTo constraint
```

**Tips:**
- `enable_session_management = true` — almost always; pays for session create/revoke
- `enable_preflight_simulation = true` — almost always; saves gas on failed txs
- Omit `accounts`/`data` arrays entirely if no constraints needed
- Use narrowly scoped `EqualTo` for discriminators
- Set `required = false` for optional instructions (e.g., ATA creation, compute budget)

### Step 4: Submit to Fogo Team

Send your TOML config to the Fogo team through the agreed channel. They load it into the paymaster and restart.

### Validating Your Config

Fogo provides a CLI tool to validate transactions against your config:

```bash
# Install
cargo install fogo-paymaster --bin paymaster-tx-validator

# Validate a historical transaction
paymaster-tx-validator validate \
  --config config.toml \
  --rpc-url-http https://testnet.fogo.io \
  --transaction-hash <TRANSACTION_SIGNATURE>

# Validate from base64
paymaster-tx-validator validate \
  --config config.toml \
  --rpc-url-http https://testnet.fogo.io \
  --transaction <BASE64_ENCODED_TX>

# Validate recent sponsor transactions against new config
paymaster-tx-validator validate \
  --config config.toml \
  --rpc-url-http https://testnet.fogo.io \
  --recent-sponsor-txs 100
```

### Paymaster API Endpoints

| Endpoint | Testnet | Mainnet |
|----------|---------|---------|
| Sponsor pubkey | `https://fogo-testnet.dourolabs-paymaster.xyz/api/sponsor_pubkey?domain=...` | `https://fogo-mainnet.dourolabs-paymaster.xyz/api/sponsor_pubkey?domain=...` |
| Sponsor & send | `https://fogo-testnet.dourolabs-paymaster.xyz/api/sponsor_and_send?domain=...` | `https://fogo-mainnet.dourolabs-paymaster.xyz/api/sponsor_and_send?domain=...` |

### Example: Full TOML for a Trading App

```toml
[[domains]]
domain = "https://sessions-example.fogo.io"
enable_session_management = true
enable_preflight_simulation = true

## Deposit variation
[[domains.tx_variations]]
version = "v1"
name = "Deposit"
max_gas_spend = 500000

# Optional ATA creation
[[domains.tx_variations.instructions]]
program = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
required = false
[[domains.tx_variations.instructions.data]]
start_byte = 0
data_type = "U8"
constraint = { EqualTo = [{ U8 = 1 }] }

# Core deposit instruction
[[domains.tx_variations.instructions]]
program = "YourProgramId111111111111111111111111111111"
required = true
[[domains.tx_variations.instructions.accounts]]
index = 0
include = [{ NonFeePayerSigner = {} }]
exclude = []
[[domains.tx_variations.instructions.data]]
start_byte = 0
data_type = "U8"
constraint = { EqualTo = [{ U8 = 12 }] }
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "domain is not registered" | Domain not in paymaster config | Contact Fogo team to register |
| "Transaction does not match any allowed variations" | Tx instructions don't match your TOML | Check discriminators, account indices, program IDs |
| Paymaster 400 | Various config mismatches | Validate with `paymaster-tx-validator` CLI |
| Paymaster 500 | Server-side issue | Usually transient; retry or contact Fogo |

### Runbook Reference

Full paymaster runbook: https://dourolabs.notion.site/Paymaster-Runbook-2763e0276d9380268d5bde602d00f887

## Wallet & Token Operations

### Create Keypair

```bash
solana-keygen new --outfile ~/fogo-wallet.json
solana-keygen pubkey ~/fogo-wallet.json
```

### Transfer Tokens

```bash
# Native FOGO
solana transfer <DEST_ADDRESS> <AMOUNT>

# FOGO SPL tokens
spl-token transfer So11111111111111111111111111111111111111112 <DEST_ADDRESS> <AMOUNT>

# fUSD
spl-token transfer fUSDNGgHkZfwckbr5RLLvRbvqvRcTLdH9hcHJiq4jry <DEST_ADDRESS> <AMOUNT>
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

- Sessions Demo (Next.js): https://github.com/fogo-foundation/fogo-sessions/tree/main/apps/sessions-demo
- Sessions Monorepo: https://github.com/fogo-foundation/fogo-sessions
- Vite Sessions: https://github.com/fogo-foundation/sessions-example-vite
