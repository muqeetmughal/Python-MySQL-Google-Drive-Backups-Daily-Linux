import configparser
import os
import time
import getpass
from dataclasses import fields
from google.auth.transport.requests import Request
import os
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import os
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
#-----------------------------------------------------------------------
"""
Will backup all the databases listed, will put files in same DIR as script'
To run: $ python dbbackup.py OR python3 dbbackup.py
"""
foldername = "dbbackups"
try:
    os.mkdir(foldername)
except:
    pass


def get_dump(database):

    HOST='localhost'
    PORT='3306'
    DB_USER='root'
    DB_PASS='12345678'

    # HOST='localhost'
    # PORT='3306'
    # DB_USER='aun'
    # DB_PASS='1234'

    # if using one database... ('database1',)
    # databases=['hesk']

    filestamp = time.strftime('%Y-%m-%d-%I')
    filepath = foldername+"/"+database+"_"+filestamp
    # D:/xampp/mysql/bin/mysqldump for xamp windows
    os.popen("mysqldump -h %s -P %s -u %s -p%s %s > %s.sql" % (HOST,PORT,DB_USER,DB_PASS,database,filepath))
    
    print("\n|| Database dumped to "+database+"_"+filestamp+".sql || ")


#-----------------------------------------------------------------------

def google_drive_backup_init():
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    creds = None

    if os.path.exists(os.path.join(BASE_DIR, "token.json")):
        creds = Credentials.from_authorized_user_file(os.path.join(BASE_DIR, "token.json"), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(BASE_DIR, "credentials.json"), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(BASE_DIR, "token.json"),"w") as token:
            token.write(creds.to_json())



    try:
        service = build("drive","v3", credentials=creds)

        response = service.files().list(
            q="name='BackupFolder2022' and mimeType='application/vnd.google-apps.folder'", spaces='drive'
        ).execute()


        if not response['files']:
            file_metadata = {
                "name" : "BackupFolder2022",
                "mimeType" : "application/vnd.google-apps.folder"
            }
            file = service.files().create(body=file_metadata, fields="id").execute()

            folder_id = file.get('id')
        else:
            folder_id = response['files'][0]['id']

        for file in os.listdir(foldername):
            file_metadata = {
                "name" : file,
                "parents" : [folder_id]
            }
            media = MediaFileUpload(os.path.join(BASE_DIR, foldername,file))
            upload_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            print("backed up file : ", upload_file)

    except HttpError as e:
        print("Error: ", str(e))




if __name__=="__main__":
    print(BASE_DIR)
    get_dump('hesk')
    google_drive_backup_init()