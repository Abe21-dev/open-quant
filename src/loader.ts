import type { Event, Market, Candlestick } from "kalshi-typescript";
import { HOUR, DAY, marketInstance } from "./index.js";

const chars = {
  full: "█", // Full block
  empty: "░", // Light shade
  partial: "▓", // Dark shade
};

export async function getCandleStickData(event: Event, market: Market) {
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
