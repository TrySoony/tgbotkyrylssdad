import ccxt
import asyncio
import logging
from datetime import datetime
from config import *
from strategy import AggressiveFuturesStrategy
from notifications import send_trade_notification

class AggressiveFuturesTrader:
    def __init__(self):
        self.logger = logging.getLogger("trader")
        self.exchange = None
        self.strategies = {}
        self.current_positions = {}
        self.daily_trades = 0
        self.daily_pnl = 0
        self.initial_balance = INITIAL_BALANCE
        self.current_balance = INITIAL_BALANCE
        self.session_start_time = datetime.now()
        self.running = False
        self.symbols = []
        self._task = None

    def setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('trading.log', encoding='utf-8')
            ]
        )

    def setup_exchange(self):
        try:
            self.exchange = ccxt.bybit({
                'apiKey': API_KEY,
                'secret': API_SECRET,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
        except Exception as e:
            self.logger.error(f"Ошибка инициализации биржи: {e}")
            self.exchange = None

    def get_symbols(self):
        if self.exchange is None:
            self.setup_exchange()
        if SYMBOLS:
            return SYMBOLS
        try:
            markets = self.exchange.load_markets()
            self.logger.info(f"Доступные рынки: {list(markets.keys())}")
            return [s for s in markets if s.endswith('/USDT') and markets[s]['future']]
        except Exception as e:
            self.logger.error(f"Ошибка получения списка пар: {e}")
            return ["BTC/USDT"]

    def get_balance(self):
        try:
            if DEMO_MODE:
                return self.current_balance
            if self.exchange is None:
                self.setup_exchange()
            if self.exchange is None:
                raise Exception("Биржа не инициализирована!")
            
            # Получаем баланс фьючерсного аккаунта
            balance = self.exchange.fetch_balance({'type': 'future'})
            return float(balance['USDT']['free'])
        except Exception as e:
            self.logger.error(f"Ошибка получения баланса: {e}")
            return self.current_balance

    def get_current_price(self, symbol):
        try:
            if self.exchange is None:
                self.setup_exchange()
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            self.logger.error(f"Ошибка получения цены {symbol}: {e}")
            return 0

    def get_ohlcv_data(self, symbol):
        try:
            if self.exchange is None:
                self.setup_exchange()
            ohlcv = self.exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=max(VOLUME_PERIOD, MA_LENGTH, 100))
            return ohlcv
        except Exception as e:
            self.logger.error(f"Ошибка получения OHLCV {symbol}: {e}")
            return []

    def open_position(self, symbol, direction, entry_price, size):
        try:
            if not ENABLE_TRADING:
                self.logger.info(f"Демо-открытие позиции: {direction} {symbol}")
                return True
            if self.exchange is None:
                self.setup_exchange()
            
            # Устанавливаем плечо перед открытием позиции и получаем его значение
            actual_leverage = self.setup_leverage(symbol)
            
            # Проверяем баланс перед открытием позиции с учётом реального плеча
            balance = self.get_balance()
            required_margin = (size * entry_price) / actual_leverage
            if required_margin > balance:
                self.logger.warning(f"Недостаточно баланса для {symbol}: требуется {required_margin:.2f}, доступно {balance:.2f} (плечо x{actual_leverage})")
                return False
            
            side = 'buy' if direction == 'long' else 'sell'
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=size,
                params={
                    'reduce_only': False,
                    'type': 'future'
                }
            )
            self.logger.info(f"Позиция открыта: {order['id']} {symbol} с плечом x{actual_leverage}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка открытия позиции {symbol}: {e}")
            return False

    def close_position(self, symbol, direction, size):
        try:
            if not ENABLE_TRADING:
                self.logger.info(f"Демо-закрытие позиции: {direction} {symbol}")
                return True
            if self.exchange is None:
                self.setup_exchange()
            side = 'sell' if direction == 'long' else 'buy'
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=size,
                params={
                    'reduce_only': True,
                    'type': 'future'
                }
            )
            self.logger.info(f"Позиция закрыта: {order['id']} {symbol}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка закрытия позиции {symbol}: {e}")
            return False

    def check_safety_limits(self):
        if self.daily_trades >= MAX_DAILY_TRADES:
            self.logger.warning(f"Достигнут лимит сделок в день: {MAX_DAILY_TRADES}")
            return False
        if self.daily_pnl < -MAX_DAILY_LOSS:
            self.logger.warning(f"Достигнут лимит дневного убытка: {MAX_DAILY_LOSS}%")
            return False
        current_balance = self.get_balance()
        if current_balance < self.initial_balance * (1 - EMERGENCY_STOP_LOSS / 100):
            self.logger.error(f"ЭКСТРЕННЫЙ СТОП: Убыток превысил {EMERGENCY_STOP_LOSS}%")
            return False
        return True

    def update_daily_stats(self, pnl):
        self.daily_trades += 1
        self.daily_pnl += pnl
        if datetime.now().date() > self.session_start_time.date():
            self.daily_trades = 0
            self.daily_pnl = 0
            self.session_start_time = datetime.now()

    def setup_leverage(self, symbol):
        """Установка максимального плеча для торговой пары."""
        try:
            if self.exchange is None:
                self.setup_exchange()
            
            # Загружаем рынки если они не загружены
            if not hasattr(self.exchange, 'markets') or not self.exchange.markets:
                self.exchange.load_markets()
            
            # Получаем информацию о рынке для определения максимального плеча
            market = self.exchange.market(symbol)
            
            # Проверяем, что это фьючерсный контракт
            if market.get('type') != 'swap' and market.get('type') != 'future':
                self.logger.warning(f"{symbol} не является фьючерсным контрактом, пропускаем установку плеча")
                return LEVERAGE
            
            # Получаем максимальное плечо
            max_leverage = market.get('limits', {}).get('leverage', {}).get('max', LEVERAGE)
            
            # Устанавливаем максимальное плечо
            self.exchange.set_leverage(max_leverage, symbol)
            self.logger.info(f"Установлено плечо x{max_leverage} для {symbol}")
            return max_leverage
        except Exception as e:
            self.logger.error(f"Ошибка установки плеча для {symbol}: {e}")
            # В случае ошибки используем значение по умолчанию
            try:
                self.exchange.set_leverage(LEVERAGE, symbol)
                self.logger.info(f"Установлено плечо по умолчанию x{LEVERAGE} для {symbol}")
                return LEVERAGE
            except Exception as e2:
                self.logger.error(f"Не удалось установить плечо для {symbol}: {e2}")
                return LEVERAGE

    def setup_all_leverages(self):
        """Установка плеча для всех торговых пар."""
        for symbol in self.symbols:
            self.setup_leverage(symbol)

    async def run_trading_cycle(self):
        self.logger.info("Запуск торгового цикла...")
        self.setup_logging()
        self.setup_exchange()
        self.symbols = self.get_symbols()
        self.logger.info(f"Торгуемые пары: {self.symbols}")
        
        # Устанавливаем плечо для всех пар
        self.setup_all_leverages()
        
        self.strategies = {symbol: AggressiveFuturesStrategy({
            'CANDLE_BODY_THRESHOLD': CANDLE_BODY_THRESHOLD,
            'VOLUME_PERIOD': VOLUME_PERIOD,
            'TAKE_PROFIT_PERCENT': TAKE_PROFIT_PERCENT,
            'STOP_LOSS_PERCENT': STOP_LOSS_PERCENT,
            'POSITION_SIZE_PERCENT': POSITION_SIZE_PERCENT,
            'MA_LENGTH': MA_LENGTH,
            'USE_TREND': USE_TREND,
            'TRADE_LONG': TRADE_LONG,
            'TRADE_SHORT': TRADE_SHORT
        }) for symbol in self.symbols}
        self.current_positions = {symbol: None for symbol in self.symbols}
        self.running = True
        while self.running:
            try:
                if not self.check_safety_limits():
                    self.logger.info("Торговля приостановлена из-за лимитов безопасности")
                    await asyncio.sleep(60)
                    continue
                for symbol in self.symbols:
                    strategy = self.strategies[symbol]
                    current_price = self.get_current_price(symbol)
                    if current_price == 0:
                        await asyncio.sleep(5)
                        continue
                    ohlcv_data = self.get_ohlcv_data(symbol)
                    if not ohlcv_data:
                        await asyncio.sleep(5)
                        continue
                    if len(strategy.candle_history) < max(VOLUME_PERIOD, MA_LENGTH):
                        for candle in ohlcv_data:
                            candle_dict = {
                                'timestamp': candle[0],
                                'open': candle[1],
                                'high': candle[2],
                                'low': candle[3],
                                'close': candle[4],
                                'volume': candle[5]
                            }
                            strategy.update_candle_history(candle_dict)
                        continue
                    latest_candle = ohlcv_data[-1]
                    candle_dict = {
                        'timestamp': latest_candle[0],
                        'open': latest_candle[1],
                        'high': latest_candle[2],
                        'low': latest_candle[3],
                        'close': latest_candle[4],
                        'volume': latest_candle[5]
                    }
                    candle_analysis = strategy.analyze_candle(candle_dict)
                    self.logger.info(f"ANALYZE {symbol}: {candle_analysis}")
                    if not self.current_positions[symbol]:
                        signal = strategy.check_entry_signal(candle_analysis)
                        if signal:
                            strategy.log_signal(signal, candle_analysis, self.get_balance())
                            balance = self.get_balance()
                            position_size = strategy.calculate_position_size(balance, current_price)
                            if self.open_position(symbol, signal, current_price, position_size):
                                self.current_positions[symbol] = {
                                    'direction': signal,
                                    'entry_price': current_price,
                                    'size': position_size,
                                    'take_profit': strategy.calculate_take_profit_price(current_price, signal),
                                    'stop_loss': strategy.calculate_stop_loss_price(current_price, signal),
                                    'entry_time': datetime.now()
                                }
                                strategy.log_position_opened(self.current_positions[symbol])
                                # Уведомление об открытии позиции
                                msg = (
                                    f"<b>ОТКРЫТА ПОЗИЦИЯ</b>\n"
                                    f"Пара: <b>{symbol}</b>\n"
                                    f"Направление: <b>{signal.upper()}</b>\n"
                                    f"Объём: <b>{position_size:.4f}</b>\n"
                                    f"Вход: <b>{current_price:.4f}</b>\n"
                                    f"TP: <b>{self.current_positions[symbol]['take_profit']:.4f}</b>\n"
                                    f"SL: <b>{self.current_positions[symbol]['stop_loss']:.4f}</b>\n"
                                )
                                await send_trade_notification(msg)
                    elif self.current_positions[symbol]:
                        should_exit, reason = strategy.check_exit_conditions(self.current_positions[symbol], current_price)
                        if should_exit:
                            if self.close_position(symbol, self.current_positions[symbol]['direction'], self.current_positions[symbol]['size']):
                                pnl = strategy.calculate_pnl(self.current_positions[symbol], current_price)
                                if DEMO_MODE:
                                    self.current_balance += pnl
                                strategy.log_position_closed(
                                    self.current_positions[symbol], current_price, reason, pnl
                                )
                                self.update_daily_stats(pnl)
                                # Уведомление о закрытии позиции
                                msg = (
                                    f"<b>ЗАКРЫТА ПОЗИЦИЯ</b>\n"
                                    f"Пара: <b>{symbol}</b>\n"
                                    f"Направление: <b>{self.current_positions[symbol]['direction'].upper()}</b>\n"
                                    f"Объём: <b>{self.current_positions[symbol]['size']:.4f}</b>\n"
                                    f"Вход: <b>{self.current_positions[symbol]['entry_price']:.4f}</b>\n"
                                    f"Выход: <b>{current_price:.4f}</b>\n"
                                    f"TP: <b>{self.current_positions[symbol]['take_profit']:.4f}</b>\n"
                                    f"SL: <b>{self.current_positions[symbol]['stop_loss']:.4f}</b>\n"
                                    f"Причина: <b>{reason}</b>\n"
                                    f"PnL: <b>{pnl:.2f} USDT</b>\n"
                                )
                                await send_trade_notification(msg)
                                self.current_positions[symbol] = None
                                if self.get_balance() >= TARGET_BALANCE:
                                    self.logger.info(f"ЦЕЛЬ ДОСТИГНУТА! Баланс: ${self.get_balance():.2f}")
                                    self.running = False
                                    break
                    if self.current_positions[symbol]:
                        pnl = strategy.calculate_pnl(self.current_positions[symbol], current_price)
                        self.logger.debug(f"{symbol} | Текущий P&L: ${pnl:.2f}")
                await asyncio.sleep(10)
            except Exception as e:
                self.logger.error(f"Ошибка в торговом цикле: {e}")
                await asyncio.sleep(30)
        self.logger.info("Торговый цикл остановлен.")

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running 