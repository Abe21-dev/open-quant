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

## Step 1: Get all binary markets

Just query the API for all active binary markets.

## Step 2: Score and select best market

For each market, calculate three metrics:

**Spread:** `spread = yes_ask - yes_bid`, where `yes_ask = 100 - no_bid`

**Volume:** Just grab `volume_24h` from the market data

**Depth concentration:** `depth_concentration = depth_within_3cents_of_best / total_depth`

This tells you how much competition there is. Lower is better (more opportunity for you).

Then normalize each to 0-100 scale:

```
spread_score = ((spread - min_spread) / (max_spread - min_spread)) × 100
volume_score = ((volume_24h - min_volume) / (max_volume - min_volume)) × 100
competition_score = (1 - depth_concentration) × 100
```

Final composite score:

```
final_score = (spread_score × 0.5) + (volume_score × 0.3) + (competition_score × 0.2)
```

Pick the market with the highest `final_score`.

## Step 3: Choose Yes or No

Simple rule:

```
if yes_bid < 50:
    market_make_yes_contracts
else:
    market_make_no_contracts
```

This picks the cheaper side to minimize capital requirements.

## Step 4: Place orders and wait

Place your limit orders with 30-60 second expiration. Just wait for either fills or expiration.

## Step 5: Update orders

When expiration hits, fetch the current market data for your selected market. Get the new `best_bid` and `best_ask`, calculate new order prices (penny improvement if spread allows), and place fresh orders.

Important: Don't re-score all markets here. Stay with the same market and same contract type (Yes or No).

## Step 6: Repeat

Keep cycling through steps 4 and 5 until you hit position limits, need to close before resolution, or manually stop.

Only re-run the full scoring from Step 2 when you complete a round trip (both sides filled and you're flat) or when starting a new trading session.

Does this work better for you?
