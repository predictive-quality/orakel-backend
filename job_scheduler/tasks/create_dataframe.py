# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from orakel.models import DataFrame, Product, ProcessStep, ProcessStepSpecification, SensorReading

from celery import Task
from job_scheduler import job_scheduler

import pandas as pd
import numpy as np

from django.db.models import Min, Max, Avg, StdDev, When, Case, IntegerField, Value
from django.core.exceptions import ValidationError

from s3_smart_open import to_pd_fth

from pyarrow import feather  # Avoid local import error of s3_smart_open

import time


class CreateDataframe(Task):
    """Celery task to create a pandas DataFrame from SensorReading instances.

    Raises:
        ValidationError: When methods_per_feature values are not one of [Min,Max,Avg,StdDev]

    Returns:
        [Exception]: Returns Exception Message if an error occurs.
    """
    name = "Create_pd.DataFrame"
    ignore_result = False # Will save the return value / Task result in the database.
    decription = "Create a pandas DataFrame from sensorreadings."
    queue = "large_task"

    # Use .using(self.db) for every queryset!

    def __call__(self, pk, database_name, methods_per_feature , product_ids=None,*args, **kwargs):
        """Set initial values and call the run method.

        Args:
            pk (int): pirmary key of the dataframe instance.
            database_name (str): Name of the database where the dataframe object is stored
            methods_per_feature (list[str]: Methods that are applied on the features.

        Raises:
            ValidationError: If methods_per_feature elements are implemented / not in decode_methods_per_feature.keys().

        Returns:
            [None or errors]: returns result from the run method
        """
        self.pk = pk
        self.db = database_name
        # Wethere to create a dataframe to check the correctness of the method. The process can take a very long time!
        self.validate_processparameter_df = False
        self.decode_methods_per_feature = { "Min": Min('value'),
                                            "Max": Max('value'),
                                            "Avg": Avg('value'),
                                            "StdDev": StdDev('value'),
                                            }
        # Validate the methods that are applied to the processparameter/qualitycharacteristics. If StackedDataFrame is listed as method no methods will be applied to the features and dataframes for timseries analysis will be created..
        self.tsfresh_bool = False
        for method in methods_per_feature:
            if method == "StackedDataFrame":
                self.tsfresh_bool = True
                break
            elif method not in self.decode_methods_per_feature.keys():
                DataFrame.objects.using(self.db).filter(pk=self.pk).update(**{"status": "Failed"})
                raise ValidationError("Provided Method is None of {}".format(self.decode_methods_per_feature.keys()))
        # Only apply each method one time per feature
        self.methods_per_feature = set(methods_per_feature)

        return self.run(product_ids=product_ids, *args, **kwargs)

    @staticmethod
    def sort_sensorreadings(processsteps, unsorted):
        """Sort an unsorted list with the order of processstep, sensorreading pairs.

        Args:
            processsteps (list[int]): orderd processstep ids which predefine the order of the sensorreading values
            unsorted (list[tuples]):  (processstep id, sensorreading value) pairs

        Returns:
            [list[float]]: ordered list of sensorreading values
        """
        assert len(processsteps) == len(unsorted)
        objects = dict(unsorted)
        return [objects[x] for x in processsteps]

    def feature_methods_on_sensorreadings(self, sr_queryset, method):
        """Apply Django Aggregations on the given queryset.

        Args:
            sr_queryset ([type]): queryset of sensorreading instances
            method (object): One of Min('value'),Max(...),Avg(...),StdDev(...) to apply on the queryset.

        Returns:
            [list[tuple]]: Returns [(sensorreading value, processstep id)...]
        """
        return sr_queryset.annotate(self.decode_methods_per_feature.get(method)).values_list('processstep', 'value')

    def create_processparameter_dataframe(self, processparameter):
        """Creates a dataframe built with products ids and processparameter names.
        Args:
            processparameter (list[objects]): List of processparameter objects that define the columns in context with the methods

        Returns:
            [pd.DataFrame]: Pandas DataFrame that contains the values of the methods thate are applied on the sensorreading values.
        """
        # Generate processparameter columns with
        pp_columns = []
        for pp in processparameter:
            pp_columns.extend([str(pp) + x for x in self.methods_per_feature])

        # Optional for debugging and time comparison
        startTime = time.perf_counter()
        # Allocate memory for the dataframe
        df_pp = pd.DataFrame(None, index=self.product_ids, columns=pp_columns).astype('float64')


        for pp in processparameter:
            # Get sensorreading objects. ProcessParameter(one) --> ProcessStepSpecifcation(one) --> processsteps(several, descending ordered by product ids) --> unordered sensorreading instances.
            processstepspec = ProcessStepSpecification.objects.using(self.db).filter(processparameter=pp).values_list('id', flat=True)[0]
            processsteps = ProcessStep.objects.using(self.db).filter(product__in=self.product_ids, processstepspecification=processstepspec).order_by('-product_id').values_list('pk', flat=True)
            unsorted_sr_queryset = SensorReading.objects.using(self.db).filter(processstep__in=processsteps, processparameter=pp).all()
            # Apply each method on the processparameter and sort them using the ordered processsteps.
            for method in self.methods_per_feature:
                unsorted = self.feature_methods_on_sensorreadings(unsorted_sr_queryset, method)
                df_pp[str(pp)+method] = self.sort_sensorreadings(processsteps, unsorted)

        # Optional for debugging and time comparison
        print('Elapsed time: {:6.3f} seconds df_pp'.format(time.perf_counter() - startTime))

        # Much slower way, but 100% secure way to build the dataframe.
        # Serves to compare it with the processparameter dataframe.
        if self.validate_processparameter_df:
            pp_columns_validation = []
            for pp in processparameter:
                pp_columns_validation.extend([str(pp) + x for x in ['Min','Max','Avg','StdDev']])
            validation_df = pd.DataFrame(None, index=self.product_ids, columns=pp_columns_validation).astype('float64')
            startTime = time.perf_counter()
            for iter, row in validation_df.iterrows():
                    product = row.name
                    pp_counter = 0
                    for pp in processparameter:
                        processstepspec = ProcessStepSpecification.objects.using(self.db).filter(processparameter=pp).values_list('id', flat=True)[0]
                        processstep = ProcessStep.objects.using(self.db).filter(product=product, processstepspecification=processstepspec).values_list('pk', flat=True)[0]
                        sr = SensorReading.objects.using(self.db).filter(processstep=processstep, processparameter=pp).aggregate(Min('value'),Max('value'),Avg('value'), StdDev('value'))
                        row[pp_counter+0] = sr.get('value__min')
                        row[pp_counter+1] = sr.get('value__max')
                        row[pp_counter+2] = sr.get('value__avg')
                        row[pp_counter+3] = sr.get('value__avg')
                        pp_counter +=4

            print('Elapsed time: {:6.3f} seconds validation_df'.format(time.perf_counter() - startTime))
            to_pd_fth(self.save_path, "validation_df.fth", validation_df)

        return df_pp

    def create_processparameter_timeseries(self, processparameter):
        """Creates a dataframe in tsfresh format for timeseries analysis built with products ids and processparameter names.
        Args:
            processparameter (list[objects]): List of processparameter objects that define the columns in context with the methods

        Returns:
            [pd.DataFrame]: Pandas DataFrame that contains values by product (id), processparameter (kind) and date (time).
        """

        # Optional for debugging and time comparison
        startTime = time.perf_counter()
        # Get sensorreading objects. ProcessParameter(one) --> ProcessStepSpecifcation(one) --> processsteps(several, descending ordered by product ids) --> unordered sensorreading instances.
        processstepspec = ProcessStepSpecification.objects.using(self.db).filter(processparameter__in=processparameter).values_list('id', flat=True)[0]
        processsteps = ProcessStep.objects.using(self.db).filter(product__in=self.product_ids, processstepspecification=processstepspec).order_by('-product_id').values_list('pk', flat=True)
        unsorted_sr_queryset = SensorReading.objects.using(self.db).filter(processstep__in=processsteps, processparameter__in=processparameter).all()

        # Annotate each sensorreading with the corresponding product id.
        processsteps_dict = dict((o.pk, o.product_id) for o in ProcessStep.objects.using(self.db).filter(product__in=self.product_ids, processstepspecification=processstepspec).only('pk','product_id'))
        whens = [When(processstep_id=int(k), then=Value(v)) for k, v in processsteps_dict.items()]
        unsorted_sr_queryset = unsorted_sr_queryset.annotate(product_id=Case(*whens, output_field=IntegerField(), default=Value(0)))
        # Sort queryset
        sr_queryset = unsorted_sr_queryset.order_by('product_id', 'processparameter', 'date')
        sr_queryset = sr_queryset.values('product_id', 'date', 'processparameter_id', 'value')
        # create DataFrame from Queryset
        df_pp = pd.DataFrame(sr_queryset)
        # rename columns to match tsfresh format
        df_pp = df_pp.rename(columns={'product_id':'id', 'date':'time', 'processparameter_id':'kind'})
        # rearrange column ordering
        df_pp = df_pp[['id','time','kind','value']]
        # Optional for debugging and time comparison
        print('Elapsed time: {:6.3f} seconds df_pp'.format(time.perf_counter() - startTime))

        return df_pp

    def create_qualiycharacteristics_dataframe(self, qualitycharacteristics, target):
        """Creates a dataframe built with products ids and qualitycharacteristics/target_value names.
        Args:
            qualitycharacteristics (list[objects]): List of qualitycharacteristics objects that define the columns in context with the methods or the target_values

        Returns:
            [pd.DataFrame]: target=False: Pandas DataFrame that contains the values of the methods thate are applied on the sensorreading values.
            [pd.DataFrame]: target=True: Pandas DataFrame that contains the sensorreading values of the target_value (qualitycharacteristic).
        """
        # Create the columns for the dataframe
        if target:
            qc_columns = [str(x) for x in qualitycharacteristics]
        else:
            qc_columns = []
            for qc in qualitycharacteristics:
                qc_columns.extend([str(qc) + "_" + x for x in self.methods_per_feature])

        df_qc = pd.DataFrame(None, index=self.product_ids, columns=qc_columns).astype('float64')
        # Get sensorreading objects. QualityCharacteristics(one) --> ProcessStepSpecifcation(one) --> ProcessSteps(several, descending ordered by product ids) --> unordered SensorReading objects.
        for qc in qualitycharacteristics:
            processstepspec = ProcessStepSpecification.objects.using(self.db).filter(qualitycharacteristics=qc).values_list('id', flat=True)[0]
            processsteps = ProcessStep.objects.using(self.db).filter(product__in=self.product_ids, processstepspecification=processstepspec).order_by('-product_id').values_list('pk', flat=True)
            unsorted_sr_queryset = SensorReading.objects.using(self.db).filter(processstep__in=processsteps, qualitycharacteristics=qc).all()
            # Wether to create the target_dataframe (y) or create features from the qualitycharacteristics and methods.
            if target:
                df_qc[str(qc)] = self.sort_sensorreadings(processsteps, unsorted_sr_queryset.values_list('processstep', 'value'))
            else:
                # Apply each method on the processparameter and sort them using the ordered processsteps.
                for method in self.methods_per_feature:
                    unsorted = self.feature_methods_on_sensorreadings(unsorted_sr_queryset, method)
                    df_qc[str(qc)+method] = self.sort_sensorreadings(processsteps, unsorted)

        return df_qc

    def create_target_timeseries(self, qualitycharacteristics):
        """Creates a dataframe with target values for timeseries analysis. Rows are the Products, columns are the QualityCharacteristics (first column is product id).
        Args:
            qualitycharacteristics (list[objects]): List of qualitycharacteristics objects that define the columns in context with the methods

        Returns:
            [pd.DataFrame]: Pandas DataFrame that contains values by product (id), qualitycharacteristic (kind) and date (time).
        """

        # Optional for debugging and time comparison
        startTime = time.perf_counter()
        # Get sensorreading objects. QualityCharacteristics(one) --> ProcessStepSpecifcation(one) --> processsteps(several, descending ordered by product ids) --> unordered sensorreading instances.
        processstepspec = ProcessStepSpecification.objects.using(self.db).filter(qualitycharacteristics__in=qualitycharacteristics).values_list('id', flat=True)[0]
        processsteps = ProcessStep.objects.using(self.db).filter(product__in=self.product_ids, processstepspecification=processstepspec).order_by('-product_id').values_list('pk', flat=True)
        unsorted_sr_queryset = SensorReading.objects.using(self.db).filter(processstep__in=processsteps, qualitycharacteristics__in=qualitycharacteristics).all()

        # Annotate each sensorreading with the corresponding product id.
        processsteps_dict = dict((o.pk, o.product_id) for o in ProcessStep.objects.using(self.db).filter(product__in=self.product_ids, processstepspecification=processstepspec).only('pk','product_id'))
        whens = [When(processstep_id=int(k), then=Value(v)) for k, v in processsteps_dict.items()]
        unsorted_sr_queryset = unsorted_sr_queryset.annotate(product_id=Case(*whens, output_field=IntegerField(), default=Value(0)))
        # Sort queryset
        sr_queryset = unsorted_sr_queryset.order_by('product_id', 'qualitycharacteristics', 'date')
        sr_queryset = sr_queryset.values('product_id', 'date', 'qualitycharacteristics_id', 'value')
        # create DataFrame from Queryset
        df_qc = pd.DataFrame(sr_queryset)
        # rename columns to match tsfresh format
        df_qc = df_qc.rename(columns={'product_id':'id', 'date':'time', 'qualitycharacteristics_id':'kind'})
        # create empty DataFrame in correct output format
        column_names = df_qc['kind'].unique()
        df_target = pd.DataFrame(columns=column_names)
        # fill the DataFrame with values
        for product in df_qc['id'].unique():
            values = []
            for column in column_names:
                temp = list(df_qc.loc[(df_qc['id']==product) & (df_qc['kind']==column), 'value'])
                if temp:
                    values.append(df_qc.loc[(df_qc['id']==product) & (df_qc['kind']==column), 'value'].values[0])
                else:
                    values.append(np.NaN)
            values = [values]
            df_target = df_target.append(pd.DataFrame(values, columns=column_names, index=[product]))
        # set index of DataFrame as column id containing the product ids
        df_target['id'] = df_target.index
        # rearrange column ordering
        product_id = df_target['id']
        df_target.drop(labels=['id'], axis=1,inplace = True)
        df_target.insert(0, 'id', product_id)


        # Optional for debugging and time comparison
        print('Elapsed time: {:6.3f} seconds df_qc'.format(time.perf_counter() - startTime))

        return df_target

    def run(self, product_ids=None, *args, **kwargs):
        """Creation of the dataframes.

        Returns:
            [None or error]: if an error occurs, the error message will be returned. Else None.
        """
        try:
            DataFrame.objects.using(self.db).filter(pk=self.pk).update(**{"status": "Running"})

            # Get attributes from the dataframe object
            df = DataFrame.objects.using(self.db).get(pk=self.pk)
            processparameter = list(df.processparameter.all())
            qualitycharacteristics = list(df.qualitycharacteristics.all())
            target_value = list(df.target_value.all())
            self.save_path = df.save_path
            rows = df.product_amount
            random_r = df.random_records

            # Get product ids
            if not product_ids:
                # Get all product ids that match to the productspecification and the processstepspecifications.
                processsteps_ids =  ProcessStep.objects.using(self.db).filter(processstepspecification__in=df.processstepspecification.all()).distinct().values_list('pk', flat=True)
                products_ids = Product.objects.using(self.db).filter(productspecification=df.productspecification.pk, processstep__in=processsteps_ids).distinct().values_list('pk', flat=True)
                product_ids = np.array(products_ids)
            # Use given product ids
            else:
                product_ids = np.array(product_ids)

            # Shortens the product ids array if more products are available than defined by dataframe.product_amount.
            # Get random products ids if specified.
            if rows < product_ids.shape[0]:
                if random_r:
                    product_ids = np.random.choice(product_ids, rows, replace=False)
                else:
                    product_ids = product_ids[:rows]

            # Set descending order
            product_ids.sort()
            self.product_ids = np.flip(product_ids)


            # Check, whether aggregation is applied or data for time series are returned.
            if not self.tsfresh_bool:

                # Create a dataframe with features from the processparameters.
                if processparameter:
                    df_pp_bool = True
                    df_pp = self.create_processparameter_dataframe(processparameter=processparameter)
                else:
                    df_pp_bool = False

                # Create a dataframe with features from the qualitycharacteristics.
                if qualitycharacteristics:
                    df_qc_bool = True
                    df_qc = self.create_qualiycharacteristics_dataframe(qualitycharacteristics=qualitycharacteristics, target=False)
                else:
                    df_qc_bool = False

                # Create a dataframe with targets from the target_value(qualitycharacteristics).
                if target_value:
                    df_target_bool = True
                    df_target = self.create_qualiycharacteristics_dataframe(qualitycharacteristics=target_value, target=True)
                else:
                    df_target_bool = False

            else:
                # Create a dataframe in tsfresh format with features from the processparameters.
                if processparameter:
                    df_pp_bool = True
                    df_pp = self.create_processparameter_timeseries(processparameter=processparameter)
                else:
                    df_pp_bool = False

                # as quality characteristics are no timeseries they would not appear in input data
                df_qc_bool = False

                # Create a dataframe with targets from the target_value(qualitycharacteristics).
                if target_value:
                    df_target_bool = True
                    df_target = self.create_target_timeseries(qualitycharacteristics=target_value)
                else:
                    df_target_bool = False

            # Check if nessesary dataframes were created and update status.
            if (not df_pp_bool and not df_qc_bool) or not df_target_bool:
                DataFrame.objects.using(self.db).filter(pk=self.pk).update(**{"status": "Failed"})
                return

            # Merge processparameter_featuers dataframe and quality_features dataframe in order to save them as one dataframe.
            if df_pp_bool and df_qc_bool:
                to_pd_fth(output_path=self.save_path, filename="x.fth", dataframe=pd.merge(df_pp, df_qc, left_index=True, right_index=True))
            elif df_pp_bool:
                to_pd_fth(output_path=self.save_path, filename="x.fth", dataframe=df_pp)
            elif df_qc_bool:
                to_pd_fth(output_path=self.save_path, filename="x.fth", dataframe=df_qc)
            else:
                DataFrame.objects.using(self.db).filter(pk=self.pk).update(**{"status": "Failed"})

            # Save the target dataframe.
            to_pd_fth(output_path=self.save_path, filename="y.fth", dataframe=df_target)
            # Update the dataframe status
            DataFrame.objects.using(self.db).filter(pk=self.pk).update(**{"status": "Succeeded"})
            return None
        except Exception as e:
            DataFrame.objects.using(self.db).filter(pk=self.pk).update(**{"status": "Failed"})
            raise e



# Register the task
job_scheduler.tasks.register(CreateDataframe())
