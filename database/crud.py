from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payment import Payment
from database.models.subscription import Subscription
from database.models.user import User


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None, full_name: str) -> User:
    query = select(User).where(User.telegram_id == telegram_id)
    user = (await session.execute(query)).scalar_one_or_none()
    if user:
        user.username = username
        user.full_name = full_name
        await session.commit()
        await session.refresh(user)
        return user

    user = User(telegram_id=telegram_id, username=username, full_name=full_name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_subscription(session: AsyncSession, user_id: int, plan_days: int, price_rub: int) -> Subscription:
    subscription = Subscription(user_id=user_id, plan_days=plan_days, price_rub=price_rub)
    session.add(subscription)
    await session.commit()
    await session.refresh(subscription)
    return subscription


async def get_latest_pending_subscription(session: AsyncSession, user_id: int) -> Subscription | None:
    q = (
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.status == 'pending')
        .order_by(Subscription.created_at.desc())
    )
    return (await session.execute(q)).scalar_one_or_none()


async def activate_subscription(
    session: AsyncSession,
    subscription: Subscription,
    wg_client_id: str,
    wg_client_name: str,
    config_path: str,
) -> Subscription:
    now = datetime.now(UTC)
    subscription.status = 'active'
    subscription.starts_at = now
    subscription.ends_at = now + timedelta(days=subscription.plan_days)
    subscription.wg_client_id = wg_client_id
    subscription.wg_client_name = wg_client_name
    subscription.config_path = config_path
    await session.commit()
    await session.refresh(subscription)
    return subscription


async def get_user_active_subscription(session: AsyncSession, user_id: int) -> Subscription | None:
    q = (
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.status == 'active')
        .order_by(Subscription.created_at.desc())
    )
    return (await session.execute(q)).scalar_one_or_none()


async def create_payment(
    session: AsyncSession,
    user_id: int,
    amount_rub: int,
    subscription_id: int | None = None,
    provider: str = 'manual',
) -> Payment:
    payment = Payment(
        user_id=user_id,
        subscription_id=subscription_id,
        amount_rub=amount_rub,
        provider=provider,
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def get_latest_created_payment_for_subscription(
    session: AsyncSession,
    subscription_id: int,
) -> Payment | None:
    q = (
        select(Payment)
        .where(Payment.subscription_id == subscription_id, Payment.status == 'created')
        .order_by(Payment.created_at.desc())
    )
    return (await session.execute(q)).scalar_one_or_none()


async def mark_payment_paid(session: AsyncSession, payment_id: int, provider_payment_id: str | None = None) -> Payment | None:
    payment = await session.get(Payment, payment_id)
    if not payment:
        return None
    payment.status = 'paid'
    payment.provider_payment_id = provider_payment_id
    await session.commit()
    await session.refresh(payment)
    return payment
    await session.commit()
    await session.refresh(payment)
    return payment

