from django.apps import AppConfig

class PuzzlestoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'puzzlestore'
    
    def ready(self):
        import puzzlestore.signals