TORTOISE_ORM = {
    "connections": {"default": "postgres://user1:password1@127.0.0.1:5432/medic_db"},
    "apps": {
        "models": {
            "models": ["models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}