from flask import Flask, request
import os
import asyncio

app = Flask(__name__)
UPLOAD_FOLDER = "sessions"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@shimorra телеграм - полный доступ
