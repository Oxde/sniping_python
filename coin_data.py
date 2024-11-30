from solders.pubkey import Pubkey  # type: ignore
from spl.token.instructions import get_associated_token_address
from construct import Padding, Struct, Int64ul, Flag
from config import client
from constants import PUMP_FUN_PROGRAM

def get_virtual_reserves(bonding_curve: Pubkey):
    bonding_curve_struct = Struct(
        Padding(8),
        "virtualTokenReserves" / Int64ul,
        "virtualSolReserves" / Int64ul,
        "realTokenReserves" / Int64ul,
        "realSolReserves" / Int64ul,
        "tokenTotalSupply" / Int64ul,
        "complete" / Flag
    )
    
    try:
        account_info = client.get_account_info(bonding_curve)
        data = account_info.value.data
        parsed_data = bonding_curve_struct.parse(data)
        return parsed_data
    except Exception:
        return None

def derive_bonding_curve_accounts(mint_str: str):
    try:
        mint = Pubkey.from_string(mint_str)
        bonding_curve, _ = Pubkey.find_program_address(
            ["bonding-curve".encode(), bytes(mint)],
            PUMP_FUN_PROGRAM
        )
        associated_bonding_curve = get_associated_token_address(bonding_curve, mint)
        return bonding_curve, associated_bonding_curve
    except Exception:
        return None, None

def get_coin_data(mint_str: str):
    """
    Fetch bonding curve and virtual reserves for a given mint.
    """

    print(f"[get_coin_data] Fetching coin data for mint: {mint_str}")

    # Derive bonding curve accounts
    bonding_curve, associated_bonding_curve = derive_bonding_curve_accounts(mint_str)
    print(f"[get_coin_data] Derived bonding curve: {bonding_curve}, associated bonding curve: {associated_bonding_curve}")

    if bonding_curve is None or associated_bonding_curve is None:
        print("[get_coin_data] Failed to derive bonding curve accounts.")
        return None

    # Fetch virtual reserves
    print(f"[get_coin_data] Fetching virtual reserves for bonding curve: {bonding_curve}")
    virtual_reserves = get_virtual_reserves(bonding_curve)

    if virtual_reserves is None:
        print("[get_coin_data] Failed to fetch virtual reserves.")
        return None

    print(f"[get_coin_data] Virtual reserves fetched: {virtual_reserves}")

    # Attempt to parse virtual reserves
    try:
        virtual_token_reserves = int(virtual_reserves.virtualTokenReserves)
        virtual_sol_reserves = int(virtual_reserves.virtualSolReserves)
        token_total_supply = int(virtual_reserves.tokenTotalSupply)
        complete = bool(virtual_reserves.complete)

        print(f"[get_coin_data] Parsed reserves: virtual_token_reserves={virtual_token_reserves}, "
              f"virtual_sol_reserves={virtual_sol_reserves}, token_total_supply={token_total_supply}, complete={complete}")

        return {
            "mint": mint_str,
            "bonding_curve": str(bonding_curve),
            "associated_bonding_curve": str(associated_bonding_curve),
            "virtual_token_reserves": virtual_token_reserves,
            "virtual_sol_reserves": virtual_sol_reserves,
            "token_total_supply": token_total_supply,
            "complete": complete
        }

    except Exception as e:
        print(f"[get_coin_data] Error while parsing virtual reserves: {e}")
        return None
