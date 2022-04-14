# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from django.contrib import admin
from orakel import models


@admin.register(models.QualityCharacteristics)
class QualityCharacteristicsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.ProcessParameter)
class ProcessParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.ShopFloor)
class ShopFloorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25


@admin.register(models.Machine)
class MachineAdminAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 20

@admin.register(models.Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.ProcessStepSpecification)
class ProcessStepSpecificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('pk',)
    list_per_page = 25

@admin.register(models.ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.PreProduct)
class PreProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    list_per_page = 25


@admin.register(models.MachineLearningRun)
class MachineLearningRunAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.DataFrame)
class DataFrameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.PipelineBlock)
class PipelineBlockAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.MachineLearningRunSpecification)
class MachineLearningRunSpecificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25

@admin.register(models.PipelineBlockSpecification)
class PipelineBlockSpecificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 25
