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

dotenv.config();

const HOUR = 60 * 60;
const DAY = 24 * HOUR;

let myApiKey: string | undefined = process.env.API_KEY_ID;

const configuration = new Configuration({
  apiKey: process.env.API_KEY_ID ?? "",
  privateKeyPath: process.env.PRIVATE_KEY_PATH ?? "",
});

const eventInstance = new EventsApi(configuration);
const marketInstance = new MarketsApi(configuration);
const portfolioInstance = new PortfolioApi(configuration);
const chars = {
  full: "█", // Full block
  empty: "░", // Light shade
  partial: "▓", // Dark shade
};

function throwCustomError(msg: string) {
  throw Error(msg);
}

async function getCandleStickData(event: Event, market: Market) {
  // get start timestamp
  let startTimeStr = market!.open_time!;
  let endTimeStr = market!.expiration_time!;
  const startTime = Math.floor(Date.now() / 1000 - 5 * DAY);
  const endTime = Date.now() / 1000;

  // Logging info
  console.log();
  console.log("Loading Candle stick data:");
  process.stdout.write(`${chars.empty.repeat(100)}`);
  let percentComplete = 0;
  let completeJobs = 0;
  let totalJobAmount = (endTime - startTime) / HOUR;

  const loadingBar = async () => {
    const percentage = (completeJobs / totalJobAmount) * 100;
    if (percentage - percentComplete >= 1) {
      percentComplete = percentage;
      process.stdout.write(`\r${chars.full.repeat(Math.floor(percentage))}`);
    }
  };

  // collect market data
  const marketData = [];

  const getOHLCData = async (
    startTs: number,
    endTS: number
  ): Promise<Candlestick[] | undefined> => {
    const { status, data } = await marketInstance.getMarketCandlesticks(
      event.series_ticker!,
      market.ticker!,
      startTs,
      endTS,
      "1"
    );

    if (status != 200) throw new Error("Failed to get candlestick data");
    completeJobs++;
    loadingBar();
    return data.candlesticks;
  };

  let dataFetches: Promise<Candlestick[] | undefined>[] = [];
  let results: Candlestick[] = [];
  for (let i = startTime; i < endTime; i += HOUR) {
    dataFetches.push(getOHLCData(i, i + HOUR));
    if (dataFetches.length == 20) {
      let tempRes = (await Promise.all(dataFetches))
        .filter((data) => data !== undefined)
        .flat();
      results = results.concat(tempRes);
      dataFetches = [];
      await new Promise((r) => setTimeout(r, 1000));
    }
  }
  console.log();
  console.log(results[0]);
}

async function marketDataLoader(eventTicker: string) {
  // get market associated with a event
  const { status, data } = await eventInstance.getEvent(eventTicker, false);
  if (status != 200) throw new Error("Failed to get event data");
  if (!data.markets || !data.event) {
    throw Error("Invalid market or event data");
  }

  let marketWithHighestVolume = data.markets?.sort(
    (a, b) => a.volume! - b.volume!
  )[0];

  let allMarkets = data.markets;

  console.log(marketWithHighestVolume);
}

async function main(link?: string) {
  await marketDataLoader(link ?? "KXNCAAFGAME-25OCT25TXAMLSU");
}

let past_link = "";

main();
