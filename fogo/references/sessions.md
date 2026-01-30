# Fogo Sessions Integration Reference

Complete guide for integrating Fogo Sessions into applications.

> **🔥 Critical Version Info**: Use `anchor-lang = "0.31.1"` with `fogo-sessions-sdk = { version = "0.7.5", features = ["anchor"] }` to avoid Pubkey type mismatches. See Dependency Compatibility section below.

## Sessions vs Traditional Wallets

| Aspect | Traditional Solana Wallet | Fogo Sessions |
|--------|---------------------------|---------------|
| **Transaction signing** | User signs every transaction | User signs once to create session |
| **Gas fees** | User pays for each tx | Paymaster covers fees |
| **Onboarding friction** | Must fund wallet first | Instant start, no funding needed |
| **UX flow** | Approve popup per action | Seamless, no interruptions |
| **Security model** | Full wallet access | Scoped limits per session |
| **Token support** | All tokens + native SOL | SPL tokens only (no native FOGO) |
| **Best for** | Power users, large txs | Consumer apps, frequent interactions |

### When to Use Sessions

✅ **Use Fogo Sessions when:**
- Building consumer-facing DeFi apps
- Users make frequent, small transactions
- Onboarding speed matters (games, social apps)
- You want to abstract away blockchain complexity

❌ **Use traditional wallets when:**
- Users need to interact with native FOGO
- Transactions exceed reasonable session limits
- Users prefer explicit approval per transaction

## React SDK

Package: `@fogo/sessions-sdk-react`

### FogoSessionProvider Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `network` | `Network.Testnet \| Network.Mainnet` | Yes | Target network. SDK uses built-in defaults for paymaster routing. |
| `domain` | `string` | No | Your registered domain. **Must match paymaster config.** Omit in production to auto-detect. |
| `rpc` | `string` | No | Custom RPC endpoint. Omit to use network defaults. |
| `paymaster` | `string` | No | Custom paymaster URL. Omit to use Fogo's default paymaster. |
| `tokens` | `string[]` | No | Token mints the session can spend. |
| `defaultRequestedLimits` | `Record<string, bigint>` | No | Spending limits per token (in lamports). |
| `enableUnlimited` | `boolean` | No | Allow unlimited session spending. |
| `defaultAddressLookupTableAddress` | `string` | No | Address lookup table for tx optimization. |

**⚠️ IMPORTANT:** Do NOT use `sponsor`, `paymasterUrl`, or `endpoint` — these props do not exist in the published SDK. Use `network`, `domain`, `rpc`, and `paymaster` only. (Note: The official docs at `docs.fogo.io` still show the old props — trust the SDK, not the docs page.)

### Reference Implementation

