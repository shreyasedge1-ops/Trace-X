import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YOUR_ETHERSCAN_API_KEY")
ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"

KNOWN_VASP_TAGS = {
    "0x28c6c06298d514db089934071355e5743bf21d60": {
        "entity": "Binance",
        "type": "Exchange Hot Wallet"
    }
}