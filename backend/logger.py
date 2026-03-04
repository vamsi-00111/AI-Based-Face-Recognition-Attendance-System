import logging
import os
from pathlib import Path
import CONFIG
from datetime import datetime

#definig logging path and making it
log_dir=os.path.join(CONFIG.ParentDir,"logs")
os.makedirs(log_dir,exist_ok=True)

#defining logging file path
time=datetime.now().strftime("%d:%m:%Y-%H:%M:%S")
log_file_path=os.path.join(log_dir,f"{time}log")

logger=logging.getLogger(__name__)
formatter=logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
logger.setLevel(logging.DEBUG)
        

#defining file handler
file_handler=logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

#definig stream handler
stream_handler=logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
stream_handler.setFormatter(formatter)

#adding handlers
logger.addHandler(file_handler)
logger.addHandler(stream_handler)