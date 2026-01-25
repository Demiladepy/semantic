"""
Atomic Executor - Execute two-leg arbitrage trades atomically

Prevents "legging risk" where one side of the trade fills but the other doesn't,
leaving you with unhedged exposure.

Strategy:
1. Send BUY order to less liquid market first (usually Kalshi)
2. Listen for fill confirmation via WebSocket
3. Immediately trigger SELL order on Polymarket
4. Auto-cancel if first leg doesn't fill within timeout
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# ENUMS & DATA STRUCTURES
# ========================


class OrderStatus(Enum):
    """Order lifecycle status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderSide(Enum):
    """Order side."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """Represents a single order."""
    market_id: str
    side: OrderSide
    price: float
    size: float
    source: str  # "polymarket" or "kalshi"
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_amount: float = 0.0


@dataclass
class ArbitrageExecution:
    """Represents a complete two-leg arbitrage execution."""
    leg1: Order  # Buy leg
    leg2: Order  # Sell leg
    leg1_filled_at: Optional[float] = None
    leg2_filled_at: Optional[float] = None
    leg1_order_id: Optional[str] = None
    leg2_order_id: Optional[str] = None
    is_complete: bool = False
    net_pnl: float = 0.0


class AtomicExecutor:
    """
    Execute two-leg arbitrage trades with atomic-like guarantees.
    """

    def __init__(self, leg_fill_timeout_seconds: float = 5.0):
        """
        Args:
            leg_fill_timeout_seconds: Max time to wait for first leg to fill
        """
        self.leg_fill_timeout = leg_fill_timeout_seconds
        self.active_orders: Dict[str, ArbitrageExecution] = {}

    # ========================
    # ORDER SUBMISSION
    # ========================

    async def execute_arbitrage_legs(
        self,
        leg1: Order,
        leg2: Order,
        on_leg1_submitted: Optional[Callable] = None,
        on_leg1_filled: Optional[Callable] = None,
        on_leg2_submitted: Optional[Callable] = None,
        on_leg2_filled: Optional[Callable] = None,
    ) -> ArbitrageExecution:
        """
        Execute two-leg arbitrage with safety checks.

        Strategy:
        1. Submit leg1 (buy on less liquid market - usually Kalshi)
        2. Wait for leg1 fill with timeout
        3. If leg1 fills: submit leg2 (sell on Polymarket)
        4. If leg1 timeout: cancel and abort

        Args:
            leg1: First order (BUY on Kalshi typically)
            leg2: Second order (SELL on Polymarket typically)
            on_leg1_submitted: Callback when leg1 submitted
            on_leg1_filled: Callback when leg1 filled
            on_leg2_submitted: Callback when leg2 submitted
            on_leg2_filled: Callback when leg2 filled

        Returns:
            ArbitrageExecution with final status
        """
        execution = ArbitrageExecution(leg1=leg1, leg2=leg2)

        logger.info("=" * 70)
        logger.info("🚀 ATOMIC ARBITRAGE EXECUTION STARTED")
        logger.info("=" * 70)

        try:
            # ===== STEP 1: Submit Leg 1 (Less Liquid Market) =====
            logger.info(f"\n[Step 1/4] Submitting LEG 1 ({leg1.source.upper()})...")
            logger.info(f"  Order: {leg1.side.value} {leg1.size} @ ${leg1.price}")
            logger.info(f"  Market ID: {leg1.market_id}")

            # Simulate order submission (replace with real API call)
            leg1_order_id = await self._submit_order(leg1)
            execution.leg1_order_id = leg1_order_id
            leg1.order_id = leg1_order_id
            leg1.status = OrderStatus.SUBMITTED

            logger.info(f"  ✅ Submitted. Order ID: {leg1_order_id}")

            if on_leg1_submitted:
                on_leg1_submitted(leg1)

            # ===== STEP 2: Wait for Leg 1 Fill (with timeout) =====
            logger.info(f"\n[Step 2/4] Waiting for LEG 1 fill (timeout: {self.leg_fill_timeout}s)...")

            try:
                # This would be replaced with real WebSocket listener
                filled = await asyncio.wait_for(
                    self._wait_for_order_fill(leg1_order_id),
                    timeout=self.leg_fill_timeout,
                )

                if filled:
                    execution.leg1_filled_at = asyncio.get_event_loop().time()
                    leg1.status = OrderStatus.FILLED
                    leg1.filled_amount = leg1.size

                    logger.info(f"  ✅ LEG 1 FILLED at ${leg1.price}")

                    if on_leg1_filled:
                        on_leg1_filled(leg1)

                else:
                    logger.error(f"  ❌ LEG 1 FAILED TO FILL")
                    execution.is_complete = False
                    return execution

            except asyncio.TimeoutError:
                logger.error(
                    f"  ❌ LEG 1 TIMEOUT after {self.leg_fill_timeout}s - ABORTING"
                )
                logger.info(f"  Cancelling order {leg1_order_id}...")

                await self._cancel_order(leg1_order_id)
                leg1.status = OrderStatus.CANCELLED
                execution.is_complete = False

                logger.warning("🛑 ARBITRAGE ABORTED: Leg 1 did not fill in time")
                return execution

            # ===== STEP 3: Submit Leg 2 (More Liquid Market) =====
            logger.info(f"\n[Step 3/4] Submitting LEG 2 ({leg2.source.upper()})...")
            logger.info(f"  Order: {leg2.side.value} {leg2.size} @ ${leg2.price}")
            logger.info(f"  Market ID: {leg2.market_id}")

            leg2_order_id = await self._submit_order(leg2)
            execution.leg2_order_id = leg2_order_id
            leg2.order_id = leg2_order_id
            leg2.status = OrderStatus.SUBMITTED

            logger.info(f"  ✅ Submitted. Order ID: {leg2_order_id}")

            if on_leg2_submitted:
                on_leg2_submitted(leg2)

            # ===== STEP 4: Wait for Leg 2 Fill =====
            logger.info(f"\n[Step 4/4] Waiting for LEG 2 fill (timeout: {self.leg_fill_timeout}s)...")

            try:
                filled = await asyncio.wait_for(
                    self._wait_for_order_fill(leg2_order_id),
                    timeout=self.leg_fill_timeout,
                )

                if filled:
                    execution.leg2_filled_at = asyncio.get_event_loop().time()
                    leg2.status = OrderStatus.FILLED
                    leg2.filled_amount = leg2.size

                    logger.info(f"  ✅ LEG 2 FILLED at ${leg2.price}")

                    if on_leg2_filled:
                        on_leg2_filled(leg2)

                    # Calculate P&L
                    # For a buy-sell arbitrage: profit = (leg2_price - leg1_price) * size
                    execution.is_complete = True
                    execution.net_pnl = (leg2.price - leg1.price) * leg1.size

                    logger.info("\n" + "=" * 70)
                    logger.info("✅ ARBITRAGE EXECUTION COMPLETE!")
                    logger.info(f"   Net P&L: ${execution.net_pnl:.2f}")
                    logger.info("=" * 70)

                    return execution

                else:
                    logger.error(f"  ❌ LEG 2 FAILED TO FILL")
                    logger.warning("⚠️  Leg 1 was filled but Leg 2 failed - UNHEDGED EXPOSURE!")
                    execution.is_complete = False
                    return execution

            except asyncio.TimeoutError:
                logger.error(f"  ❌ LEG 2 TIMEOUT after {self.leg_fill_timeout}s")
                logger.warning("⚠️  Leg 1 filled but Leg 2 timed out - UNHEDGED EXPOSURE!")
                execution.is_complete = False
                return execution

        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR: {e}")
            execution.is_complete = False
            return execution

    # ========================
    # MOCK METHODS (Replace with Real API)
    # ========================

    async def _submit_order(self, order: Order) -> str:
        """
        Submit order to exchange.
        Replace with real API call (Polymarket CLOB, Kalshi API, etc.)
        """
        # Mock: Generate order ID
        order_id = f"{order.source}_{order.market_id}_{abs(hash(str(order)))}"
        await asyncio.sleep(0.1)  # Simulate network latency
        return order_id

    async def _wait_for_order_fill(self, order_id: str) -> bool:
        """
        Wait for order to fill by listening to WebSocket.
        Replace with real WebSocket listener.
        """
        # Mock: Assume fill after short delay
        await asyncio.sleep(0.5)
        return True

    async def _cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        Replace with real API call.
        """
        logger.info(f"   Cancelled order {order_id}")
        await asyncio.sleep(0.1)
        return True


