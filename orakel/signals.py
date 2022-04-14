from django.dispatch import receiver, Signal
from django.core.cache import cache
from orakel import models

from django.db.models.signals import (
    post_save,
    post_delete,
    m2m_changed,
)

receiver_signals = [post_save, post_delete, m2m_changed]

# method for updating after entry save/delete data
"""
@receiver(receiver_signals, sender=models.Event)
@receiver(receiver_signals, sender=models.DataFrame)
@receiver(receiver_signals, sender=models.PipelineBlock)
@receiver(receiver_signals, sender=models.MachineLearningRun)
@receiver(receiver_signals, sender=models.MachineLearningRunSpecification)
@receiver(receiver_signals, sender=models.Machine)
@receiver(receiver_signals, sender=models.Operator)
@receiver(receiver_signals, sender=models.ProcessParameter)
@receiver(receiver_signals, sender=models.ProcessStep)
@receiver(receiver_signals, sender=models.ProcessStepSpecification)
@receiver(receiver_signals, sender=models.Product)
@receiver(receiver_signals, sender=models.PreProduct)
@receiver(receiver_signals, sender=models.ProductSpecification)
@receiver(receiver_signals, sender=models.QualityCharacteristics)
@receiver(receiver_signals, sender=models.Sensor)
@receiver(receiver_signals, sender=models.SensorReading)
@receiver(receiver_signals, sender=models.ShopFloor)
@receiver(receiver_signals, sender=models.Tool)
def clear_cache(sender, instance, *args, **kwargs):
    cache.clear()
"""
