from rest_framework import serializers
from .models import TrafficViolation, ViolationRecord


class ViolationRecordSerializer(serializers.ModelSerializer):
    """Serializer for persisted traffic violation records and scan outputs."""

    evidence_crop_url = serializers.SerializerMethodField()
    annotated_media_url = serializers.SerializerMethodField()

    class Meta:
        model = ViolationRecord
        fields = (
            'id',
            'file_name',
            'media_type',
            'violation_type',
            'confidence',
            'evidence_crop',
            'evidence_crop_url',
            'annotated_media',
            'annotated_media_url',
            'cars_count',
            'motorcycles_count',
            'violations_count',
            'created_at',
        )

    def get_evidence_crop_url(self, obj):
        if not obj.evidence_crop:
            return None
        request = self.context.get('request')
        url = obj.evidence_crop.url
        return request.build_absolute_uri(url) if request else url

    def get_annotated_media_url(self, obj):
        if not obj.annotated_media:
            return None
        request = self.context.get('request')
        url = obj.annotated_media.url
        return request.build_absolute_uri(url) if request else url


class TrafficViolationSerializer(serializers.ModelSerializer):
    """Legacy serializer for streaming detections."""

    crop_image_url = serializers.SerializerMethodField()

    class Meta:
        model = TrafficViolation
        fields = ('id', 'detected_at', 'vehicle_type', 'confidence', 'track_id', 'crop_image_url')

    def get_crop_image_url(self, obj):
        if not obj.crop_image:
            return None
        request = self.context.get('request')
        url = obj.crop_image.url
        return request.build_absolute_uri(url) if request else url
