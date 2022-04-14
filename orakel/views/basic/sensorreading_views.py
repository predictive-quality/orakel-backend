# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.models.basic import qualitycharacteristics
from orakel.views.utils import CustomModelViewSet
from orakel.serializers.v1 import SensorReadingSerializer
from orakel.models import SensorReading, Sensor, ProcessParameter, QualityCharacteristics, ProcessStep, Event, ProcessStepSpecification
from rest_framework.decorators import action
from rest_framework import status as rf_status
from rest_framework.response import Response
from rest_framework import pagination

import pandas as pd
import numpy as np
import datetime
import re
import numbers
from job_scheduler.tasks import c_update_date

class SensorReadingViewSet(CustomModelViewSet):
    """Viewset for Model SensorReading.
    The ModelViewSet class inherits from GenericAPIView and includes implementations for various actions, by mixing in the behavior of the various mixin classes.
    The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .partial_update(), and .destroy()

    Model Relationships:
        SensorReading to Sensor: ManyToOne
        SensorReading to ProcessStep: ManyToOne
        SensorReading to ProcessParameter: ManyToOne
        SensorReading to QualityCharacteristics: ManyToOne
        Event to SensorReading: ManyToOne
    """
    serializer_class = SensorReadingSerializer
    django_model = SensorReading

    def __init__(self, *args, **kwargs):
        super(SensorReadingViewSet, self).__init__(*args, **kwargs)
        self.filter_fields["date"].extend(["gte", "lte"])

    @action(detail=False, methods=["get"])
    def aggregation(self, request, *args, **kwargs):
        """Lists the aggregation of SensorReading instances over a certain QualityCharacteristics, ProcessParameter or Sensor.
        Args:
            qualitycharacteristics_id (int): Id of a QualityCharacteristics instance. Exactly one of the parameters processparameter_id, qualitycharacterics_id, sensor_id must be given. (Supplied with the url)
            processparameter_id (int): Id of a ProcessParameeter instance. Exactly one of the parameters processparameter_id, qualitycharacterics_id, sensor_id must be given. (Supplied with the url)
            sensor_id (int): Id of a Sensor instance. Exactly one of the parameters processparameter_id, qualitycharacterics_id, sensor_id must be given. (Supplied with the url)
            processstep_id (int): Id of a ProcessStep. (optional, supplied with the url)
            aggregationWindow (str): length of the time windows for aggregation. Format: <time><unit>. Supported units: ms, s, m. Example: 5s (Optional, supplied with the ur)
            aggregationFcn (str): Function for aggregation. Supports avg, min, max and std. (optional, provided with the url)
            date_gte (timestamp): Start date and time of timeframe to consider.
            date_lte (timestamo): End date and time of timeframe to consider.
        Returns:
            if not aggregated:
            [dict]: Id, date, value and sensor_id of SensorReading instances.
            if aggregated and aggregationWindow:
            [dict]: Start date ('date') of the aggreationWindows with SensorReadings within and aggregated value ('value') of SensorReadings within this aggregationWindow. Empty
            if aggregatet and no aggregationWindow:
            [float]: Aggregated value
        """

        """
        Input to Output:
          - processparameter_id/qualitycharacteristics_id/sensor_id: user input / request data
          - queryset = SensorReadings(<one of qualitycharacteristic, processparameter or sensor>, processsteps)
        """
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
        excluded_fields = ["event", "url", "processparameter", "qualitycharacteristics",  "processstep"]

        qualitycharacteristics_id = request.GET.get("qualitycharacteristics_id", None)
        processparameter_id = request.GET.get("processparameter_id", None)
        sensor_id = request.GET.get("sensor_id", None)
        processstep_id = request.GET.get("processstep_id", None)
        date_lte = request.GET.get("date_lte")
        date_gte = request.GET.get("date_gte")


        # Check whether exactly one of processparameter_id, qualitycharacteristics_id and sensor_id is provided.
        not_none_count = 0
        if qualitycharacteristics_id:
            not_none_count += 1
        if processparameter_id:
            not_none_count += 1
        if sensor_id:
            not_none_count += 1
        if not_none_count != 1:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Not exactly one of processparameter_id, qualitycharacteristics_id and sensor_id provided.")

        # define filter for querying the database
        queryset_filter_kwargs = {}
        if date_gte:
            queryset_filter_kwargs ['date__gte'] = date_gte
        if date_lte:
            queryset_filter_kwargs ['date__lte'] = date_lte
        if processstep_id:
            queryset_filter_kwargs ['processstep_id'] = processstep_id
        if qualitycharacteristics_id:
            queryset_filter_kwargs ['qualitycharacteristics_id'] = qualitycharacteristics_id
        if processparameter_id:
            queryset_filter_kwargs ['processparameter_id'] = processparameter_id
        if processstep_id:
            queryset_filter_kwargs ['processstep_id'] = processstep_id
        if sensor_id:
            queryset_filter_kwargs ['sensor_id'] = sensor_id

        # aggregation if aggregation parameters are provided
        if aggregationWindow_split is not None:

            # query database and convert queryset to pandas.DataFrame for efficient aggregation
            df = pd.DataFrame(list(SensorReading.objects.filter(**queryset_filter_kwargs).order_by('date').only('date', 'value').values()))
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = df['value'].astype(float)
            df = df[['date', 'value']]
            df = df.set_index('date', drop=False)

            # select the correct aggregation function
            if aggregationFcn in ['avg',None]:
                df = df.groupby([pd.Grouper(freq=freq)]).mean()
            elif aggregationFcn == 'min':
                df = df.groupby([pd.Grouper(freq=freq)]).min()
            elif aggregationFcn == 'max':
                df = df.groupby([pd.Grouper(freq=freq)]).max()
            elif aggregationFcn == 'std':
                df = df.groupby([pd.Grouper(freq=freq)]).std()

            # set datetime to iso format
            df.index = df.index.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))

            # delete data points from aggregationWindows without values within
            df['value'].replace('', np.nan, inplace=True)
            df.dropna(subset=['value'], inplace=True)


            data = []
            # create list of dictionaries out of the aggregated data
            for index, row in df.iterrows():
                dictionary = {}
                dictionary['date'] = str(index)
                dictionary['value'] = row['value']
                data.append(dictionary.copy())

            # state additional fields to exclude and paginate the list
            excluded_fields.append('id')
            excluded_fields.append('sensor')
            page = self.paginate_queryset(data)
            if page is not None:
                serializer = SensorReadingSerializer(page, excluded_fields=excluded_fields, context=self.get_serializer_context(), many=True)
                return self.get_paginated_response(serializer.data)
            serializer = SensorReadingSerializer(data, excluded_fields=excluded_fields, context=self.get_serializer_context(), many=True)
            return Response(status=rf_status.HTTP_200_OK, data=serializer.data)

        else:
            # when no aggregationFcn and aggregationWindow are provided
            if aggregationFcn is None:

                queryset = SensorReading.objects.filter(**queryset_filter_kwargs).order_by('date').only('id', 'date', 'value', 'sensor_id')

                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = SensorReadingSerializer(page, excluded_fields=excluded_fields, context=self.get_serializer_context(), many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = SensorReadingSerializer(queryset, excluded_fields=excluded_fields, context=self.get_serializer_context(), many=True)

                return Response(status=rf_status.HTTP_200_OK, data=serializer.data)

            # when aggregationFcn but no aggregation window is provided
            else:
                queryset = SensorReading.objects.filter(**queryset_filter_kwargs).order_by('date').only('date', 'value')
                # convert queryset to pandas.DataFrame for efficient aggregation
                df = pd.DataFrame(list(queryset.values()))
                df = df['value'].astype('float')
                if aggregationFcn == 'avg':
                    df = df.mean()
                elif aggregationFcn == 'min':
                    df = df.min()
                elif aggregationFcn == 'max':
                    df = df.max()
                elif aggregationFcn == 'std':
                    df = df.std()

                return Response(float(df))

    @action(detail=False, methods=["get"])
    def daterange(self, request, *args, **kwargs):
        """Returns the oldest and the youngest date of SensorReading concerning the boundary conditions provided with the url entries.
        Args:
            product_ids (list): ids of the Product instances. At maximum one of product_ids and productspecification_ids. (provided with the url, optional)
            productspecification_ids(list): ids of the ProductSpecificationInstances. At maximum one of product_ids and productspecification_ids. (provided with the url, optional)
            processparameter_ids (list): ids of the ProcessParameterInstances. At maximum one of processparameter_ids and qualitycharacteristics_ids. (provided with the url, optional)
            qualitycharacteristics_ids (list): ids of the QualityCharacteristics. At maximum one of processparameter_ids and qualitycharacteristics_ids. (provided with the url, optional)

        Returns:
            [dict(str)]:
                - firstDate: Date of the sensorreading entry with the oldest date regarding to the given QualityCharacteristic.ids.
                - lastDate: Date of the sensorreading entry with the newest date regarding to the given QualityCharacteristic.ids.
        """

        qualitycharacteristics_ids = request.GET.get("qualitycharacteristics_ids", None)
        processparameter_ids = request.GET.get("processparameter_ids", None)
        productspecification_ids = request.GET.get("productspecification_ids", None)
        product_ids = request.GET.get("product_ids", None)
        if (product_ids is not None and productspecification_ids is not None):
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="product_ids and productspecification_ids were provided. Only one of these parameters is allowed at a time")

        if (processparameter_ids is not None and qualitycharacteristics_ids is not None):
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="processparameter_ids and qualitycharacteristics_ids were provided. Only one of these parameters is allowed at a time")

        # define filter for querying the database
        queryset_filter_kwargs = {}

        if product_ids:
            product_ids = self.url_to_list(product_ids)
            queryset_filter_kwargs ['processstep_id__in'] = list(ProcessStep.objects.filter(product_id__in=product_ids).values_list('id'))
        if productspecification_ids:
            productspecification_ids = self.url_to_list(productspecification_ids)
            processstepspecification_from_productspecification = list(ProcessStepSpecification.objects.filter(productspecification_id__in=productspecification_ids).values_list('id'))
            queryset_filter_kwargs ['processstep_id__in'] = list(ProcessStep.objects.filter(processstepspecification_id__in=processstepspecification_from_productspecification).values_list('id'))
        if qualitycharacteristics_ids:
            queryset_filter_kwargs ['qualitycharacteristics_id__in'] = self.url_to_list(qualitycharacteristics_ids)
        if processparameter_ids:
            queryset_filter_kwargs ['processparameter_id__in'] = self.url_to_list(processparameter_ids)


        last_object = SensorReading.objects.filter(**queryset_filter_kwargs).order_by('date').last()
        first_object = SensorReading.objects.filter(**queryset_filter_kwargs).order_by('date').first()

        first_date = first_object.date if first_object else None
        last_date = last_object.date if last_object else None

        return Response(status=rf_status.HTTP_200_OK, data={"firstDate": first_date, "lastDate": last_date})

    @staticmethod
    def url_to_list(url_list):
        """Returns list derived from list in url.
        Args:
            url_list: list in url
        Returns:
            [list]
        """
        new_list = url_list.strip('[]').replace('"', '').replace(' ', '').split(',')
        new_list =  list(map(int, new_list))
        return new_list

    @action(detail=False, methods=["get"])
    def return_qc_by_product(self, request, *args, **kwargs):
        """Returns list of measured QualityCharacteristics and list of list of predicted QualityCharacteristics that correspond to the given products.
        Args:
            product_list: List of product id
        Returns:
            [list]: measured QualityCharacteristics
            [[list]]: predicted QualityCharacteristics
        """
        product_list = request.GET.get("product_list", None)
        product_list = self.url_to_list(product_list)

        message = []
        # get the data and convert them to dataframe
        processstep_ids = list(ProcessStep.objects.filter(product_id__in=product_list).values_list('id'))
        sensorreadings = SensorReading.objects.exclude(qualitycharacteristics_id__isnull=True).filter(processstep_id__in=processstep_ids).values('value', 'processstep__product__id', 'qualitycharacteristics__id', 'sensor__id', 'sensor__virtual')
        df = pd.DataFrame(list(sensorreadings))
        df  = df.reset_index()
        # split the dataframe in dataframes with values from real respective virtual sensors
        df_real = df[df['sensor__virtual'] == False]
        df_virtual = df[df['sensor__virtual'] == True]
        df_real = df_real.reset_index()
        df_virtual = df_virtual.reset_index()

        # iterate over the QualityCharacteristics
        qc_list = df['qualitycharacteristics__id'].unique()
        qc_list.sort()
        for qc in qc_list:
            # get the corresponding virtual sensors
            sensor_list = df_virtual[df_virtual['qualitycharacteristics__id'] == qc]['sensor__id'].unique()
            measured_list = []
            predicted_list = []
            # iterate over the products  for real values and create a list with values
            for product in product_list:
                temp = df_real[(df_real['processstep__product__id'] == product) & (df_real['qualitycharacteristics__id'] == qc)]['value'].tolist()
                if len(temp) > 0:
                    temp = temp[0]
                else:
                    temp = None
                if isinstance(temp, numbers.Number):
                    measured_list.append(float(temp))
                else:
                    measured_list.append('null')
            # iterate over the sensors for virtual values
            for sensor in sensor_list:
                temp_list = []
                # iterate over the prducts and crate a list with values
                for product in product_list:
                    temp = df_virtual[(df_virtual['processstep__product__id'] == product) & (df_virtual['qualitycharacteristics__id'] == qc) & (df_virtual['sensor__id'] == sensor)]['value'].tolist()
                    if len(temp) > 0:
                        temp = temp[0]
                    else:
                        temp = None
                    if isinstance(temp, numbers.Number):
                        temp_list.append(float(temp))
                    else:
                        temp_list.append('null')
                # create a list of lists from virtual values
                predicted_list.append(temp_list)
            # convert data to json format
            temp_dict = {
                "QualityCharacteristic": qc,
                "measured_values": measured_list,
                "predicted_values": predicted_list
                }
            # append data to the returned message
            message.append(temp_dict)
        return Response(status=rf_status.HTTP_200_OK, data={'results': message})

    @action(detail=False, methods=["get"])
    def update_date(self, request, *args, **kwargs):
        """Updates the date of a given product to a given date. Time is not changed.
        Args:
            product_id: Id of the product whoose dates should be changed.
            year: year of the new date.
            month: Month of the new date.
            day: day of the new date.
            database: database which should be update.
        Returns:

        """

        year = request.GET.get("year", None)
        month = request.GET.get("month", None)
        day = request.GET.get("day", None)
        product_id = request.GET.get("product_id", None)
        database = request.GET.get("database", None)
        if (year is not None) and (month is not None) and (day is not None) and (product_id is not None) and (database is not None):
            message = {
                    "database": database,
                    "year": year,
                    "month": month,
                    "day": day,
                    "product_id": product_id
            }
            update_messages = c_update_date.delay(request=message)
            return Response(status=rf_status.HTTP_200_OK)
        else:
            return Response(status=rf_status.HTTP_400_BAD_REQUEST, data="Not all necessary parameters are provided. Needed: year, month, date, product_id and database")








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
