import json
import os
from typing import Dict, List

STATE_FILE = 'bot_state.json'

# Пример структуры состояния
state = {
    'balance': 0.0,
    'open_positions': {},  # {symbol: {direction, entry_price, size, ...}}
    'leverage': {},        # {symbol: value}
    'symbols': [],
    'risk_profile': 'moderate',
}

def save_state():
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_state():
    global state
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)

def get_balance() -> float:
    return state.get('balance', 0.0)

def set_balance(value: float):
    state['balance'] = value
    save_state()

def get_open_positions() -> Dict:
    return state.get('open_positions', {})

def set_open_positions(positions: Dict):
    state['open_positions'] = positions
    save_state()

def close_position(symbol: str):
    if symbol in state['open_positions']:
        del state['open_positions'][symbol]
        save_state()

def get_leverage(symbol: str) -> int:
    return state.get('leverage', {}).get(symbol, 0)

def set_leverage(symbol: str, value: int):
    if 'leverage' not in state:
        state['leverage'] = {}
    state['leverage'][symbol] = value
    save_state()

def get_symbols() -> List[str]:
    return state.get('symbols', [])

def set_symbols(symbols: List[str]):
    state['symbols'] = symbols
    save_state()

def get_risk_profile() -> str:
    return state.get('risk_profile', 'moderate')

def set_risk_profile(profile: str):
    state['risk_profile'] = profile
    save_state()

# Инициализация при импорте
load_state() 