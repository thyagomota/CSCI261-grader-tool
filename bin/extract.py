# ------------------------------------------------------------------------------- #
# extract.py - homework extracting tool for CSCI 261 @ CSM                        #
# Expects only one homework submissions bundle file in the current working folder #
# Author: Thyago Mota (from Yong's grade.rb)                                      #
# Date: 06/02/14                                                                  #
# Last Update: 09/02/14                                                           #
# ------------------------------------------------------------------------------- #

import glob, config, logging, datetime, os, shutil
from glob import glob
from datetime import datetime
import SubmissionsBundle
from SubmissionsBundle import SubmissionsBundle

# script begins
print('Homework submissions extracting tool started @ ' + str(datetime.now()))

# checking if ONE and only ONE zip file exists in the current working folder
list = glob('*.zip')
if not list:
	raise Exception('no zip file to grade!')
elif len(list) > 1:
	raise Exception('> 1 zip file to grade!')
fileName = list[0]
print(fileName + ' will be graded.')

# removing previously extracted submissions
if os.path.exists(config.EXTRACTION_FOLDER):
	shutil.rmtree(config.EXTRACTION_FOLDER)
os.makedirs(config.EXTRACTION_FOLDER)
os.makedirs(config.EXTRACTION_FOLDER + '/' + config.INVALID_FOLDER)
os.makedirs(config.EXTRACTION_FOLDER + '/' + config.ON_TIME_FOLDER)
os.makedirs(config.EXTRACTION_FOLDER + '/' + config.LATE_FOLDER)

# extracting students' submissions
submissions = SubmissionsBundle(fileName)
submissions.extractAll()

# script ends
print('Homework submissions extracting tool ended @ ' + str(datetime.now()))