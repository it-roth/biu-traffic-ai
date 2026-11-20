from django.urls import path
from .views import (
    ScanImageView,
    ScanVideoView,
    TrafficViolationListView,
    ViolationRecordListView,
    hello,
    traffic_stats,
    traffic_stream,
    traffic_stream_stop,
)

urlpatterns = [
    # Core Traffic Safety Enforcement Scan Endpoints
    path('scan/image/', ScanImageView.as_view(), name='scan-image'),
    path('scan/video/', ScanVideoView.as_view(), name='scan-video'),
    path('violations/', ViolationRecordListView.as_view(), name='violations-list'),

    # Health & Live Stream Routes
    path('hello/', hello, name='hello'),
    path('traffic/violations/', TrafficViolationListView.as_view(), name='traffic-violations'),
    path('traffic/stats/', traffic_stats, name='traffic-stats'),
    path('traffic/stream/', traffic_stream, name='traffic-stream'),
    path('traffic/stream/stop/', traffic_stream_stop, name='traffic-stream-stop'),
]
