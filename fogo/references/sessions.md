# Fogo Sessions Integration Reference

Complete guide for integrating Fogo Sessions into applications.

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
- Integrating with existing Solana wallet infrastructure

### Hybrid Approach

Many apps support both:
1. Fogo Sessions as default for new/casual users
2. Traditional wallet connect for power users

```tsx
// Offer both options
<SessionButton />
<WalletMultiButton /> {/* from @solana/wallet-adapter-react-ui */}
```

## Overview

Fogo Sessions combine account abstraction with paymasters to enable:
- Gasless transactions (users don't pay fees)
- No individual transaction signing
- Robust user protections (spending limits, domain verification)
- Consistent wallet UX across Fogo apps

**Important**: Sessions only work with SPL tokens, not native FOGO. Native FOGO is for paymasters and low-level primitives only.

## React SDK

Package: `@fogo/sessions-sdk-react`

### FogoSessionProvider Props

| Prop | Type | Description |
|------|------|-------------|
| `sponsor` | string | Paymaster sponsor public key. Use `8HnaXmgFJbvvJxSdjeNyWwMXZb85E35NM4XNg6rxuw3w` |
| `paymasterUrl` | string | Paymaster URL. Use `https://sessions-example.fogo.io/paymaster` |
| `domain` | string \| undefined | Override domain for dev environments. Use `undefined` in production |
| `endpoint` | string | Fogo RPC URL (`https://testnet.fogo.io/` or `https://mainnet.fogo.io`) |
| `tokens` | string[] | Array of token mint addresses the app may request permissions for |
| `defaultRequestedLimits` | Record<string, bigint> | Map of token mints to default requested amounts |

### SessionButton Component

Adds connect button with wallet management panel when connected.

**Props:**
- `requestedLimits`: Optional override for `defaultRequestedLimits` when this button is clicked

### useSession Hook

Returns discriminated union based on session state.

#### When Not Established

```typescript
session.type === SessionStateType.NotEstablished
session.establish(requestedLimits?) // Start session flow
```

#### When Established

Use `isEstablished(session)` helper to check.

```typescript
session.walletPublicKey    // Wallet that created session
session.sessionPublicKey   // Session public key
session.payer              // Paymaster sponsor public key
session.sendTransaction(instructions: TransactionInstruction[]) // Send tx
session.endSession()       // Destroy session
```

## Full Example

```tsx
import { ReactNode } from 'react';
import { FogoSessionProvider, SessionButton, useSession, isEstablished, SessionStateType } from '@fogo/sessions-sdk-react';
import { NATIVE_MINT } from '@solana/spl-token';
import { TransactionInstruction, PublicKey } from '@solana/web3.js';

// Layout wrapper
export function Layout({ children }: { children: ReactNode }) {
  return (
    <FogoSessionProvider
      sponsor="8HnaXmgFJbvvJxSdjeNyWwMXZb85E35NM4XNg6rxuw3w"
      paymasterUrl="https://sessions-example.fogo.io/paymaster"
      domain={process.env.NODE_ENV === "production" ? undefined : "https://localhost:3000"}
      endpoint="https://testnet.fogo.io/"
      tokens={[NATIVE_MINT.toBase58()]}
      defaultRequestedLimits={{
        [NATIVE_MINT.toBase58()]: 1_500_000_000n, // 1.5 FOGO in lamports
      }}
    >
      <header>
        <h1>My Fogo App</h1>
        <SessionButton />
      </header>
      <main>{children}</main>
    </FogoSessionProvider>
  );
}

// Component using session
export function TradingPanel() {
  const session = useSession();

  async function executeTrade() {
    if (!isEstablished(session)) return;
    
    // Build your transaction instructions
    const instructions: TransactionInstruction[] = [
      // Your program instructions here
    ];
    
    try {
      await session.sendTransaction(instructions);
      console.log('Trade executed!');
    } catch (error) {
      console.error('Trade failed:', error);
    }
  }

  if (session.type === SessionStateType.NotEstablished) {
    return (
      <div>
        <p>Connect to start trading</p>
        <button onClick={() => session.establish()}>
          Connect Wallet
        </button>
      </div>
    );
  }

  if (isEstablished(session)) {
    return (
      <div>
        <p>Connected: {session.walletPublicKey.toBase58()}</p>
        <button onClick={executeTrade}>Execute Trade</button>
        <button onClick={session.endSession}>Disconnect</button>
      </div>
    );
  }

  return <p>Loading...</p>;
}
```

## User Protection Features

### Domain Verification

The `domain` field in the intent message must match the origin domain. This prevents XSS attacks where users are phished into signing sessions for malicious apps.

- In production: Set `domain={undefined}` to use actual origin
- In development: Override with your dev URL

### Spending Limits

Sessions can be limited or unlimited:
- **Limited**: Specify max tokens the app can interact with
- **Unlimited**: No restrictions (for trusted apps)

Users can explore new apps with limited sessions without risking full wallet.

### Session Expiry

Sessions expire and must be renewed. The SDK handles renewal flows automatically through the SessionButton panel.

## Paymaster Economics

Currently using centralized paymasters. Economics and limitations are under active development.

Current public paymaster:
- Sponsor: `8HnaXmgFJbvvJxSdjeNyWwMXZb85E35NM4XNg6rxuw3w`
- URL: `https://sessions-example.fogo.io/paymaster`

Public paymasters with different economics coming soon.
