from rest_framework import routers
from orakel import views


router =  routers.DefaultRouter()

router.register('event', viewset=views.EventViewSet, basename='event')
router.register('machine', viewset=views.MachineViewSet, basename='machine')
router.register('operator', viewset=views.OperatorViewSet, basename='operator')
router.register('processparameter', viewset=views.ProcessParameterViewSet, basename='processparameter')
router.register('processstep', viewset=views.ProcessStepViewSet, basename='processstep')
router.register('processstepspecification', viewset=views.ProcessStepSpecificationViewSet, basename='processstepspecification')
router.register('product', viewset=views.ProductViewSet, basename='product')
router.register('preproduct', viewset=views.PreProductViewSet, basename='preproduct')
router.register('productspecification', viewset=views.ProductSpecificationViewSet, basename='productspecification')
router.register('qualitycharacteristics', viewset=views.QualityCharacteristicsViewSet, basename='qualitycharacteristics')
router.register('sensor', viewset=views.SensorViewSet, basename='sensor')
router.register('sensorreading', viewset=views.SensorReadingViewSet, basename='sensorreading')
router.register('shopfloor', viewset=views.ShopFloorViewSet, basename='shopfloor')
router.register('tool', viewset=views.ToolViewSet, basename='tool')
router.register('dataframe',viewset=views.DataFrameViewSet, basename='dataframe')
router.register('machinelearningrun',viewset=views.MachineLearningRunViewSet, basename='machinelearningrun')
router.register('pipelineblock',viewset=views.PipeLineBlockViewSet, basename='pipelineblock')
router.register('pipelineblockspecification',viewset=views.PipeLineBlockSpecificationViewSet, basename='pipelineblockspecification')
router.register('machinelearningrunspecification',viewset=views.MachineLearningRunSpecificationViewSet, basename='machinelearningrunspecification')
router.register('importfixtures', viewset=views.ImportFixturesViewSet, basename='importfixtures')


urlpatterns = router.urls
