import asyncio
import websockets
import json
from pump_fun import buy  # Assuming the `buy` function is implemented
from config import *

# WebSocket URI for Pump Portal
PUMP_PORTAL_URI = "wss://pumpportal.fun/api/data"

# Target Wallet Address to Monitor
TARGET_WALLET = "FLgoysyf6DfbjphH7mmBcezjcVxQ5y943K4K3uzGJHWn"  # Replace with the wallet address you want to monitor

# Retry Parameters for `snipe_cycle`
MAX_RETRIES = 100  # Max number of retries per token
RETRY_DELAY = 0.01  # Delay between retries in seconds


# Function: Snipe with No Retry Cycle
async def snipe_nocycle():
    async with websockets.connect(PUMP_PORTAL_URI) as websocket:
        # Subscribe to events for the target wallet address
        subscribe_payload = {
            "method": "subscribeAccountTrade",
            "keys": [TARGET_WALLET],
        }
        await websocket.send(json.dumps(subscribe_payload))
        print(f"[snipe_nocycle] Subscribed to events for wallet: {TARGET_WALLET}")

        # Listen for messages from the WebSocket
        async for message in websocket:
            event_data = json.loads(message)
            print("[snipe_nocycle] Received event:", event_data)

            # Check if the event is a new token creation
            if event_data.get("txType") == "create":
                mint_str = event_data.get("mint")
                print(f"[snipe_nocycle] New token detected! Mint address: {mint_str}")

                # Attempt to buy the new token (single transaction attempt)
                try:
                    confirmed = buy(mint_str, sol_in=0.02, slippage=25)  # Adjust `sol_in` and `slippage` as needed
                    if confirmed:
                        print(f"[snipe_nocycle] Successfully bought token: {mint_str}")
                    else:
                        print(f"[snipe_nocycle] Failed to buy token: {mint_str}")
                except Exception as e:
                    print(f"[snipe_nocycle] Error while buying token {mint_str}: {e}")
# Function: Snipe with Retry Cycle
async def snipe_cycle():
    async with websockets.connect(PUMP_PORTAL_URI) as websocket:
        # Subscribe to events for the target wallet address
        subscribe_payload = {
            "method": "subscribeAccountTrade",
            "keys": [TARGET_WALLET],
        }
        await websocket.send(json.dumps(subscribe_payload))
        print(f"[snipe_cycle] Subscribed to events for wallet: {TARGET_WALLET}")

        # Listen for messages from the WebSocket
        async for message in websocket:
            event_data = json.loads(message)
            print("[snipe_cycle] Received event:", event_data)

            # Check if the event is a new token creation
            if event_data.get("txType") == "create":
                mint_str = event_data.get("mint")
                print(f"[snipe_cycle] New token detected! Mint address: {mint_str}")

                # Attempt to buy the new token with retry logic
                success = False
                attempt = 0

                while not success and attempt < MAX_RETRIES:
                    try:
                        # Attempt to buy the token
                        confirmed = buy(mint_str, sol_in=0.02, slippage=25)  # Adjust `sol_in` and `slippage` as needed
                        if confirmed:
                            print(f"[snipe_cycle] Successfully bought token: {mint_str}")
                            success = True  # Exit the retry loop
                        else:
                            print(f"[snipe_cycle] Failed to buy token (attempt {attempt + 1}). Retrying...")
                    except Exception as e:
                        print(f"[snipe_cycle] Error on attempt {attempt + 1}: {e}")

                    # Increment attempt count and wait before retrying
                    attempt += 1
                    await asyncio.sleep(RETRY_DELAY)

                if not success:
                    print(f"[snipe_cycle] Max retries reached. Failed to buy token: {mint_str}")


asyncio.run(snipe_cycle())