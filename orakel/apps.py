from django.apps import AppConfig

class OrakelConfig(AppConfig):
    name = 'orakel'

    def ready(self): #method to import the signals
    	import orakel.signals
