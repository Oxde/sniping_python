from solana.rpc.api import Client
from solders.keypair import Keypair #type: ignore

PRIV_KEY = "5afm39KmerbXfvVC6qaNUvsjjwtwTNsX4gv6VcDzjmY5VfTSpkKzHkNuBNAJ1Ns1KWXy4isJ8vCeMVFchLTXg1w1"
RPC = "https://mainnet.helius-rpc.com/?api-key=92e617b8-3742-4094-8a15-5c66b6c75f32"
UNIT_BUDGET =  100_000
UNIT_PRICE =  150_000_000
SOL_AMOUNT = 0.02
BUY_SLIPPAGE = 100
SELL_SLIPAGE = 100
client = Client(RPC)
payer_keypair = Keypair.from_base58_string(PRIV_KEY)
