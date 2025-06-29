# Стратегия для агрессивного трейдера

import ta

class AggressiveFuturesStrategy:
    def __init__(self, params):
        self.body_threshold = params['CANDLE_BODY_THRESHOLD']
        self.volume_period = params['VOLUME_PERIOD']
        self.take_profit_percent = params['TAKE_PROFIT_PERCENT']
        self.stop_loss_percent = params['STOP_LOSS_PERCENT']
        self.position_size_percent = params['POSITION_SIZE_PERCENT']
        self.ma_length = params.get('MA_LENGTH', 50)
        self.use_trend = params.get('USE_TREND', True)
        self.trade_long = params.get('TRADE_LONG', True)
        self.trade_short = params.get('TRADE_SHORT', True)
        self.candle_history = []
        self.close_history = []

    def update_candle_history(self, candle):
        self.candle_history.append(candle)
        self.close_history.append(candle['close'])
        if len(self.candle_history) > max(self.volume_period, self.ma_length):
            self.candle_history.pop(0)
            self.close_history.pop(0)

    def get_ma(self):
        if len(self.close_history) < self.ma_length:
            return None
        return sum(self.close_history[-self.ma_length:]) / self.ma_length

    def analyze_candle(self, candle):
        body = abs(candle['close'] - candle['open']) / candle['open'] * 100
        direction = 'long' if candle['close'] > candle['open'] else 'short'
        avg_volume = sum(c['volume'] for c in self.candle_history[-self.volume_period:]) / max(1, min(len(self.candle_history), self.volume_period))
        ma = self.get_ma()
        trend_up = ma is not None and candle['close'] > ma
        trend_down = ma is not None and candle['close'] < ma
        return {
            'body': body,
            'direction': direction,
            'volume': candle['volume'],
            'avg_volume': avg_volume,
            'ma': ma,
            'trend_up': trend_up,
            'trend_down': trend_down
        }

    def check_entry_signal(self, analysis):
        if (
            analysis['body'] > self.body_threshold and
            analysis['volume'] > analysis['avg_volume']
        ):
            if self.use_trend:
                if analysis['direction'] == 'long' and self.trade_long and analysis['trend_up']:
                    return 'long'
                if analysis['direction'] == 'short' and self.trade_short and analysis['trend_down']:
                    return 'short'
            else:
                if analysis['direction'] == 'long' and self.trade_long:
                    return 'long'
                if analysis['direction'] == 'short' and self.trade_short:
                    return 'short'
        return None

    def calculate_position_size(self, balance, price):
        return (balance * self.position_size_percent / 100) / price

    def calculate_take_profit_price(self, entry_price, direction):
        if direction == 'long':
            return entry_price * (1 + self.take_profit_percent / 100)
        else:
            return entry_price * (1 - self.take_profit_percent / 100)

    def calculate_stop_loss_price(self, entry_price, direction):
        if direction == 'long':
            return entry_price * (1 - self.stop_loss_percent / 100)
        else:
            return entry_price * (1 + self.stop_loss_percent / 100)

    def check_exit_conditions(self, position, current_price):
        if position['direction'] == 'long':
            if current_price >= position['take_profit']:
                return True, 'take_profit'
            if current_price <= position['stop_loss']:
                return True, 'stop_loss'
        else:
            if current_price <= position['take_profit']:
                return True, 'take_profit'
            if current_price >= position['stop_loss']:
                return True, 'stop_loss'
        return False, None

    def calculate_pnl(self, position, current_price):
        if position['direction'] == 'long':
            return (current_price - position['entry_price']) * position['size']
        else:
            return (position['entry_price'] - current_price) * position['size']

    def log_signal(self, signal, analysis, balance):
        print(f"Сигнал: {signal}, Анализ: {analysis}, Баланс: {balance}")

    def log_position_opened(self, position):
        print(f"ПОЗИЦИЯ ОТКРЫТА: {position}")

    def log_position_closed(self, position, price, reason, pnl):
        print(f"ПОЗИЦИЯ ЗАКРЫТА: {position}, Цена: {price}, Причина: {reason}, PnL: {pnl}") 