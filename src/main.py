import os
import logging
from flask import Flask, render_template
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobPrefix
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)

dotenv_path = find_dotenv(filename='.env')
load_dotenv(dotenv_path=dotenv_path)

_SaUrl=os.getenv('SERVICE_ACCOUNT_URL').strip()
_BlobName=os.getenv('BLOB_NAME').strip()

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

def list_blobs_flat(blob_service_client: BlobServiceClient, container_name):
  blobs = []
  container_client = blob_service_client.get_container_client(container=container_name)
  blob_list = container_client.list_blobs()
  for blob in blob_list:
    logging.info("Name: {blobname}".format(blobname=blob.name))
    blobs.append(blob.name)

  return blob

def main():
  logging.basicConfig(filename='app.log', level=logging.INFO)
  logging.info("start testapp")
  app.run()

if __name__ == '__main__':
  main()
