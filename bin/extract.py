# ------------------------------------------------------------------------------- #
# extract.py - homework extracting tool for CSCI 261 @ CSM                        #
# Expects only one homework submissions bundle file in the current working folder #
# Author: Thyago Mota (from Yong's grade.rb)                                      #
# Date: 06/02/14                                                                  #
# Last Update: 08/26/14                                                           #
# ------------------------------------------------------------------------------- #

import glob, config, logging, datetime, os, shutil
from glob import glob
from datetime import datetime
import SubmissionsBundle
from SubmissionsBundle import SubmissionsBundle

# setting logging configuration
if os.path.exists(config.LOG_FOLDER + '/' + config.EXTRACT_LOG_FILE):
	os.remove(config.LOG_FOLDER + '/' + config.EXTRACT_LOG_FILE)
logging.basicConfig(filename=config.LOG_FOLDER + '/' + config.EXTRACT_LOG_FILE, level=logging.INFO)
msg = 'Homework submissions extracting tool started @ ' + str(datetime.now())
print(msg)
logging.info(msg) 

# checking if one and only one zip file exists in the current working folder
list = glob('*.zip')
if not list:
	msg = 'no zip file to grade!'
	logging.error(msg)
	raise Exception(msg)
elif len(list) > 1:
	msg = '> 1 zip file to grade!'
	logging.error(msg)
	raise Exception(msg)
fileName = list[0]
logging.info(fileName + ' will be graded.')

# removing previously extracted submissions
if os.path.exists(config.EXTRACTION_FOLDER):
	shutil.rmtree(config.EXTRACTION_FOLDER)
if os.path.exists(config.TO_GRADE_FOLDER):
	shutil.rmtree(config.TO_GRADE_FOLDER)

# extracting students' submissions
submissions = SubmissionsBundle(logging, fileName)
submissions.extractAll()

# ending 
msg = 'Homework submissions extracting tool ended   @ ' + str(datetime.now())
print(msg)
logging.info(msg) 
print('Log file is ' + config.LOG_FOLDER + '/' + config.EXTRACT_LOG_FILE)