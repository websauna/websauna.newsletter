"""User state management."""
# Standard Library
import logging
from typing import Optional

# Pyramid
from transaction import TransactionManager

# Websauna
from websauna.system.model.retry import ensure_transactionless
from websauna.system.model.retry import retryable
from websauna.system.user.models import User

from .mailgun import Mailgun


logger = logging.getLogger(__name__)


def import_subscriber(mailgun: Mailgun, address: str, user: User, upsert=True) -> bool:
    """Add one subscriber to the mailing list.

    :return: True if user was fresh and imported
    """

    # Track import status in user_data JSON, so we don't do double requests if the user has already been subscribed once
    mailing_list_subscribes = user.user_data.get("mailing_list_subscribes", [])

    if address not in mailing_list_subscribes:

        # Some sanity logic to filter out emails that are legit in some services, unlegit in Mailgun
        first_part, second_part = address.split("@")
        if first_part.startswith(".") or first_part.endswith("."):
            logger.info("Bad email address: %s", address)
            return False

        logger.info("Subscribing %s to %s", user.email, address)

        # Don't set subscribed field, so that we don't accidentally update unsubscribed users
        data = {
            "address": user.email,
            "name": user.friendly_name,
            "upsert": upsert and "yes" or "no",
        }

        try:
            mailgun.update_subscription(address, data)
        except Exception as e:
            logger.error("Failed to subscribe email %s: %s", user.email, e)
            return False

        mailing_list_subscribes.append(address)

        user.user_data["mailing_list_subscribes"] = mailing_list_subscribes
        return True
    return False


def import_all_users(mailgun: Mailgun, dbsession, address: str, tm: Optional[TransactionManager]=None) -> int:
    """Update Mail subscribers database from Websauna internal database.

    :return: Imported count
    """

    if tm is None:
        tm = dbsession.transaction_manager

    count = 0

    for obj in dbsession:
        print(obj)

    # Make sure we don't have a transaction in progress as we do batching ourselves
    ensure_transactionless(transaction_manager=tm)

    @retryable(tm=tm)
    def tx1():
        """Get user ids on the first transaction."""
        return [u.id for u in dbsession.query(User.id).all()]

    @retryable(tm=tm)
    def tx_n(id):
        """For each user, import it in a subsequent transaction."""
        u = dbsession.query(User).get(id)
        if import_subscriber(mailgun, address, u):
            return 1
        else:
            return 0

    user_ids = tx1()
    for id in user_ids:
        count += tx_n(id)

    logger.info("Imported %d users", count)

    return count
