# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.models.basic.processstepspecification import ProcessStepSpecification
from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import ProcessStepSpecificationSerializer
from orakel.models import ProcessStepSpecification

from rest_framework import status as rf_status



class ProcessStepSpecificationViewSet(CustomModelViewSet):
    """Viewset for Model ProcessStepSpecification.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Relationships:
        ProcessStep to ProcessStepSpecification: ManyToOne
        ProcessParameter to ProcessStepSpecification: ManyToOne
        Event to ProcessStepSpecification: ManyToOne
        ProcessStepSpecification to Productspecification: ManyToOne
        ProcessStepSpecification to MachineLearningRun: OneToOne
    """
    serializer_class = ProcessStepSpecificationSerializer
    django_model = ProcessStepSpecification


    def add_ids(self,pk, ids_to_add, attribute):
        """Add ProcessStepSpecification instance id to related ProcessStepSpecification next_pss or previous_pss.

        Args:
            pk (int): ProcessStepSpecification id from the request.
            ids_to_add (list): ProcessStepSpecification ids to add the requests instance id.
            attribute (str): Wether next_pss or previous_pss.
        """
        assert attribute in ["next_pss", "previous_pss"]
        for id in ids_to_add:
            if id is not None:
                if attribute == 'next_pss':
                    self.django_model.objects.get(id=id).add_previous_pss(self.django_model.objects.get(id=pk))
                if attribute == 'previous_pss':
                    self.django_model.objects.get(id=id).add_next_pss(self.django_model.objects.get(id=pk))

    def remove_ids(self,pk, ids_to_remove, attribute):
        """Remove ProcessStepSpecification instance id to related ProcessStepSpecification next_pss or previous_pss.

        Args:
            pk (int): ProcessStepSpecification id from the request.
            ids_to_add (list): ProcessStepSpecification ids to remove the requests instance id.
            attribute (str): Wether next_pss or previous_pss.
        """
        assert attribute in ["next_pss", "previous_pss"]
        for id in ids_to_remove:
            if id is not None:
                if attribute == 'next_pss':
                    self.django_model.objects.get(id=id).remove_previous_pss(self.django_model.objects.get(id=pk))
                if attribute == 'previous_pss':
                    self.django_model.objects.get(id=id).remove_next_pss(self.django_model.objects.get(id=pk))


    def update_next_previous_pss(self, pk, next_pss, previous_pss, current_next_ids, current_previous_ids):
        """Check if related ProcessStepSpecification fields next_pss/previous_pss has to be updated.

        Args:
            pk (int): ProcessStepSpecification id from the request.
            next_pss (list[int]):  ProcessStepSpecification.next_pss ids from the request.data
            previous_pss (list[int]):ProcessStepSpecification.previous_pss ids from the request.data
            current_next_ids (list[int]): ProcessStepSpecification.next_pss id that are assigned to the ProcessStepSpecification instance before the update.
            current_previous_ids (list[int]): ProcessStepSpecification.previous_pss ids that are assigned to the ProcessStepSpecification instance before the update.
        """
        if type(next_pss) == list:
            next_ids_to_add = tuple(set(next_pss) - set(current_next_ids))
            next_ids_to_remove = tuple(set(current_next_ids) - set(next_pss))
            if next_ids_to_add:
                self.add_ids(pk, next_ids_to_add, 'next_pss')
            if next_ids_to_remove:
                self.remove_ids(pk, next_ids_to_remove, 'next_pss')

        if type(previous_pss) == list:
            previous_next_ids_to_add = tuple(set(previous_pss) - set(current_previous_ids))
            previous_ids_to_remove = tuple(set(current_previous_ids) - set(previous_pss))
            if previous_next_ids_to_add:
                self.add_ids(pk, previous_next_ids_to_add, 'previous_pss')
            if previous_ids_to_remove:
                self.remove_ids(pk, previous_ids_to_remove, 'previous_pss')



    def partial_update(self, request, pk, *args, **kwargs):

        # Check if next_pss or previous_pss is in the update_data in order to update the related ProcessStepSpecifications.
        next_pss = request.data.get("next_pss", None)
        previous_pss = request.data.get("previous_pss", None)

        if type(next_pss) == list or type(previous_pss) == list:
            current_next_ids = list(self.django_model.objects.filter(pk=pk).values_list('next_pss', flat=True))
            current_previous_ids = list(self.django_model.objects.filter(pk=pk).values_list('previous_pss', flat=True))

            update_response = super().partial_update(request, pk, *args, **kwargs)

            if update_response.status_code == rf_status.HTTP_200_OK:
                self.update_next_previous_pss(pk, next_pss, previous_pss, current_next_ids, current_previous_ids)

            return update_response

        else:
            return super().partial_update(request, pk, *args, **kwargs)
