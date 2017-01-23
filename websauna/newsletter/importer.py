"""User state management."""
import logging

from websauna.system.model.retry import ensure_transactionless
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

        logger.info("Subscribing %s to %s", user.email, address)

        # Don't set subscribed field, so that we don't accidentally update unsubscribed users
        data = {
            "address": user.email,
            "name": user.friendly_name,
            "upsert": upsert and "yes" or "no",
        }

        mailgun.make_request("lists/{}/members".format(address), **data)
        mailing_list_subscribes.append(address)

        user.user_data["mailing_list_subscribes"] = mailing_list_subscribes
        return True
    return False


def import_all_users(mailgun: Mailgun, dbsession, address: str) -> int:
    """Update Mail subscribers database from Websauna internal database.

    :return: Imported count
    """

    tm = dbsession.transaction_manager
    count = 0

    # Make sure we don't have a transaction in progress as we do batching ourselves
    ensure_transactionless(transaction_manager=tm)

    with tm:
        user_ids = [u.id for u in dbsession.query(User.id).all()]

    for id in user_ids:
        with tm:
            u = dbsession.query(User).get(id)
            if import_subscriber(mailgun, address, u):
                count += 1

    return count