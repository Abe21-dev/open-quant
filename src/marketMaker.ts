import { findSourceMap } from "module";
import { portfolioInstance, sleep, marketInstance, MINUTE } from "./index.js";
import type { Event, Market } from "kalshi-typescript";
import minimist from "minimist";
import chalk from "chalk";

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

interface IMarket {
  ticker: string;
  side: string;
  ask_price: number;
  bid_price: number;
}

function toAbstract(market: Market, side: "yes" | "no"): IMarket {
  return {
    ticker: market.ticker!,
    side: side,
    ask_price: side == "yes" ? market.yes_ask! : market.no_ask!,
    bid_price: side == "yes" ? market.yes_bid! : market.no_bid!,
  };
}

async function makeOrders(abstract: IMarket) {
  let curr_ask = abstract.ask_price - 1;
  let curr_bid = abstract.bid_price + 1;
  // prettier-ignore
  if (curr_ask <= curr_bid) {
    curr_ask = abstract.ask_price;
    curr_bid = abstract.bid_price;
  }
  // market ask and bid
  console.log(
    "Market Bid:",
    abstract.bid_price,
    "Market Ask:",
    abstract.ask_price
  );
  console.log(
    `Placing orders for ${abstract.ticker} | Side: ${abstract.side} | Spread $${curr_ask - curr_bid} |Bid: $${curr_bid} | Ask: $${curr_ask}`
  );

  // prettier-ignore
  const expiration_time = Math.floor((Date.now() / 1000) + (5 * MINUTE));

  let { status, data } = await portfolioInstance.createOrder({
    ticker: abstract.ticker,
    side: abstract.side == "yes" ? "yes" : "no",
    action: "sell",
    count: 1,
    type: "limit",
    yes_price: curr_ask,
    expiration_ts: expiration_time,
  });
  const getStatusColor = (status: string | undefined) => {
    if (status === "executed") {
      return chalk.green(status);
    } else if (status === "resting") {
      return chalk.yellow(status);
    }
    return chalk.white(status ?? "unknown");
  };

  console.log(
    `Status: ${getStatusColor(data?.order?.status)} | Side: ${data?.order?.side ?? "unknown"} | Action: ${data?.order?.action ?? "unknown"} | Price: $${data?.order?.side === "yes" ? (data?.order?.yes_price ?? "N/A") : (data?.order?.no_price ?? "N/A")} | ID: ${data?.order?.order_id?.slice(0, 8) ?? "unknown"}`
  );

  ({ status, data } = await portfolioInstance.createOrder({
    ticker: abstract.ticker,
    side: abstract.side == "yes" ? "yes" : "no",
    action: "buy",
    count: 1,
    type: "limit",
    yes_price: curr_bid,
    expiration_ts: expiration_time,
  }));

  console.log(
    `Status: ${getStatusColor(data?.order?.status)} | Side: ${data?.order?.side ?? "unknown"} | Action: ${data?.order?.action ?? "unknown"} | Price: $${data?.order?.side === "yes" ? (data?.order?.yes_price ?? "N/A") : (data?.order?.no_price ?? "N/A")} | ID: ${data?.order?.order_id?.slice(0, 8) ?? "unknown"}`
  );
}

async function getUpdateAbstractMarkets(
  abstractMarkets: IMarket[]
): Promise<IMarket[]> {
  let first = await marketInstance.getMarket(abstractMarkets[0]?.ticker!);
  let firstMarket = first.data.market;

  return [toAbstract(firstMarket!, "yes"), toAbstract(firstMarket!, "no")];
}

async function tradingLoop(abstractMarkets: IMarket[]) {
  let orders = [];
  let updateAbstractMarkets: IMarket[] = [];
  let contractCount = 0;

  while (true) {
    for (const abs of abstractMarkets) {
      orders.push(makeOrders(abs));
      contractCount += 1;
    }
    await sleep(5 * 60 * 1000);
    console.log("Updating markets...");
    console.log(`Total contracts traded so far: ${contractCount}`);
    updateAbstractMarkets = await getUpdateAbstractMarkets(abstractMarkets);
    abstractMarkets = updateAbstractMarkets;
    updateAbstractMarkets = [];
  }
}

export async function initialStrategy(markets: Market) {
  // split into yes and no markets
  let firstMarket = markets;

  const { status, data } = await marketInstance.getMarketOrderbook(
    firstMarket?.ticker!
  );

  const absMarket: IMarket[] = [
    toAbstract(firstMarket!, "yes"),
    toAbstract(firstMarket!, "no"),
  ];
  try {
    tradingLoop(absMarket);
  } catch (error) {
    console.error("something went wrong");
  }
}