From [`fogo-foundation/fogo-sessions/apps/sessions-demo/src/config/server.ts`](https://github.com/fogo-foundation/fogo-sessions/blob/main/apps/sessions-demo/src/config/server.ts):

```tsx
// Standard testnet/mainnet setup (uses Fogo's built-in paymaster):
<FogoSessionProvider
  network={Network.Testnet}
  domain="https://your-registered-domain.com"
  tokens={[NATIVE_MINT.toBase58()]}
  defaultRequestedLimits={{
    [NATIVE_MINT.toBase58()]: 1_500_000_000n,
  }}
>
  <SessionButton />
  {children}
</FogoSessionProvider>

// Custom paymaster setup (self-hosted or localnet):
<FogoSessionProvider
  network={Network.Testnet}
  rpc="http://127.0.0.1:8899"
  paymaster="http://localhost:4000"
  domain="http://localhost:3000"
  tokens={[NATIVE_MINT.toBase58()]}
  defaultRequestedLimits={{
    [NATIVE_MINT.toBase58()]: 1_500_000_000n,
  }}
>
```

### SessionButton Component

Adds connect button with wallet management panel when connected.

### useSession Hook

```tsx
import { useSession, SessionStateType, isEstablished } from '@fogo/sessions-sdk-react';

function MyComponent() {
  const session = useSession();
  
  if (session.type === SessionStateType.NotEstablished) {
    return <button onClick={() => session.establish()}>Connect</button>;
  }
  
  if (isEstablished(session)) {
    const { walletPublicKey, sessionPublicKey, sendTransaction, endSession } = session;
    
    // Send transaction — pass array of TransactionInstruction
    // Use sessionPublicKey as signer, NOT walletPublicKey
    await sendTransaction([instruction1, instruction2]);
  }
}
```

## Paymaster Setup

Every app using Fogo Sessions needs a paymaster configuration. The paymaster sponsors user transactions so users don't pay gas. **On mainnet, apps fund their own paymasters.**

### How It Works

1. **Domain registration** — Fogo team registers your domain with the paymaster
2. **Sponsor wallet** — Each domain gets a sponsor pubkey; you fund it with FOGO
3. **Transaction variations** — You define which transactions the paymaster sponsors (TOML config)
4. **Submission** — Send the TOML to the Fogo team; they load it into the paymaster

### Step 1: Register Your Domain

Contact the Fogo team to register your production domain. Until registered, the paymaster will reject all requests from your domain with: `"The domain X is not registered with the paymaster"`.

### Step 2: Find & Fund Your Sponsor Address

```bash
# Get your sponsor pubkey (testnet)
curl "https://fogo-testnet.dourolabs-paymaster.xyz/api/sponsor_pubkey?domain=https://yourapp.example"

# Get your sponsor pubkey (mainnet)
curl "https://fogo-mainnet.dourolabs-paymaster.xyz/api/sponsor_pubkey?domain=https://yourapp.example"
```

Returns a base58 pubkey. Fund it with native FOGO:

```bash
solana transfer <SPONSOR_PUBKEY> <AMOUNT> --allow-unfunded-recipient
```

**Economics:**
- Transactions use your sponsor's FOGO for gas and priority fees
- Rent is paid from sponsor's FOGO but reclaimable to sponsor wallet when token accounts close
- **No one can extract FOGO from your paymaster for their own gain**

### Step 3: Define Transaction Variations (TOML)

Each distinct on-chain action needs a "variation" — constraints telling the paymaster what to sponsor. One variation per user action you want to fund.

```toml
[[domains]]
domain = "https://yourapp.example"
enable_session_management = true    # Pay for session create/revoke (almost always true)
enable_preflight_simulation = true  # Simulate before landing (saves gas on failures)

[[domains.tx_variations]]
version = "v1"
name = "MyAction"               # Unique, stable name for this action type
max_gas_spend = 150000          # Upper bound gas in lamports (excludes rent)

# Which program instruction to match
[[domains.tx_variations.instructions]]
program = "<PROGRAM_ID>"        # Base58 program address
required = true                 # true = must appear in tx; false = optional

# Account constraints (optional — omit entirely if unused)
[[domains.tx_variations.instructions.accounts]]
index = 0                       # Account index in the instruction
include = [{ NonFeePayerSigner = {} }]
exclude = []

# Data constraints — match instruction discriminator (optional — omit if unused)
[[domains.tx_variations.instructions.data]]
start_byte = 0
data_type = "U8"
constraint = { EqualTo = [{ U8 = 44 }] }  # Match first byte of discriminator
```

**Key fields:**
- `enable_session_management = true` — almost always; pays for session create/revoke
- `enable_preflight_simulation = true` — almost always; saves gas on failed txs
- `required = true` — instruction must appear in tx; `false` for optional (ATA creation, compute budget)
- `include` — account at index must match one of these
- `exclude` — account at index must not match any of these
- Data constraints: `EqualTo`, `LessThan`, `GreaterThan`, `Neq` — all take `{type = value}` arrays

**⚠️ CRITICAL — Paymaster matches TOP-LEVEL instructions only:**
The paymaster does NOT inspect inner CPI (Cross-Program Invocation) calls. For Anchor programs:
- Account creation (system program) happens via internal CPI — do NOT add a separate system program instruction to your TOML
- Each variation should only list YOUR program's instruction
- Example: `InitializeGame` creates a PDA via Anchor's CPI to system program, but the transaction has only ONE top-level instruction (your program). The TOML must match that single instruction, not two.
- This is the #1 gotcha for Anchor programs using the paymaster

**Anchor discriminators:** First 8 bytes of `SHA256("global:<function_name>")`. Use the first byte for a simple `EqualTo` constraint:

```python
import hashlib
h = hashlib.sha256(b"global:my_function").digest()
first_byte = h[0]  # Use in: constraint = { EqualTo = [{ U8 = <first_byte> }] }
```

### Step 4: Submit to Fogo Team

Send your TOML config to the Fogo team through the agreed channel. They load it into the paymaster and restart/reload.

### Example: Full TOML for a Trading App

```toml
[[domains]]
domain = "https://sessions-example.fogo.io"
enable_session_management = true
enable_preflight_simulation = true

## Deposit
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

## Trade
[[domains.tx_variations]]
version = "v1"
name = "Trade"
max_gas_spend = 800000

# Optional ATA creation
[[domains.tx_variations.instructions]]
program = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
required = false
[[domains.tx_variations.instructions.data]]
start_byte = 0
data_type = "U8"
constraint = { EqualTo = [{ U8 = 1 }] }

# Load market
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
constraint = { EqualTo = [{ U8 = 10 }] }

# Place order
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
constraint = { EqualTo = [{ U8 = 27 }] }
```

### Validating Your Config

Fogo provides a CLI to validate transactions against your config:

```bash
# Install
cargo install fogo-paymaster --bin paymaster-tx-validator

# Validate a historical transaction
paymaster-tx-validator validate \
  --config config.toml \
  --rpc-url-http https://testnet.fogo.io \
  --transaction-hash <TRANSACTION_SIGNATURE>

# Validate from base64-encoded transaction
paymaster-tx-validator validate \
  --config config.toml \
  --rpc-url-http https://testnet.fogo.io \
  --transaction <BASE64_ENCODED_TX>

# Validate recent sponsor transactions against a new config
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

### Common Paymaster Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "domain is not registered" | Domain not in paymaster config | Contact Fogo team to register |
| "Transaction does not match any allowed variations" | Tx instructions don't match TOML | Check discriminators, account indices, program IDs |
| Paymaster 400 | Config mismatch | Validate with `paymaster-tx-validator` CLI |
| Paymaster 500 | Server-side issue (e.g., token price API) | Usually transient; retry or contact Fogo |

### Runbook Reference

Full paymaster runbook: https://dourolabs.notion.site/Paymaster-Runbook-2763e0276d9380268d5bde602d00f887

## Rust SDK Integration

### Installation

```toml
[dependencies]
anchor-lang = "0.31.1"
anchor-spl = "0.31.1"
fogo-sessions-sdk = { version = "0.7.5", features = ["anchor", "token-program"] }
# DO NOT manually add solana-program — comes from anchor-lang
```

### Core Pattern: Extract User from Signer or Session

```rust
use anchor_lang::prelude::*;
use fogo_sessions_sdk::session::Session;

#[program]
pub mod my_program {
    use super::*;

    pub fn my_instruction(ctx: Context<MyAccounts>) -> Result<()> {
        // Works for both direct wallet AND session key
        let user = Session::extract_user_from_signer_or_session(
            &ctx.accounts.signer_or_session,
            &crate::ID,
        ).map_err(ProgramError::from)?;

        // user is always the wallet pubkey regardless of signing method
        require_keys_eq!(ctx.accounts.some_resource.owner, user);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct MyAccounts<'info> {
    pub signer_or_session: Signer<'info>,
    // ... your accounts
}
```

### Token Transfer Pattern (Session-aware)

```rust
use anchor_lang::solana_program::program::invoke_signed;
use anchor_spl::token::{Mint, Token, TokenAccount};
use fogo_sessions_sdk::session::{is_session, Session};
use fogo_sessions_sdk::token::{instruction::transfer_checked, PROGRAM_SIGNER_SEED};

pub fn transfer_tokens(ctx: Context<TransferCtx>, amount: u64) -> Result<()> {
    let user = Session::extract_user_from_signer_or_session(
        &ctx.accounts.signer_or_session,
        &crate::ID,
    ).map_err(ProgramError::from)?;

    let instruction = transfer_checked(
        ctx.accounts.token_program.key,
        &ctx.accounts.user_token_account.key(),
        &ctx.accounts.mint.key(),
        &ctx.accounts.destination.key(),
        &ctx.accounts.signer_or_session.key(),
        ctx.accounts.program_signer.as_ref().map(|ai| ai.key()).as_ref(),
        amount,
        ctx.accounts.mint.decimals,
    )?;

    if is_session(&ctx.accounts.signer_or_session) {
        // Session: needs program signer PDA
        invoke_signed(
            &instruction,
            &ctx.accounts.to_account_infos(),
            &[&[PROGRAM_SIGNER_SEED, &[ctx.bumps.program_signer.unwrap()]]],
        )?;
    } else {
        // Direct wallet
        invoke(&instruction, &ctx.accounts.to_account_infos())?;
    }
    Ok(())
}

#[derive(Accounts)]
pub struct TransferCtx<'info> {
    pub signer_or_session: Signer<'info>,
    
    /// PDA signer for token CPIs — required for sessions, optional for wallets
    /// CHECK: PDA seeds validated
    #[account(seeds = [PROGRAM_SIGNER_SEED], bump)]
    pub program_signer: Option<AccountInfo<'info>>,
    
    #[account(mut, token::mint = mint)]
    pub user_token_account: Account<'info, TokenAccount>,
    pub mint: Account<'info, Mint>,
    #[account(mut, token::mint = mint)]
    pub destination: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}
```

### Key Constants

```rust
// Session Manager Program
pub const SESSION_MANAGER_ID: Pubkey = 
    solana_program::pubkey!("SesswvJ7puvAgpyqp7N8HnjNnvpnS8447tKNF3sPgbC");

// PDA seed for program signer (token transfers)
pub const PROGRAM_SIGNER_SEED: &[u8] = b"program_signer";
```

## Common Pitfalls

### 1. Wrong Provider Props
**Error**: Various — session won't establish, paymaster errors
**Fix**: Use `network`, `domain`, `rpc`, `paymaster`. NOT `sponsor`, `paymasterUrl`, `endpoint`.

### 2. Pubkey Type Mismatch
**Error**: `mismatched types: expected solana_program::pubkey::Pubkey, found anchor_lang::prelude::Pubkey`
**Fix**: Use `anchor-lang = "0.31.1"`, don't manually add `solana-program`.

### 3. Wrong Signer on Client
**Error**: Session validation fails
**Fix**: Pass `session.sessionPublicKey` as signer, NOT `session.walletPublicKey`.

### 4. Domain Mismatch
**Error**: "domain is not registered with the paymaster"
**Fix**: Domain in `FogoSessionProvider` must exactly match what's registered. In dev, use a registered domain like `sessions-example.fogo.io`.

### 5. Paymaster TOML Demands Extra Instructions (Anchor CPI)
**Error**: "Transaction does not match any allowed variations"
**Fix**: The paymaster only matches **top-level instructions**. Anchor handles account creation (system program) via internal CPI — it's NOT a separate instruction in the transaction. Remove any system program instruction requirements from your TOML. Each variation should only list your program's instruction.

### 6. Native FOGO in Sessions
**Error**: Sessions don't work with FOGO
**Fix**: Use Wrapped SOL (`NATIVE_MINT` = `So11111111111111111111111111111111111111112`), not native FOGO.

## Source Code & Resources

- **Sessions monorepo**: https://github.com/fogo-foundation/fogo-sessions
- **Sessions demo**: `apps/sessions-demo/` in monorepo
- **Rust SDK**: `packages/sessions-sdk-rs/`
- **React SDK**: `packages/sessions-sdk-react/`
- **Vite example**: https://github.com/fogo-foundation/sessions-example-vite
- **Fogo docs**: https://docs.fogo.io
- **NPM**: https://www.npmjs.com/package/@fogo/sessions-sdk-react
- **Crates.io**: https://crates.io/crates/fogo-sessions-sdk
