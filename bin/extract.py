# ------------------------------------------------------------------------------- #
# extract.py - homework extracting tool for CSCI 261 @ CSM                        #
# Configuration options are set in config.py                                      #
# Author: Thyago Mota (from Yong's grade.rb)                                      #
# ------------------------------------------------------------------------------- #

import glob, config, logging, datetime, os, shutil, sys, zipfile
from glob import glob
from datetime import datetime
from zipfile import ZipFile, BadZipfile

# show grading info
print('This is the homework submissions extracting tool version: ' + str(config.VERSION) + '.' + str(config.BUILD))
print('Script started @ ' + datetime.now().strftime('%H:%M:%S'))
sys.stdout.write('Grading for ' + config.COURSE + ' (' + config.SEMESTER + ')')
sys.stdout.write('- section(s): ')
print[(section + ' ') for section in config.SECTIONS]
sys.stdout.write('Homework ' + str(config.HOMEWORK_NUMBER).zfill(2) + ' - ')
dueDate = datetime.strptime(config.HOMEWORK_DUE_DATE, '%Y-%m-%d %H:%M:%S')
sys.stdout.write('due date is ' + str(dueDate) + ' - ')			
lateDate = datetime.strptime(config.HOMEWORK_LATE_DATE, '%Y-%m-%d %H:%M:%S')
print('later due date is ' + str(lateDate))			

# check for main extraction folder
if not os.path.exists(config.EXTRACTION_FOLDER):
	os.makedirs(config.EXTRACTION_FOLDER)				

# main loop
for section in config.SECTIONS:
	print('-' * 85)
	print('Section ' + section)
	# check for section folder
	sectionPath = os.path.join(config.EXTRACTION_FOLDER, section)
	if not os.path.exists(sectionPath):
		os.makedirs(sectionPath)				
	# look for section zip bundle file	
	sectionZipfilePrefix = 'gradebook_' + config.SEMESTER + '-' + config.COURSE + section + '_' + config.ASSIGNMENTS_PREFIX + config.SEPARATOR_CHARACTER + str(config.HOMEWORK_NUMBER).zfill(2)
	list = glob(os.path.join(config.ZIP_FILES_FOLDER, sectionZipfilePrefix + '*.zip'))
	if not list:
		print('No submission bundle file found!')
	elif len(list) > 1:
		print('> 1 submission bundle file match!')
	else:
		# section zip bundle file was found!
		sectionZipfileName = list[0]
		print('Found \'' + sectionZipfileName + '\'')
		fields = sectionZipfileName.split('_')
		sectionDatetime = datetime.strptime(fields[3].split('.')[0], '%Y-%m-%d-%H-%M-%S')
		# print('Date: ' + sectionDatetime.strftime('%Y-%m-%d') + ' - Time: ' + sectionDatetime.strftime('%H:%M:%S'))
		try:
			# open section zip bundle file
			sectionZipfile = ZipFile(sectionZipfileName)
			# check destination folders
			baseSubmissionFolder = os.path.join(config.EXTRACTION_FOLDER, section, str(config.HOMEWORK_NUMBER).zfill(2))
			if os.path.exists(baseSubmissionFolder):
				shutil.rmtree(baseSubmissionFolder)				
			os.makedirs(baseSubmissionFolder)		
			os.makedirs(os.path.join(baseSubmissionFolder, config.INVALID_FOLDER))							
			os.makedirs(os.path.join(baseSubmissionFolder, config.ON_TIME_FOLDER))							
			os.makedirs(os.path.join(baseSubmissionFolder, config.LATE_FOLDER))
			# create CSV file
			csvFile = open(os.path.join(baseSubmissionFolder, config.CSV_FILE_NAME), 'wt')
			# extract submissions
			stats = [0] * 3
			for submissionOriginalFileName in sectionZipfile.namelist():
				# ignore any submission with an extension other than zip
				extension = os.path.splitext(submissionOriginalFileName)[1].lower()
				if extension != '.zip':
					continue
				# get submission info
				fields = submissionOriginalFileName.split('_')
				studentId = fields[1]
				submissionDate = datetime.strptime(fields[3], '%Y-%m-%d-%H-%M-%S')
				submissionFileName = fields[4]
				# create invalid submission folder for the student
				submissionInvalidFolder = os.path.join(baseSubmissionFolder, config.INVALID_FOLDER, studentId)
				os.makedirs(submissionInvalidFolder)							
				# extract and rename submission
				sectionZipfile.extract(submissionOriginalFileName, submissionInvalidFolder)
				submissionNewFileName = os.path.join(submissionInvalidFolder, 'src' + str(config.HOMEWORK_NUMBER).zfill(2) + '.zip')
				os.rename(os.path.join(submissionInvalidFolder, submissionOriginalFileName), submissionNewFileName)
				try:
					# extract student's submission
					studentZipFile = ZipFile(submissionNewFileName)
					for fileName in studentZipFile.namelist():
						studentZipFile.extract(fileName, submissionInvalidFolder)
					# close student's submission
					studentZipFile.close()
					# move all source files to the root 
					hasSource = False
					for root, dirs, files in os.walk(submissionInvalidFolder):
						for name in files:
							fileName = os.path.join(root, name)
							extension = os.path.splitext(fileName)[1].lower()
							if extension in config.ACCEPTED_FILE_EXTENSIONS:
								if extension in config.SOURCE_FILE_EXTENSIONS:
									hasSource = True
								if root != submissionInvalidFolder:
									shutil.copyfile(fileName, os.path.join(submissionInvalidFolder, name))					
					# final clean up
					for name in os.listdir(submissionInvalidFolder):
						nameWithPath = os.path.join(submissionInvalidFolder, name)
						if os.path.isdir(nameWithPath):
							shutil.rmtree(nameWithPath)
						elif nameWithPath == submissionNewFileName:
							continue
						else:
							extension = os.path.splitext(name)[1].lower()
							if extension not in config.ACCEPTED_FILE_EXTENSIONS:
								os.remove(nameWithPath)
					# moving submission to the correct submission folder (if needed)
					if hasSource:
						# on time? 
						if submissionDate <= dueDate:	
							os.rename(submissionInvalidFolder, os.path.join(baseSubmissionFolder, config.ON_TIME_FOLDER, studentId))
							csvFile.write(studentId + ',' + '\n')
							stats[0] += 1
						# late submission?
						elif submissionDate <= lateDate:
							os.rename(submissionInvalidFolder, os.path.join(baseSubmissionFolder, config.LATE_FOLDER, studentId))
							csvFile.write(studentId + ',late' + '\n')
							stats[1] += 1
					else:
						csvFile.write(studentId + ',no source' + '\n')
						stats[2] += 1
				except Exception, ex2:
					csvFile.write(studentId + ',problems with zip' + '\n')
					stats[2] += 1
			# close section zip bundle file
			sectionZipfile.close()
			print(str(sum(stats)) + ' submission(s) extracted: {' + str(stats[0]) + ' on time; ' + str(stats[1]) + ' late; ' + str(stats[2]) + ' invalid}')
			csvFile.close()
		except Exception, ex: 
			print('Submission file bundle is invalid!')		

# script ends
print('-' * 85)
print('Script ended @ ' + datetime.now().strftime('%H:%M:%S'))
print('Goodbye :-)')