# Strategy

Outline of the various market making strategies to follow.

## Phase 0 - Trial Period Strategy

Initial focus on binary markets with wide spreads that update frequently. Sports category is the logical starting point.

### Reasons for Avoiding Multiple Outcome Markets

**Multiple outcome markets (e.g. 3+ candidate elections):**
- Only one outcome wins, all others resolve to $0
- Risk of unbalanced inventory across outcomes
- If you accumulate shorts on multiple candidates and any wins, you owe $1 per contract
- Example: Short 10 contracts of Candidate A at 46¢, Short 10 of Candidate B at 36¢
  - If A wins: lose $5.40 on A shorts, gain $3.60 on B shorts, net loss $1.80
  - Directional exposure accumulates without clear hedging mechanism
- Requires active cross-contract inventory management
- Higher complexity, higher risk for beginners

**Cumulative outcome markets (e.g. "event before date X"):**
- Contracts have logical ordering that must be maintained
- Price relationships create arbitrage opportunities
- Mismanaged positions can lock in guaranteed losses
- Requires monitoring multiple related contracts simultaneously

### Binary Market Advantages

- Yes and No are perfect opposites (Yes + No = $1)
- Short Yes = Long No (natural hedge)
- Simpler inventory management
- Lower risk of catastrophic directional exposure
- Easier to calculate maximum loss

## Core Market Making Strategy

### Basic Mechanics

**Objective:** Provide liquidity by posting simultaneous buy and sell orders, profiting from the spread.

**Approach:**
1. Identify current best bid and best ask
2. Place limit orders with penny improvement:
   - Bid: current_best_bid + $0.01
   - Ask: current_best_ask - $0.01
3. Set short expiration time (30-60 seconds)
4. Wait for fills or expiration
5. Update orders based on new market conditions
6. Repeat

**Example:**
- Current market: 30¢ bid / 70¢ ask
- Your orders: 31¢ bid / 69¢ ask
- Potential spread: 38¢ per completed round trip