import { findSourceMap } from "module";
import { portfolioInstance, marketInstance } from "./index.js";
import type { Event, Market } from "kalshi-typescript";

async function simpleOrder(market: Market, event: Event) {
  const { status, data } = await portfolioInstance.createOrder({
    ticker: market.ticker!,
    side: "yes",
    action: "sell",
    count: 1,
    type: "market",
    yes_price: 87,
  });
  console.log(status);
  console.log(data);
}

export async function initialStrategy(markets: Market[]) {
  // split into yes and no markets
  let firstMarket = markets[0];
  let secondMarket = markets[1];

  const { status, data } = await marketInstance.getMarketOrderbook(
    firstMarket?.ticker!
  );
  console.log(firstMarket?.yes_ask);
}
