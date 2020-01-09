"""ccomptes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework import routers

from comment.views import CommentsView, FrameCommentsView, IndicatorCommentsView
from open_anafi import views

router = routers.SimpleRouter()

router.register(r'comments/app', CommentsView)
router.register(r'comments/indicators', IndicatorCommentsView)
router.register(r'comments/frames', FrameCommentsView)
router.register(r'variables', views.VariableViewsSet)
router.register(r'indicators/parameters', views.IndicatorParameterViewsSet)
router.register(r'frames', views.FrameViewsSet)
router.register(r'nomenclatures', views.NomenclatureViewsSet)
router.register(r'translation_table', views.TranslationTableEstablismentTypeViewsSet)
router.register(r'departments', views.DepartmentViews)
router.register(r'institutions', views.InstitutionTypeViews)
router.register(r'indicators', views.IndicatorViews, base_name = 'indicators')
router.register(r'identifier_types', views.IdentifierTypeViews)

urlpatterns = [
    path('users/authenticate/', views.UsersViews.as_view()),
    path('equation/parse/', views.IndicatorViews.as_view({'post': 'check_equation'})),
    path('identifiers/', views.IdentifierViews.as_view()),
    path('reports/', views.ReportViews.as_view()),
    path('reports/<int:pk>/', views.ReportGetViews.as_view()),
    path('reports/<int:pk>/download/', views.ReportDownloadViews.as_view()),
    path('reports/balances/', views.BalanceViews.as_view()),
    path('reports/aggregates/', views.AggregatedReportViews.as_view()),
    path('frames/<int:pk>/indicators/', views.IndicatorFrameView.as_view()),
    path('downloadframe/<int:pk>/', views.FrameDownloadViews.as_view()),
    path('downloadframelight/<int:pk>/', views.FrameDownloadLightViews.as_view()),
    path('indicators/<int:pk>/libelles/', views.IndicatorLibelleView.as_view()),
    path('libelles/', views.LibelleView.as_view()),
    path('indicators/parameters/<int:pk>/tree/', views.IndicatorParameterViewsSet.as_view({'get': 'generate_tree'}))
]

urlpatterns += router.urls
