from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import get_object_or_404
import traceback
import json
import os
from .models import Analysis
from .constants import BOXES_COUNT_DEFAULT, SCORE_THRESHOLD_DEFAULT
from tfod.detect_from_image import run_inference as execute_detection
from tfod.label_map_utils import read_label_map


@login_required(login_url="/users/unauthenticated")
@csrf_exempt
def run_analysis(request):
    if request.method == 'POST':  
        if not(request.FILES) or not('image' in request.FILES):
            return JsonResponse({"error": 'No image provided'}, status=400)
    
        image = request.FILES['image']
        if (image.size > int(10e8)):
            traceback.print_exc()
            return JsonResponse({"error": 'The provided image has size over 100 MB and such images are not accepted'}, status=400)
        
        image_bytes = _read_image_as_bytes(image)
        
        try:
            boxes_count, score_threshold = _extract_detection_params_from_request(request.POST)
        except:
            traceback.print_exc()
            return JsonResponse({"error": 'The provided parameters for detection (score threshold or boxes count) have invalid values'}, status=400)
            
        try:
            detections, result_img = execute_detection(
                settings.OBJECT_DETECTION_MODEL_PATH,
                settings.OBJECT_DETECTION_LABEL_MAP_PATH,
                image_bytes,
                boxes_count,
                score_threshold
            )
            
            category_index_items = read_label_map(settings.OBJECT_DETECTION_LABEL_MAP_PATH)
            analysis = Analysis.create(
                request.user.pk,
                image,
                detections,
                result_img,
                category_index_items,
                boxes_count,
                score_threshold
            )
            
            return JsonResponse({'id': analysis.pk}, status=200)
        except:
            traceback.print_exc()
            raise

@login_required(login_url="/users/unauthenticated")
@csrf_exempt
def rerun_analysis(request, id):
    if request.method == 'PUT':  
        analysis = get_object_or_404(Analysis, id=id)
        image_bytes = _read_image_as_bytes(analysis.original_file)
        
        if (analysis.user != request.user):
            return JsonResponse({"error": 'You cannot rerun an analysis of another user'}, status=401)
        
        try:
            body = json.loads(request.body)
            boxes_count, score_threshold = _extract_detection_params_from_request(body)
        except:
            traceback.print_exc()
            return JsonResponse({"error": 'The provided parameters for detection (score threshold or boxes count) have invalid values'}, status=400)
        
        try:
            detections, result_img = execute_detection(
                settings.OBJECT_DETECTION_MODEL_PATH,
                settings.OBJECT_DETECTION_LABEL_MAP_PATH,
                image_bytes,
                boxes_count,
                score_threshold
            )
            
            category_index_items = read_label_map(settings.OBJECT_DETECTION_LABEL_MAP_PATH)
            
            analysis.update(
                detections,
                result_img,
                category_index_items,
                boxes_count,
                score_threshold
            )
            
            return JsonResponse({'success': True}, status=200)
        except:
            traceback.print_exc()
            raise


@login_required(login_url="/users/unauthenticated") 
@csrf_exempt
def analysis_detail(request, id):
    analysis = get_object_or_404(Analysis, id=id)
    
    if (analysis.user != request.user):
        return JsonResponse({"error": 'You cannot perform operations on an analysis of another user'}, status=401)
    
    try:
        if request.method == 'GET':
            return JsonResponse(analysis.to_dict(), status=200)
            
        if request.method == 'DELETE':
            analysis.delete()
            return JsonResponse({'success': True}, status=200)
    except:
        traceback.print_exc()
        return JsonResponse({"error": 'Could complete the requested operation'}, status=500)


@login_required(login_url="/users/unauthenticated")
@csrf_exempt
def image_original(request, id):
    analysis = get_object_or_404(Analysis, id=id)
    
    if (analysis.user != request.user):
        return JsonResponse({"error": 'You cannot view images from an analysis of another user'}, status=401)
    
    if request.method == 'GET':
        try:
            extension = os.path.splitext(analysis.original_filename)[1].replace('.', '')
            return HttpResponse(analysis.original_file, content_type='image/' + extension)
        except:
            traceback.print_exc()
            return JsonResponse({"error": 'Could not retrieve image'}, status=500)
        

@login_required(login_url="/users/unauthenticated") 
@csrf_exempt
def image_result(request, id):
    analysis = get_object_or_404(Analysis, id=id)
    
    if (analysis.user != request.user):
        return JsonResponse({"error": 'You cannot view images from an analysis of another user'}, status=401)
    
    if request.method == 'GET':
        try:
            extension = os.path.splitext(analysis.original_filename)[1].replace('.', '')
            return HttpResponse(analysis.result_file, content_type='image/' + extension)
        except:
            traceback.print_exc()
            return JsonResponse({"error": 'Could not retrieve image'}, status=500)
    

@login_required(login_url="/users/unauthenticated")
@csrf_exempt
def analyses_overview(request):
    if request.method == 'GET':
        try:
            analyses = [analysis.to_dict() for analysis in request.user.analysis_set.all()]
            return JsonResponse({'analyses': analyses}, status=200)
        except:
            traceback.print_exc()
            return JsonResponse({"error": 'Could not retrieve analyses'}, status=500)


def _extract_detection_params_from_request(request_object):
    boxes_count = int(request_object['boxes_count']) if 'boxes_count' in request_object else BOXES_COUNT_DEFAULT
    score_threshold = float(request_object['score_threshold']) if 'score_threshold' in request_object else SCORE_THRESHOLD_DEFAULT
    return boxes_count, score_threshold


def _read_image_as_bytes(image):
    image_bytes = bytes()
    for chunk in image.chunks():
        image_bytes += chunk[0:len(chunk)]
            
    return image_bytes
