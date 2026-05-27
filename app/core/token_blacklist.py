from app.core.redis import redis_client

BLACKLIST_PREFIX = "blacklist:"


def blacklist_token(jti: str, expires_in: int):

    redis_client.setex(
        f"{BLACKLIST_PREFIX}{jti}",
        expires_in,
        "true"
    )


def is_token_blacklisted(jti: str):

    token = redis_client.get(
        f"{BLACKLIST_PREFIX}{jti}"
    )

    return token is not None