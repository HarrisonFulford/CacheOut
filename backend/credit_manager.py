from collections import defaultdict
from config import config
from database import engine
from sqlmodel import Session, select
from models import User
from logger import logger
from typing import Optional

class CreditManager:
    """
    Manages user credit balances and transactions with database persistence.
    """
    def __init__(self):
        self._cache: defaultdict[str, float] = defaultdict(lambda: config.DEFAULT_STARTING_CREDITS)
        self._load_balances_from_db()

    def _load_balances_from_db(self) -> None:
        """Load all user balances from database into cache."""
        try:
            with Session(engine) as session:
                users = session.exec(select(User)).all()
                for user in users:
                    self._cache[user.user_id] = user.credits
                logger.info(f"Loaded {len(users)} user balances from database")
        except Exception as e:
            logger.error(f"Error loading balances from database: {e}")

    def _get_or_create_user(self, user_id: str) -> User:
        """Get user from database or create if doesn't exist."""
        with Session(engine) as session:
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=f"User-{user_id}",
                    credits=config.DEFAULT_STARTING_CREDITS
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created new user {user_id} with {config.DEFAULT_STARTING_CREDITS} credits")
            return user

    def get_balance(self, user_id: str) -> float:
        """Get the credit balance for a user."""
        # Check cache first
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Load from database if not in cache
        try:
            user = self._get_or_create_user(user_id)
            self._cache[user_id] = user.credits
            return user.credits
        except Exception as e:
            logger.error(f"Error getting balance for user {user_id}: {e}")
            return config.DEFAULT_STARTING_CREDITS

    def deduct_credits(self, user_id: str, amount: float) -> bool:
        """Deduct credits from a user's balance. Returns False if insufficient funds."""
        if amount <= 0:
            logger.warning(f"Invalid deduction amount {amount} for user {user_id}")
            return False
        
        try:
            with Session(engine) as session:
                user = session.exec(select(User).where(User.user_id == user_id)).first()
                if not user:
                    logger.warning(f"User {user_id} not found for credit deduction")
                    return False
                
                if user.credits < amount:
                    logger.warning(f"Insufficient credits for user {user_id}: {user.credits} < {amount}")
                    return False
                
                user.credits -= amount
                session.add(user)
                session.commit()
                session.refresh(user)
                
                # Update cache
                self._cache[user_id] = user.credits
                
                logger.info(f"Deducted {amount} credits from user {user_id}. New balance: {user.credits}")
                return True
                
        except Exception as e:
            logger.error(f"Error deducting credits for user {user_id}: {e}")
            return False

    def award_credits(self, user_id: str, amount: float) -> None:
        """Award credits to a user's balance."""
        if amount <= 0:
            logger.warning(f"Invalid award amount {amount} for user {user_id}")
            return
        
        try:
            with Session(engine) as session:
                user = session.exec(select(User).where(User.user_id == user_id)).first()
                if not user:
                    # Create user if doesn't exist
                    user = User(
                        user_id=user_id,
                        username=f"User-{user_id}",
                        credits=amount
                    )
                    session.add(user)
                else:
                    user.credits += amount
                    session.add(user)
                
                session.commit()
                session.refresh(user)
                
                # Update cache
                self._cache[user_id] = user.credits
                
                logger.info(f"Awarded {amount} credits to user {user_id}. New balance: {user.credits}")
                
        except Exception as e:
            logger.error(f"Error awarding credits to user {user_id}: {e}")

    def transfer_credits(self, from_user_id: str, to_user_id: str, amount: float) -> bool:
        """Transfer credits between users atomically."""
        if amount <= 0:
            logger.warning(f"Invalid transfer amount {amount}")
            return False
        
        try:
            with Session(engine) as session:
                from_user = session.exec(select(User).where(User.user_id == from_user_id)).first()
                to_user = session.exec(select(User).where(User.user_id == to_user_id)).first()
                
                if not from_user:
                    logger.warning(f"Source user {from_user_id} not found")
                    return False
                
                if from_user.credits < amount:
                    logger.warning(f"Insufficient credits for transfer: {from_user.credits} < {amount}")
                    return False
                
                # Deduct from source user
                from_user.credits -= amount
                session.add(from_user)
                
                # Add to destination user
                if not to_user:
                    to_user = User(
                        user_id=to_user_id,
                        username=f"User-{to_user_id}",
                        credits=amount
                    )
                    session.add(to_user)
                else:
                    to_user.credits += amount
                    session.add(to_user)
                
                session.commit()
                session.refresh(from_user)
                session.refresh(to_user)
                
                # Update cache
                self._cache[from_user_id] = from_user.credits
                self._cache[to_user_id] = to_user.credits
                
                logger.info(f"Transferred {amount} credits from {from_user_id} to {to_user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error transferring credits: {e}")
            return False

    def get_all_balances(self) -> dict[str, float]:
        """Get all user balances."""
        return dict(self._cache) 