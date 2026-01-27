"""
Telegram Bot Integration for Monitoring & Alerting

Features:
- Real-time arbitrage opportunity alerts
- Trading statistics and reports
- Error notifications
- Interactive commands
- Scheduled reports
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    from telegram import Bot, Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot not installed - Telegram features disabled")

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ArbitrageAlert:
    """Arbitrage opportunity alert data."""
    market_a_id: str
    market_b_id: str
    market_a_question: str
    market_b_question: str
    market_a_price: float
    market_b_price: float
    spread_pct: float
    expected_profit_usd: float
    expected_profit_pct: float
    confidence: float
    similarity: float
    strategy_type: str
    timestamp: datetime


class TelegramAlerter:
    """
    Telegram bot for arbitrage alerts and monitoring.
    
    Features:
    - Real-time opportunity alerts
    - Trading statistics
    - Error notifications
    - Interactive commands
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        """
        Initialize Telegram alerter.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID for sending messages
        """
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot required for Telegram integration")

        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN required")

        self.bot = Bot(token=self.bot_token)
        self.app: Optional[Application] = None
        self.stats_cache: Dict[str, Any] = {}

        logger.info("✅ Telegram Alerter initialized")

    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        chat_id: Optional[str] = None,
    ) -> bool:
        """
        Send message to Telegram chat.
        
        Args:
            text: Message text
            parse_mode: Parse mode ("HTML" or "Markdown")
            chat_id: Chat ID (uses default if not provided)
            
        Returns:
            True if sent successfully
        """
        chat_id = chat_id or self.chat_id

        if not chat_id:
            logger.error("Chat ID not set")
            return False

        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_arbitrage_alert(self, alert: ArbitrageAlert) -> bool:
        """
        Send formatted arbitrage opportunity alert.
        
        Args:
            alert: ArbitrageAlert dataclass
            
        Returns:
            True if sent successfully
        """
        emoji = "🚨" if alert.expected_profit_pct > 3.0 else "💰"

        message = f"""
{emoji} <b>ARBITRAGE OPPORTUNITY DETECTED</b> {emoji}

<b>Strategy:</b> {alert.strategy_type.upper()}

<b>Markets:</b>
• Market A: {alert.market_a_question[:50]}...
• Market B: {alert.market_b_question[:50]}...

<b>Prices:</b>
• Market A: {alert.market_a_price:.4f}
• Market B: {alert.market_b_price:.4f}

<b>Spread:</b> {alert.spread_pct:.2f}%
<b>Expected Profit:</b> ${alert.expected_profit_usd:.2f} ({alert.expected_profit_pct:.2f}%)

<b>Confidence:</b> {alert.confidence:.2%}
<b>Semantic Similarity:</b> {alert.similarity:.2f}

<b>Action Required:</b>
Buy Market A @ {alert.market_a_price:.4f}
Sell Market B @ {alert.market_b_price:.4f}

⏰ Detected: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """

        return await self.send_message(message)

    async def send_error_alert(
        self,
        error_message: str,
        error_type: str = "ERROR",
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send error notification.
        
        Args:
            error_message: Error message
            error_type: Error type ("ERROR", "WARNING", "CRITICAL")
            context: Optional context dictionary
            
        Returns:
            True if sent successfully
        """
        emoji_map = {
            "ERROR": "⚠️",
            "WARNING": "🔶",
            "CRITICAL": "🚨",
        }

        emoji = emoji_map.get(error_type, "⚠️")

        message = f"""
{emoji} <b>{error_type}</b>

{error_message}
        """

        if context:
            context_str = "\n".join(f"• {k}: {v}" for k, v in context.items())
            message += f"\n\n<b>Context:</b>\n{context_str}"

        message += f"\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return await self.send_message(message)

    async def send_daily_report(self, stats: Dict[str, Any]) -> bool:
        """
        Send daily performance report.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            True if sent successfully
        """
        message = f"""
📊 <b>DAILY PERFORMANCE REPORT</b>

<b>Today's Performance:</b>
• Trades Executed: {stats.get('trades_today', 0)}
• Total Profit: ${stats.get('profit_today', 0):,.2f}
• Win Rate: {stats.get('win_rate_today', 0):.1%}
• Best Trade: ${stats.get('best_trade_today', 0):.2f}

<b>This Week:</b>
• Total Trades: {stats.get('trades_week', 0)}
• Total Profit: ${stats.get('profit_week', 0):,.2f}
• Avg Profit/Trade: ${stats.get('avg_profit_week', 0):.2f}

<b>All Time:</b>
• Total Trades: {stats.get('total_trades', 0)}
• Total Profit: ${stats.get('total_profit', 0):,.2f}
• Overall Win Rate: {stats.get('overall_win_rate', 0):.1%}

<b>Active Opportunities:</b> {stats.get('active_opportunities', 0)}
<b>Markets Monitored:</b> {stats.get('markets_monitored', 0)}

⏰ Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        return await self.send_message(message)

    def setup_bot_commands(self):
        """Set up interactive bot commands."""
        if not self.bot_token:
            logger.warning("Bot token not set - commands disabled")
            return

        self.app = Application.builder().token(self.bot_token).build()

        # Register command handlers
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("opportunities", self._cmd_opportunities))
        self.app.add_handler(CommandHandler("stats", self._cmd_stats))
        self.app.add_handler(CommandHandler("help", self._cmd_help))

        logger.info("✅ Bot commands registered")

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await update.message.reply_text(
            "🤖 <b>Arbitrage Bot Started!</b>\n\n"
            "Commands:\n"
            "/status - Check bot status\n"
            "/opportunities - View current opportunities\n"
            "/stats - View trading statistics\n"
            "/help - Show help message",
            parse_mode="HTML"
        )

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        status_msg = """
✅ <b>Bot Status</b>

🔴 Markets Monitored: {markets}
🟢 Active Opportunities: {opportunities}
⚡ Update Frequency: 30s
💰 Total Profit Today: ${profit_today:.2f}
📊 Win Rate: {win_rate:.1%}
        """.format(
            markets=self.stats_cache.get("markets_monitored", 0),
            opportunities=self.stats_cache.get("active_opportunities", 0),
            profit_today=self.stats_cache.get("profit_today", 0),
            win_rate=self.stats_cache.get("win_rate_today", 0),
        )

        await update.message.reply_text(status_msg, parse_mode="HTML")

    async def _cmd_opportunities(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /opportunities command."""
        opportunities = self.stats_cache.get("current_opportunities", [])

        if not opportunities:
            await update.message.reply_text("No opportunities found.")
            return

        message = "<b>Current Opportunities:</b>\n\n"
        for i, opp in enumerate(opportunities[:10], 1):  # Limit to 10
            message += f"{i}. {opp.get('question', 'N/A')[:40]}...\n"
            message += f"   Spread: {opp.get('spread', 0):.2f}%\n"
            message += f"   Profit: ${opp.get('profit', 0):.2f}\n\n"

        await update.message.reply_text(message, parse_mode="HTML")

    async def _cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        await self.send_daily_report(self.stats_cache)

    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
<b>Arbitrage Bot Commands</b>

/start - Start the bot
/status - Check bot status and metrics
/opportunities - View current arbitrage opportunities
/stats - View detailed trading statistics
/help - Show this help message

<b>Features:</b>
• Real-time arbitrage alerts
• Trading performance tracking
• Error notifications
• Market monitoring

For support, check the logs or contact the administrator.
        """

        await update.message.reply_text(help_text, parse_mode="HTML")

    def run_bot(self):
        """Start the bot polling."""
        if not self.app:
            self.setup_bot_commands()

        if self.app:
            logger.info("🤖 Starting Telegram bot...")
            self.app.run_polling()
        else:
            logger.error("Bot not initialized")

    def update_stats_cache(self, stats: Dict[str, Any]):
        """Update statistics cache for commands."""
        self.stats_cache.update(stats)


# ========================
# UTILITY FUNCTIONS
# ========================

def get_telegram_alerter(
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> TelegramAlerter:
    """Factory function for TelegramAlerter."""
    return TelegramAlerter(bot_token=bot_token, chat_id=chat_id)


if __name__ == "__main__":
    # Test Telegram alerter
    try:
        alerter = get_telegram_alerter()
        
        # Test alert
        test_alert = ArbitrageAlert(
            market_a_id="poly_123",
            market_b_id="kalshi_456",
            market_a_question="Will Bitcoin reach $100k by 2025?",
            market_b_question="BTC-100K-2025",
            market_a_price=0.65,
            market_b_price=0.72,
            spread_pct=7.0,
            expected_profit_usd=35.00,
            expected_profit_pct=3.5,
            confidence=0.95,
            similarity=0.89,
            strategy_type="combinatorial",
            timestamp=datetime.now(),
        )
        
        # Uncomment to send test alert
        # asyncio.run(alerter.send_arbitrage_alert(test_alert))
        
        print("✅ Telegram Alerter initialized")
    except Exception as e:
        print(f"Error: {e}")
