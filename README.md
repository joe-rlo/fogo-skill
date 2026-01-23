# Fogo Skill for Claude Code

A [Claude Code](https://claude.ai/code) skill for building and deploying applications on the [Fogo](https://fogo.io) blockchain.

## What is this?

This skill extends Claude Code with specialized knowledge for Fogo development, including:

- 🚀 Deploying Solana programs to Fogo (full SVM compatibility)
- ⚡ Configuring Solana CLI and Anchor for Fogo endpoints
- 🔐 Integrating Fogo Sessions for gasless, no-approve UX
- 🪙 Working with FOGO and fUSD tokens
- 🌐 Connecting to testnet and mainnet RPCs

## Installation

### Claude.ai

1. Download the latest `fogo.skill` from [Releases](../../releases)
2. Go to **Settings → Capabilities → Skills**
3. Click **Upload skill** and select the downloaded file

### Claude Code

Copy the `fogo` folder to your personal skills directory:

```bash
# Clone this repo
git clone https://github.com/joe-rlo/fogo-skill.git

# Copy to Claude Code skills folder
cp -r fogo-skill/fogo ~/.claude/skills/
```

Or install directly:

```bash
mkdir -p ~/.claude/skills
cp -r fogo ~/.claude/skills/
```

## Usage

Once installed, Claude Code will automatically use this skill when you ask about Fogo development. Try prompts like:

- "Deploy my Anchor program to Fogo testnet"
- "Set up Fogo Sessions in my React app"
- "How do I get testnet FOGO tokens?"
- "Configure my project for Fogo mainnet"

## Quick Reference

### RPC Endpoints

| Network | URL |
|---------|-----|
| Mainnet | `https://mainnet.fogo.io` |
| Testnet | `https://testnet.fogo.io` |

### Key Resources

- 📖 [Fogo Docs](https://docs.fogo.io)
- 🚰 [Testnet Faucet](https://faucet.fogo.io)
- 🔍 [Fogoscan Explorer](https://fogoscan.com)

## Skill Contents

```
fogo/
├── SKILL.md              # Main skill instructions
└── references/
    ├── sessions.md       # Fogo Sessions integration guide
    └── fluxrpc.md        # FluxRPC high-performance RPC docs
```

## Building from Source

If you want to modify the skill:

1. Edit files in the `fogo/` directory
2. Rebuild the package:
   ```bash
   python build.py
   ```

This creates a new `fogo.skill` file ready for installation.

## Links

- [Fogo Documentation](https://docs.fogo.io)
- [Fogo Sessions Example (Next.js)](https://github.com/fogo-foundation/sessions-example)
- [Fogo Sessions Example (Vite)](https://github.com/fogo-foundation/sessions-example-vite)
- [Claude Code](https://claude.ai/code)

## License

MIT
