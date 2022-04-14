# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import ProcessParameterSerializer, SensorReadingSerializer
from orakel import models
import pandas as pd
from rest_framework.decorators import action
from rest_framework import status as rf_status
from rest_framework.response import Response
from rest_framework import pagination

import datetime
import re

class ProcessParameterViewSet(CustomModelViewSet):
    """Viewset for Model ProcessParameter.
    ProcessParameter specify sensor and processstepspecification characteristics and limits.

    Relationships:
        ProcessParameter to ProcessStepSpecification: ManyToOne
        ProcessParameter to Sensor: ManyToOne
        SensorReading to ProcessParameter: ManyToOne
        Event to ProcessParameter: ManyToOne
    """
    serializer_class = ProcessParameterSerializer
    django_model = models.ProcessParameter


    @action(detail=True, methods=["get"], url_path="daterange")  # Detail=True to use action/method on an instance.
    def daterange_from_id(self, request, pk, *args, **kwargs):
        """Returns the oldest and the youngest date of sensorreading entries.
        Args:
            request (requests): Get Request on an instance.
            pk (int): pk/id of the ProcessParameter instance.

        Returns:
            [dict(str)]:
                - firstDate: Date of the sensorreading entry with the oldest date regarding to the given ProcessParameter.id.
                - lastDate: Date of the sensorreading entry with the newest date regarding to the given ProcessParameter.id .
        """

        last_object = models.SensorReading.objects.filter(processparameter=pk).order_by('date').last()
        first_object = models.SensorReading.objects.filter(processparameter=pk).order_by('date').first()

        first_date = first_object.date if first_object else None
        last_date = last_object.date if last_object else None

        return Response(status=rf_status.HTTP_200_OK, data={"firstDate": first_date, "lastDate": last_date})

    @action(detail=False, methods=["post"], url_path="daterange")
    def daterange_from_list(self, request, *args, **kwargs):
        """Returns the oldest and the youngest date of sensorreading entries.
        Args:
           processparameter_ids (list): ids of the ProcessParameter instances.
        Example Data:
            {
                "processparameter_ids": [1,2]
            }

        Returns:
            [dict(str)]:
                - firstDate: Date of the sensorreading entry with the oldest date regarding to the given ProcessParameter.ids.
                - lastDate: Date of the sensorreading entry with the newest date regarding to the given ProcessParameter.ids.
        """
        data = request.data
        processparameter_ids = data.get("processparameter_ids", None)
        last_object = models.SensorReading.objects.filter(processparameter__in=processparameter_ids).order_by('date').last()
        first_object = models.SensorReading.objects.filter(qualitycharacteristics__in=processparameter_ids).order_by('date').first()

        first_date = first_object.date if first_object else None
        last_date = last_object.date if last_object else None

        return Response(status=rf_status.HTTP_200_OK, data={"firstDate": first_date, "lastDate": last_date})


    @staticmethod
    def validate_date(date):
        """Validate the date format

        Args:
            date (datetime.date): datetime.date or string of a date

        Returns:
            [bool]: Wether the datetime format fits or not.
        """
        try:
            datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
            return True
        except:
            return False

    @staticmethod
    def validate_productspecification_id(productspecification_id):
        """Validate the productspecification_id type and if its existing.

        Args:
            productspecification_id (int): id of a productspecification instance

        Returns:
            [bool]: True when the productspecification id is correct.
        """
        if type(productspecification_id) != int:
            return False
        if not models.ProcessStepSpecification.objects.filter(pk=productspecification_id).exists():
            return False

        return True


    def validate_product_id(self, product_id):
        """Validate the product_id type and if a corresponding ProcessStep is existing.

        Args:
            product_id (int): id of a product instance

        Returns:
            [bool]: True when the product_id is correct and connected with a ProcessStep.
        """
        if type(product_id) != int:
            return False
        if not models.ProcessStep.objects.filter(product_id=product_id).exists():
            return False

        return True

    @action(detail=True, methods=["get"], url_path='perproduct/(?P<product_id>[0-9]{1,10})') # Detail=True to use action/method on an instance.
    def perproduct(self, request, pk, product_id, *args, **kwargs):
        """Lists all SensorReadings related to the ProcessParameter instance and the given Product instance.
        Args:
            pk (int): id/pk of the ProcessParameter instance. (Supplied with the url)
            product_id (int): Id of an Product instance. (Supplied with the url)
            aggregationWindow (str): length of the time windows for aggregation. Format: <time><unit>. Supported units: ms, s, m. Example: 5s (Optional, supplied with the url)
            aggregationFcn (str): Function for aggregation. Supports avg, min, max and std. (optional, provided with the url)
        Returns:
            if not aggregated:
            [dict]: Id, date, value and sensor_id of SensorReading instances.
            if aggregated:
            [list]: {Start time of aggregationWindow, aggregated value}
        """

        """
        Input to Output:
          - processparemter/pk: user input / request data
          - product_id: user input / request data
          - processsteps = ProcessSteps(product_id)
          - queryset = SensorReadings(processparemter, processsteps)
        """
        if (request.GET.get("aggregationFcn", None) is not None) and (request.GET.get("aggregationWindow", None) is None):
           return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Aggregation function but no aggregation window provided.")

        # get and check the aggregation function
        aggregationFcn = request.GET.get("aggregationFcn", None)
        if aggregationFcn not in ['avg', 'max', 'min', 'std', None]:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="The provided aggregationFcn is not supported or the provided format is wrong.")
        # get and check the aggregation window, convert it to a datetime.timedelta and a frequency for pandas grouping
        aggregationWindow = request.GET.get("aggregationWindow", None)
        if aggregationWindow:
            aggregationWindow_split = re.split('(\d+)', aggregationWindow)
            if aggregationWindow_split:
                if aggregationWindow_split[2] == 'm':
                    delta = datetime.timedelta(minutes=int(aggregationWindow_split[1]))
                    freq = aggregationWindow_split[1]+'T'
                elif aggregationWindow_split[2] == 's':
                    delta = datetime.timedelta(seconds=int(aggregationWindow_split[1]))
                    freq = aggregationWindow_split[1]+'S'
                elif aggregationWindow_split[2] == 'ms':
                    delta = datetime.timedelta(milliseconds=int(aggregationWindow_split[1]))
                    freq = aggregationWindow_split[1]+'L'
                else:
                    return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Time unit is not supported.")

            else:
                    return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="The provided aggregationWindow has the wrong format.")
        else:
            aggregationWindow_split = None

        # Exclude these fields from the Response data.
        excluded_fields = ["event", "name", "url", "processparameter", "qualitycharacteristics",  "processstep"]
        product_id = int(product_id)

        # Validate the Product id.
        if not self.validate_product_id(product_id):
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Incorrect data type or product id is not conntected with a ProcessStep.")

        # Get the related ProcessStep instances related to the Products instances.
        processsteps = models.Product.objects.filter(id=product_id).values_list('id', flat=True)
        if processsteps:
            # Get the SensorReadings ordered by the date. Oldest first, newest last.
            queryset = models.SensorReading.objects.filter(processparameter=pk,processstep_id__in=processsteps).order_by('date').only('id','value','date','sensor_id')

            # aggregation if aggregation parameters are provided
            if aggregationWindow_split is not None:
                # calculate whether the aggregation window is too small (more than 10% of the windows without sensorreadings). If aggegationWindow is too small unaggregated values are returned.
                first_date = queryset.first().date
                last_date = queryset.last().date
                aggregation = True
                if ((delta/(last_date-first_date))<0.1):
                    aggregation = False
                # convert queryset to pandas.DataFrame for efficient aggregation
                df = pd.DataFrame(list(queryset.values()))
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = df['value'].astype(float)
                df = df[['date', 'value']]
                df = df.set_index('date', drop=False)
                # select the correct aggregation function
                if aggregation == True:
                    if aggregationFcn in ['avg',None]:
                        df = df.groupby([pd.Grouper(freq=freq)]).mean()
                    elif aggregationFcn == 'min':
                        df = df.groupby([pd.Grouper(freq=freq)]).min()
                    elif aggregationFcn == 'max':
                        df = df.groupby([pd.Grouper(freq=freq)]).max()
                    elif aggregationFcn == 'std':
                        df = df.groupby([pd.Grouper(freq=freq)]).std()
                # insert empty values with linear interpolation
                df['value'] = df['value'].interpolate()
                data = []
                # create list of dictionaries out of the aggregated data
                for index, row in df.iterrows():
                    dictionary = {str(index):row['value']}
                    data.append(dictionary.copy())
                # paginate the list
                paginator = LinkHeaderPagination()
                page = paginator.paginate_queryset(data, request)
                if page is not None:
                    return paginator.get_paginated_response(page)
                return Response(status=rf_status.HTTP_200_OK, data=data)

            else:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = SensorReadingSerializer(page, excluded_fields=excluded_fields, context={'request': request}, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = SensorReadingSerializer(queryset, excluded_fields=excluded_fields, context={'request': request}, many=True)

                return Response(status=rf_status.HTTP_200_OK, data=serializer.data)

        else:
            return Response(status=rf_status.HTTP_404_NOT_FOUND, data="No SensorReadings found! There is no related ProcessStep.")

# pagination for list of dictionaries
class LinkHeaderPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
        else:
            link = ''

        link = link.format(next_url=next_url, previous_url=previous_url)
        headers = {'Link': link, 'Count': self.page.paginator.count} if link else {}

        return Response(data, headers=headers)
