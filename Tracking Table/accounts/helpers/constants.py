"""Account role values stored on accounts.User."""

USER_ROLE_ADMIN = "Admin"
USER_ROLE_STORE = "Store"
USER_ROLE_WAREHOUSE = "Warehouse"
USER_ROLE_EXTERNAL = "External"

USER_ROLES = (
    USER_ROLE_ADMIN,
    USER_ROLE_STORE,
    USER_ROLE_WAREHOUSE,
    USER_ROLE_EXTERNAL,
)

USER_ROLE_CHOICES = (
    (USER_ROLE_ADMIN, "Администратор"),
    (USER_ROLE_STORE, "Магазин"),
    (USER_ROLE_WAREHOUSE, "Склад"),
    (USER_ROLE_EXTERNAL, "Външен потребител"),
)
