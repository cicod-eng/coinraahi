#!/usr/bin/env python3
"""Fetch current USDT premium data for coinraahi.com.

Pulls three sources and prints:
  1. A ready-to-paste HTML <table> snippet for
     /crypto/stablecoins/usdt-premium-india/
  2. The raw numbers, so you can also update the page's fallback
     reference rate (REF = ...) in the inline script.

Sources (all public, no keys):
  - open.er-api.com  -> USD/INR foreign-exchange reference
  - api.wazirx.com   -> USDT/INR last trade on WazirX
  - api.coingecko.com -> USDT/USD (peg sanity check)

Usage:
  python3 fetch-premium.py
"""
import json
import urllib.request
from datetime import datetime, timezone


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "coinraahi/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def main():
    # 1. USD/INR reference (forex)
    fx = get_json("https://open.er-api.com/v6/latest/USD")
    usd_inr = fx["rates"]["INR"]
    fx_updated = fx.get("time_last_update_utc", "?")

    # 2. WazirX USDT/INR last trade
    tickers = get_json("https://api.wazirx.com/sapi/v1/tickers/24hr")
    usdt_inr = None
    for t in tickers:
        if t.get("symbol") == "usdtinr":
            usdt_inr = float(t["lastPrice"])
            break

    # 3. CoinGecko USDT/USD (peg sanity)
    cg = get_json("https://api.coingecko.com/api/v3/simple/price"
                  "?ids=tether&vs_currencies=usd")
    usdt_usd = cg["tether"]["usd"]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print("=" * 60)
    print(f"USD/INR reference : {usd_inr:.2f}  (forex, {fx_updated})")
    if usdt_inr is not None:
        premium = (usdt_inr / usd_inr - 1) * 100
        print(f"WazirX USDT/INR    : {usdt_inr:.2f}")
        print(f"USDT premium       : {premium:+.2f}%")
    else:
        premium = None
        print("WazirX USDT/INR    : not found (symbol may have changed)")
    print(f"USDT/USD peg       : {usdt_usd:.6f}")
    print("=" * 60)

    if usdt_inr is not None:
        print("\nPaste this <table> into /crypto/stablecoins/usdt-premium-india/:")
        print(f"""        <tr>
          <td>Official USD/INR reference rate</td>
          <td>₹{usd_inr:.2f}</td>
          <td>{fx_updated[:11]}</td>
          <td>open.er-api.com (forex)</td>
        </tr>
        <tr>
          <td>USDT/INR on WazirX (last trade)</td>
          <td>₹{usdt_inr:.2f}</td>
          <td>{today}</td>
          <td>WazirX public ticker</td>
        </tr>
        <tr>
          <td><strong>USDT premium over USD/INR</strong></td>
          <td class="warn"><strong>{premium:+.1f}%</strong></td>
          <td>&mdash;</td>
          <td>calculated</td>
        </tr>""")
        print(f'\nAlso update the page fallback:  var REF = {usd_inr:.2f};')


if __name__ == "__main__":
    main()
