import os
import argparse

from playsound import playsound
from google.cloud import vision
from google.oauth2 import service_account


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio_file", help="The path to the audio file to play")
    ap.add_argument("image_path", help="The image file from the motion detection camera")
    ap.add_argument("labels_to_detect", help="A comma separated list of object labels to activate the audio")
    ap.add_argument("service_account_file", help="The path to the Google cloud vision service account json",
                    default=os.path.expanduser("~/seagullscarer_service_account.json"))

    args = ap.parse_args()

    labels_to_detect = set(args.labels_to_detect.split(","))

    # Initialize the Google cloud vision client
    client = get_cloud_vision_client(args.service_account_file)

    # Test whether the labels are in the image
    if detected_labels(client, args.image_path, labels_to_detect):
        playsound(os.path.abspath(args.audio_file))


def get_cloud_vision_client(service_account_file):
    """
    Initialize a Google Cloud Vision client using the service account file
    :param service_account_file The service account file
    :return:
    """
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    client = vision.ImageAnnotatorClient(credentials=credentials)
    return client


def detected_labels(client, image_path, labels_to_detect):
    """
    Determine whether labels are in the image
    :client Google cloud vision client
    :image_path The path to the image
    :labels_to_detect A set of labels we are looking for in the image
    """
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.label_detection(image=image)
    found_labels = {label.description.lower() for label in response.label_annotations}

    return len(found_labels.intersection(labels_to_detect)) > 0


if __name__ == '__main__':
  main()