import os

from celery import Celery

# Установим модуль настроек Django по умолчанию для программы "celery".
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery(
    "config",
    broker="redis://localhost:6379/0",  # Отрегулируйте, настроен ли ваш Redis по-другому
    backend="redis://localhost:6379/0",
    include=["mailing.tasks"],
)  #  Задачи будут определены в почтовом приложении

# Использование строки здесь означает, что для работы не нужны сериализаторы
# объект конфигурации для дочерних процессов.
# - namespace='CELERY' означает, что все ключи конфигурации, связанные с celery
# , должны иметь префикс CELERY_.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Загружайте модули задач из всех зарегистрированных конфигураций приложений Django.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
