import numpy as np
import argparse
import tensorflow as tf
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1

# Patch the location of gfile
tf.gfile = tf.io.gfile


def _load_image_bytes_from_file(path: str):
    return tf.io.gfile.GFile(path, 'rb').read()


def _load_image_as_array(img_data: bytes):
    image = Image.open(BytesIO(img_data))
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


def _run_inference_for_single_image(model, image):
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5, tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    return output_dict


def _run_inference_internal(model, category_index, image_bytes, boxes_count=1, score_threshold=0.4):
    image_np = _load_image_as_array(image_bytes)
    image_np_with_detections = image_np.copy()
    
    # Actual detection.
    output_dict = _run_inference_for_single_image(model, image_np)
    
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        max_boxes_to_draw=boxes_count,
        min_score_thresh=score_threshold,
        line_thickness=8)
    plt.imshow(image_np_with_detections)
    return output_dict, image_np_with_detections


def run_inference(model, category_index, image, boxes_count=1, score_threshold=0.4):
    if (type(model) == str):
        model = tf.saved_model.load(model)
        
    if (type(category_index) == str):
        category_index = label_map_util.create_category_index_from_labelmap(category_index, use_display_name=True)
        
    if (type(image) == str):
        image = _load_image_bytes_from_file(image)
    
    return _run_inference_internal(model, category_index, image, boxes_count, score_threshold)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detect objects in an image')
    parser.add_argument('-m', '--model', type=str, required=True, help='Model Path')
    parser.add_argument('-l', '--labelmap', type=str, required=True, help='Path to Labelmap')
    parser.add_argument('-i', '--image_path', type=str, required=True, help='Path to image (or folder)')
    args = parser.parse_args()

    run_inference(args.model, args.labelmap, args.image_path)
    
    plt.savefig("detection_output.png")  
    plt.show()

# Sample Command to start script
#  python .\detect_from_images.py -m ssd_mobilenet_v2_320x320_coco17_tpu-8\saved_model -l .\data\mscoco_label_map.pbtxt -i .\test_images
