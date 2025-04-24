from decouple import config

ENVIRONMENT = config("ENVIRONMENT", default="dev")

REDIS_HOST = config("REDIS_HOST") if ENVIRONMENT == "prod" else "0.0.0.0"
REDIS_PORT = config("REDIS_PORT", cast=int)
REDIS_PASSWORD= config("REDIS_PASSWORD")
QUEUE_NAME = config("QUEUE_NAME", default="PET_MATCHER")


EMAIL_PASSWORD = config("EMAIL_PASSWORD")

ROOT_KEY = "qc_pet_adoption"
PET_MATCHER_QUEUE = "qc_pet_adoption:lost_pet_reports"
NOTIFICATION_QUEUE = "qc_pet_adoption:notifications"