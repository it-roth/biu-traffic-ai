import io
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .ai_engine import AIEngineUnavailableError
from .models import ViolationRecord


class TrafficScanAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def create_dummy_image(self):
        """Generate dummy JPEG image for testing upload pipelines."""
        file = io.BytesIO()
        image = Image.new('RGB', (640, 480), color=(73, 109, 137))
        image.save(file, 'jpeg')
        file.seek(0)
        return SimpleUploadedFile(
            'test_traffic.jpg',
            file.read(),
            content_type='image/jpeg',
        )

    def test_violations_history_endpoint(self):
        """GET /api/violations/ should return paginated list."""
        ViolationRecord.objects.create(
            file_name='test1.jpg',
            media_type='IMAGE',
            violation_type='NO_HELMET',
            confidence=0.92,
            cars_count=2,
            motorcycles_count=1,
            violations_count=1,
        )
        response = self.client.get('/api/violations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['file_name'], 'test1.jpg')

    def test_scan_image_missing_file(self):
        """POST /api/scan/image/ should return 400 when no file is uploaded."""
        response = self.client.post('/api/scan/image/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_scan_video_missing_file(self):
        """POST /api/scan/video/ should return 400 when no video is uploaded."""
        response = self.client.post('/api/scan/video/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_scan_image_pipeline_execution(self):
        """POST /api/scan/image/ should persist a successful inference result."""
        dummy_file = self.create_dummy_image()
        result = {
            'evidence_crops': [],
            'annotated_media_path': str(Path(settings.MEDIA_ROOT) / 'annotated' / 'result.jpg'),
            'annotated_media_url': '/media/annotated/result.jpg',
            'confidence': 0.92,
            'cars_count': 2,
            'motorcycles_count': 1,
            'violations_count': 1,
            'tuktuk_count': 0,
            'remorque_count': 0,
        }
        with patch('api.views.AIEngine.get_instance') as get_engine:
            get_engine.return_value.process_image.return_value = result
            response = self.client.post(
                '/api/scan/image/',
                {'file': dummy_file},
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('annotated_media_url', response.data)
        self.assertIn('cars_count', response.data)
        self.assertIn('motorcycles_count', response.data)
        self.assertIn('violations_count', response.data)
        self.assertEqual(ViolationRecord.objects.count(), 1)

    def test_scan_image_reports_unavailable_ai_runtime(self):
        """POST /api/scan/image/ should report native runtime failures as 503."""
        dummy_file = self.create_dummy_image()
        with patch(
            'api.views.AIEngine.get_instance',
            side_effect=AIEngineUnavailableError('AI runtime unavailable'),
        ):
            response = self.client.post(
                '/api/scan/image/',
                {'file': dummy_file},
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data['error'], 'AI runtime unavailable')
