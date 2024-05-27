from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.dispatch import receiver
import uuid
import os
import numpy as np
import cv2


def generate_file_name_uuid(instance=None, filename=None):
    return str(uuid.uuid4())


class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    boxes_count = models.IntegerField()
    score_threshold = models.FloatField()
    image_height = models.IntegerField()
    image_width = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)
    original_filename = models.CharField(max_length=1000, default=None)
    original_file = models.FileField(default=None, upload_to=generate_file_name_uuid)
    result_file = models.FileField(default=None, upload_to=generate_file_name_uuid)
    
    class Meta:
        verbose_name_plural = "Analyses"
    
    
    def create(
        user_id,
        image_original_request_file,
        detections_np,
        image_result_array,
        category_index_items,
        boxes_count=1,
        score_threshold=0.2
    ):
        result_file_bytes = _convert_np_result_image_to_rgb_bytes(
            image_result_array,
            os.path.splitext(image_original_request_file.name)[1]
        )
        analysis = Analysis(
            user_id=user_id,
            boxes_count=boxes_count,
            score_threshold=score_threshold,
            image_height=image_result_array.shape[0],
            image_width=image_result_array.shape[1],
            original_filename=image_original_request_file.name,
            original_file=image_original_request_file,
            result_file=ContentFile(result_file_bytes, generate_file_name_uuid())
        )
        
        analysis.save()
        
        analysis.__set_clean_detections(
            detections_np,
            category_index_items,
            image_result_array.shape[0],
            image_result_array.shape[1],
            boxes_count,
            score_threshold)
        
        return analysis
    
    
    def update(
        self,
        detections_np,
        image_result_array,
        category_index_items,
        boxes_count=1,
        score_threshold=0.2
    ):
        result_file_bytes = _convert_np_result_image_to_rgb_bytes(
            image_result_array,
            os.path.splitext(self.original_filename)[1]
        )
        
        self.boxes_count = boxes_count
        self.score_threshold = score_threshold
        self.result_file.save(generate_file_name_uuid, ContentFile(result_file_bytes))
        
        self.save()
        
        self.detectedanimal_set.all().delete()
        
        self.__set_clean_detections(
            detections_np,
            category_index_items,
            image_result_array.shape[0],
            image_result_array.shape[1],
            boxes_count,
            score_threshold)
        
    
    def to_dict(self):
        return {
            "id": self.pk,
            "metadata": {
                "boxes_count": self.boxes_count,
                "score_threshold": self.score_threshold,
                "image_height": self.image_height,
                "image_width": self.image_width,
                "timestamp": self.timestamp,
                "filename": self.original_filename,
            },
            "objects": [{
                "score": detection.score,
                "class": detection.breed,
                "species": detection.species,
                "coordinates": {
                    "start": {
                        "x": detection.start_x,
                        "y": detection.start_y
                    },
                    "end": {
                        "x": detection.end_x,
                        "y": detection.end_y
                    }
                }
            } for detection in self.detectedanimal_set.all()]
            
        }
    
    
    def __set_clean_detections(
        self,
        detections_np,
        category_index_items,
        image_height,
        image_width,
        boxes_count,
        score_threshold
    ):
        detections = _get_clean_detections(
            detections_np,
            category_index_items,
            boxes_count,
            score_threshold,
            image_height,
            image_width
        )
        
        for detection in detections:
            self.detectedanimal_set.create(
                score=detection['score'],
                breed=detection['class'],
                species=detection['species'],
                start_x=detection['coordinates']['start']['x'],
                start_y=detection['coordinates']['start']['y'],
                end_x=detection['coordinates']['end']['x'],
                end_y=detection['coordinates']['end']['y'],
            )
        

@receiver(models.signals.pre_delete, sender=Analysis)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.original_file and instance.original_file.storage.exists(instance.original_file.name):
        instance.original_file.delete()
    
    if instance.result_file and instance.result_file.storage.exists(instance.result_file.name):
        instance.result_file.delete()
        
    return True

@receiver(models.signals.pre_save, sender=Analysis)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_analysis = Analysis.objects.get(pk=instance.pk)
        
        old_original_file = old_analysis.original_file
        new_original_file = instance.original_file
        if not(old_original_file == new_original_file) and old_original_file and old_original_file.name and old_original_file.storage.exists(old_original_file.name):
            old_original_file.delete()
            
        old_result_file = old_analysis.result_file
        new_result_file = instance.result_file
        if not(old_result_file == new_result_file) and old_result_file and old_result_file.name and old_result_file.storage.exists(old_result_file.name):
            old_result_file.delete()
            
        return True
    except Analysis.DoesNotExist:
        return False

class DetectedAnimal(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    score = models.FloatField()
    breed = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    start_x = models.FloatField()
    start_y = models.FloatField()
    end_x = models.FloatField()
    end_y = models.FloatField()
    
    class Meta:
        verbose_name_plural = "Detected animals"
    

def _convert_np_result_image_to_rgb_bytes(image_array, extension='.jpg'):
    result_image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    return cv2.imencode(extension, result_image_rgb)[1].tobytes()
    
    
def _get_clean_detections(data, category_index_items, boxes_count, score_threshold, image_height, image_width):
    indices = np.argsort(data['detection_scores'])[::-1]
    indices_good = indices[data['detection_scores'] > score_threshold]
    indices_good = indices_good[:boxes_count]
    scores = data['detection_scores'][indices_good]
    class_ids = list(data['detection_classes'][indices_good])
    category_items = [category_index_items[id] for id in class_ids]
    boxes = data['detection_boxes'][indices_good]
    zipped_data = zip(scores, category_items, boxes)
    data_clean = [_get_detection_object_as_dict(score, ci, box, image_height, image_width) for score, ci, box in zipped_data]
    return data_clean


def _get_detection_object_as_dict(score, category_item, box, image_height, image_width):
    return {
        'score': score,
        'class': category_item['breed'],
        'species': category_item['species'],
        'coordinates': {
            'start': {
                'x': box[1] * image_width,
                'y': box[0] * image_height
            },
            'end': {
                'x': box[3] * image_width,
                'y': box[2] * image_height
            }
        }
    }