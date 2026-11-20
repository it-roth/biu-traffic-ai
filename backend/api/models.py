from django.db import models


class ViolationRecord(models.Model):
    """
    Stores detected traffic violations from image and video inference scans.
    Tracks vehicle counts, confidence scores, and media output paths.
    """

    class MediaType(models.TextChoices):
        IMAGE = 'IMAGE', 'Image'
        VIDEO = 'VIDEO', 'Video'

    file_name = models.CharField(max_length=255)
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    violation_type = models.CharField(max_length=50, default='NO_HELMET')
    confidence = models.FloatField(default=0.0)
    evidence_crop = models.ImageField(upload_to='crops/', blank=True, null=True)
    annotated_media = models.FileField(upload_to='annotated/', blank=True, null=True)
    cars_count = models.IntegerField(default=0)
    motorcycles_count = models.IntegerField(default=0)
    violations_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('-created_at',)),
        ]

    def __str__(self):
        return f"{self.violation_type} in {self.file_name} ({self.created_at:%Y-%m-%d %H:%M})"


# Retain legacy model for backwards compatibility with existing database tables
class TrafficViolation(models.Model):
    class VehicleType(models.TextChoices):
        MOTORCYCLE = 'motorcycle', 'Motorcycle'
        CAR = 'car', 'Car'
        UNKNOWN = 'unknown', 'Unknown'

    detected_at = models.DateTimeField(auto_now_add=True)
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.MOTORCYCLE,
    )
    confidence = models.FloatField()
    track_id = models.PositiveIntegerField(null=True, blank=True)
    crop_image = models.ImageField(upload_to='violations/%Y/%m/%d/')

    class Meta:
        ordering = ('-detected_at',)
        indexes = [models.Index(fields=('-detected_at',))]

    def __str__(self):
        return f'{self.vehicle_type} violation at {self.detected_at:%Y-%m-%d %H:%M:%S}'
