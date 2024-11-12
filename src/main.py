import os, sys
import logging
from flask import Flask, render_template
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobPrefix
from dotenv import load_dotenv, find_dotenv

#logging.basicConfig(filename='app.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("azure.identity")
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
_ManagedIdentityID=os.getenv('MI_ID').strip()

@app.route('/')
def root():
  return render_template("index.html")

@app.route('/usemi')
def usemi():
  cred = DefaultAzureCredential(exclude_workload_identity_credential=True)
  blobsc = BlobServiceClient(_SaUrl, credential=cred)
  blobs = list_blobs_flat(blobsc, _BlobName)
  return render_template("storages.html", blobs=blobs)

@app.route('/usewi')
def usewi():
  cred = DefaultAzureCredential(exclude_managed_identity_credential=True)
  blobsc = BlobServiceClient(_SaUrl, credential=cred)
  blobs = list_blobs_flat(blobsc, _BlobName)
  return render_template("storages.html", blobs=blobs)

@app.route('/usemi-clientid')
def usemi_clientid():
  cred = DefaultAzureCredential(managed_identity_client_id=_ManagedIdentityID)
  blobsc = BlobServiceClient(_SaUrl, credential=cred)
  blobs = list_blobs_flat(blobsc, _BlobName)
  return render_template("storages.html", blobs=blobs)

def list_blobs_flat(blob_service_client: BlobServiceClient, container_name):
  blobs = []
  container_client = blob_service_client.get_container_client(container=container_name)
  blob_list = container_client.list_blobs()
  for blob in blob_list:
    logging.info("Name: {blobname}".format(blobname=blob.name))
    blobs.append(blob.name)

  return blob

def main():
  logging.info("start testapp")
  app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
  main()