# ========================
# UTILITY FUNCTIONS
# ========================


def get_atomic_executor(leg_fill_timeout_seconds: float = 5.0) -> AtomicExecutor:
    """Factory function for AtomicExecutor."""
    return AtomicExecutor(leg_fill_timeout_seconds=leg_fill_timeout_seconds)


if __name__ == "__main__":
    # Test the atomic executor
    async def test_atomic_execution():
        executor = AtomicExecutor(leg_fill_timeout_seconds=5.0)

        # Create two-leg arbitrage orders
        leg1 = Order(
            market_id="kalshi_market_123",
            side=OrderSide.BUY,
            price=0.48,
            size=100,
            source="kalshi",
        )

        leg2 = Order(
            market_id="polymarket_456",
            side=OrderSide.SELL,
            price=0.52,
            size=100,
            source="polymarket",
        )

        # Execute with callbacks
        def on_fill(order):
            logger.info(f"📊 Order filled: {order.order_id}")

        execution = await executor.execute_arbitrage_legs(
            leg1,
            leg2,
            on_leg1_filled=on_fill,
            on_leg2_filled=on_fill,
        )

        print(f"\nFinal Status: {'✅ Complete' if execution.is_complete else '❌ Failed'}")
        print(f"Net P&L: ${execution.net_pnl:.2f}")

    # Run test
    asyncio.run(test_atomic_execution())
