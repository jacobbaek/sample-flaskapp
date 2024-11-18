import os, sys
import logging
import uuid

from flask import Flask, render_template
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient, BlobPrefix
from dotenv import load_dotenv, find_dotenv

#logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger('azure.identity')
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('[%(levelname)s %(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)

if os.environ.get('STORAGE_ACCOUNT_URL') == None: 
  logging.warning("load .env")
  dotenv_path = find_dotenv(filename='.env')
  if not os.path.exists(dotenv_path):
    logging.error(f".env file({dotenv_path}) not found")
    sys.exit()
  load_dotenv(dotenv_path=dotenv_path)

_SaUrl=os.getenv('STORAGE_ACCOUNT_URL').strip()
_BlobName=os.getenv('BLOB_NAME').strip()

@app.route('/')
def root():
  return render_template("index.html")

@app.route('/usemi')
def usemi():
  blobsc = BlobServiceClient(_SaUrl, DefaultAzureCredential(exclude_workload_identity_credential=True))
  blobs = list_blobs_flat(blobsc, _BlobName)
  if blobs == None:
    return render_template("error.html")
  return render_template("storages.html", blobs=blobs)

@app.route('/usewi')
def usewi():
  blobsc = BlobServiceClient(_SaUrl, credential=DefaultAzureCredential(exclude_managed_identity_credential=True))
  blobs = list_blobs_flat(blobsc, _BlobName)
  if blobs == None:
    return render_template("error.html")
  return render_template("storages.html", blobs=blobs)

def create_container(blob_service_client: BlobServiceClient, container_name):
  container_name = str(uuid.uuid4())
  container_client = blob_service_client.create_container(container_name)
  logging.warning(f"trying to create container {container_name}")
 
def list_blobs_flat(blob_service_client: BlobServiceClient, container_name):
  blobs = []

  try:
    container_client = blob_service_client.get_container_client(container=container_name)
    logging.warning(f"trying to get bloblist for ({container_name})")
    blob_list = container_client.list_blobs()
    for blob in blob_list:
      logging.info(f"Name: {blob.name}")
      blobs.append(blob.name)
    print(blobs)
  except Exception as e:
    logger.critical("blob error : ", e)
    return None

  return blobs

def main():
  logging.info("start testapp")
  app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
  main()
