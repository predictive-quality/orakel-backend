# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.apps import AppConfig

class OrakelConfig(AppConfig):
    name = 'orakel'

    def ready(self): #method to import the signals
    	import orakel.signals
