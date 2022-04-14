from django.db import models
from orakel.models.utils import BaseModel

class ProcessStep(BaseModel):
    """process step performs any form of manipulation required in the Process Flow. Some exemplary manipulations are forming, assembly and also quality inspections. 
    They usually involve a machine, a tool and an operator. The Process Step stores the effective parameters and is further linked to all generated sensor readings. 
    After its execution, the Inter-Product Specifications, as linked via the Process Step Specification, should be satisfied. 
    The complexity of a process step should be minimal to (a) reduce the number of contributing entities and to (b) minimize the model complexity of the employed PQ methods.

    Relationships:
        ProcessStep to Machine: ManyToOne
        ProcessStep to Operator: ManyToOne
        ProcessStep to ProcessStepSpecification: ManyToOne
        ProcessStep to Product: ManyToOne
        ProcessStep to PreProduct: ManyToOne
        Tool to ProcessStep: ManyToMany
        SensorReading to ProcessStep: ManyToOne
        Event to ProcessStep: ManyToOne
    """
    name = models.CharField(max_length=100, default=None ,null=True, blank=True)
    machine = models.ForeignKey('Machine',  related_name='%(class)s',  default=None, null=True, blank=True, on_delete=models.SET_NULL) 
    operator = models.ForeignKey('Operator',  related_name='%(class)s',  default=None, null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey('Product',  related_name='%(class)s',  default=None, null=True, blank=True, on_delete=models.SET_NULL)
    preproduct = models.ForeignKey('PreProduct',  related_name='%(class)s',  default=None, null=True, blank=True, on_delete=models.SET_NULL)
    processstepspecification = models.ForeignKey('ProcessStepSpecification', related_name='%(class)s',  default=None, null=True, blank=True, on_delete=models.SET_NULL)
    
    status_choices = [  ('Succeeded','Succeeded'),
                        ('Running','Running'),
                        ('Pending','Pending'),
                        ('Failed','Failed'),
                        ('Stopped','Stopped'),
                        ('Other','Other'),
                        ('Created','Created')
                    ]
    status = models.CharField(max_length=100, default='Other', null=True, blank=True, choices=status_choices)
    started = models.DateTimeField(default=None,null=True, blank=True)
    ended = models.DateTimeField(default=None,null=True, blank=True)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=['product']), 
                   models.Index(fields=['machine']), 
                   models.Index(fields=['processstepspecification']),
                   models.Index(fields=['preproduct'])
                   ]
