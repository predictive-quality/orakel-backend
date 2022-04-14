from orakel import models
from orakel.serializers.utils import BaseSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField

class ShopFloorSerializer(BaseSerializer):
    """HyperlinkedSerializer for Model Shopfloor.

    Relationships:
        Machine to ShopFloor: ManyToOne
        RealSensor to ShopFloor: ManyToOne
        Event to ShopFloor: ManyToOne
    """
    url = HyperlinkedIdentityField(view_name="shopfloor-detail", read_only=True)
    machine = PrimaryKeyRelatedField(view_name='machine-detail',read_only=False, many=True, required=False, queryset=models.Machine.objects.all(), style={'base_template': 'input.html'})
    sensor = PrimaryKeyRelatedField(view_name='sensor-detail',read_only=False, many=True, required=False, queryset=models.Sensor.objects.all(), style={'base_template': 'input.html'})
    event = PrimaryKeyRelatedField(view_name='event-detail',read_only=False, many=True, required=False, queryset=models.Event.objects.all(), style={'base_template': 'input.html'})

    # It is possible to exclude Related Attributes with many=True from returning an url with a filter in order to return a list with the defined fields
    # exclude_many_relations_from_filter_url = ('event',) 

    class Meta:
        model = models.ShopFloor
        fields = ('id','name','url','description','machine','sensor','event')
        depth = 1
