BROKER_URL="amqp://mosileno:mosileno@localhost:5672/mosilenovhost"

CELERY_TIMEZONE = 'UTC'

CELERY_RESULT_BACKEND = "amqp"
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
