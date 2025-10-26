import dotenv from "dotenv";
import minimist from "minimist";
import type {
  Event,
  Market,
  Candlestick,
  CreateOrderRequest,
} from "kalshi-typescript";
import {
  EventsApi,
  Configuration,
  MarketsApi,
  type GetEventResponse,
  PortfolioApi,
} from "kalshi-typescript";
import { getCandleStickData } from "./loader.js";
import { initialStrategy } from "./marketMaker.js";

dotenv.config();

export const HOUR = 60 * 60;
export const DAY = 24 * HOUR;

let myApiKey: string | undefined = process.env.API_KEY_ID;

const configuration = new Configuration({
  apiKey: process.env.API_KEY_ID ?? "",
  privateKeyPath: process.env.PRIVATE_KEY_PATH ?? "",
});

const eventInstance = new EventsApi(configuration);
export const marketInstance = new MarketsApi(configuration);
export const portfolioInstance = new PortfolioApi(configuration);

async function marketDataLoader(eventTicker: string) {
  // get market associated with a event
  const { status, data } = await eventInstance.getEvent(eventTicker, false);
  if (status != 200) throw new Error("Failed to get event data");

  let selectedMarket = data?.markets?.sort((a, b) => a.volume! - b.volume!)[0];
  if (!selectedMarket || !data.event) {
    throw Error("Invalid market or event data");
  }
  console.log(selectedMarket.ticker, selectedMarket.title);
  getCandleStickData(data.event, selectedMarket);
}

async function mm(eventTicker: string) {
  let { status, data } = await eventInstance.getEvent(eventTicker, false);
  if (status != 200) throw new Error("Failed to get event data");
  let event = data.event;
  let selectedMarket = data?.markets?.sort((a, b) => b.volume! - a.volume!)[0];
  if (!selectedMarket || !data.event) {
    throw Error("Invalid market or event data");
  }

  await initialStrategy(data.markets!);
}

async function main(mode: string, link?: string) {
  if (mode == "test") {
    await marketDataLoader(link ?? "KXNCAAFGAME-25OCT25TXAMLSU");
  } else if (mode == "mm") {
    await mm("KXNCAAFGAME-25OCT25TXAMLSU");
  }
}

let argv = minimist(process.argv.slice(2))["_"];
let mode;
if (argv.length != 0) {
  mode = argv[0] ?? "";
  console.log(argv, mode);
} else {
  mode = "test";
}
main(mode);
