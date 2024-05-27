import wget
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download model')
    parser.add_argument('-m', '--model', type=str, required=True, help='Model name')
    args = parser.parse_args()

    model_link = f"http://download.tensorflow.org/models/object_detection/tf2/20200711/{args.model}.tar.gz"
    wget.download(model_link)
    import tarfile
    tar = tarfile.open(f"{args.model}.tar.gz")
    tar.extractall('.')
    tar.close()

# Sample Command to start script
#  python .\model_downloader.py -m ssd_mobilenet_v2_320x320_coco17_tpu-8