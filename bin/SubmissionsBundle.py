# ------------------------------------------------------------------------------- #
# SubmissionsBundle.py - Extracts and verifies student's homework submissions     #
# Author: Thyago Mota (from Yong's AssignmentAmalgamation.rb)                     #
# Date: 06/02/2014                                                                #
# Last update: 08/28/14                                                           #
# ------------------------------------------------------------------------------- #

import config, zipfile, Submission, os, datetime, shutil
from zipfile import ZipFile, BadZipfile
from Submission import Submission
from datetime import datetime

# SubmissionsBundle class
class SubmissionsBundle:

	# __init__
	def __init__(self, logging, fileName):
		self.logging = logging
		# checking if zip file is valid
		try:
			self.mainZip = ZipFile(fileName)
		except Exception, ex: 
			msg = fileName + ' zip file is corrupted!'
			self.logging.error(msg)
			raise ex
		# obtaining homework number
		msg = 'Extracting submissions for homework ' + str(config.HOMEWORK_NUMBER)
		self.logging.info(msg)		
		print(msg)
		self.correctName = 'src' + str(config.HOMEWORK_NUMBER).zfill(2) + '.zip'
		# checking whether zip bundle file is for the same homework number
		fields = fileName.split('_')
		id = int(fields[2][len(fields[2])-2:])
		if id != config.HOMEWORK_NUMBER:
			msg = 'submission file ' + fileName + ' does not match homework number!'
			self.logging.error(msg)
			raise Exception(msg)
		print('Section is ' + fields[1])
		# obtaining due date
		self.dueDate = datetime.strptime(config.HOMEWORK_DUE_DATE, '%Y-%m-%d %H:%M:%S')
		self.logging.info('Due date for homework ' + str(config.HOMEWORK_NUMBER) + ' is ' + str(self.dueDate))			
		# obtaining late date
		self.lateDate = datetime.strptime(config.HOMEWORK_LATE_DATE, '%Y-%m-%d %H:%M:%S')
		self.logging.info('Late date for homework ' + str(config.HOMEWORK_NUMBER) + ' is ' + str(self.lateDate))			
		
	# 
	# extension - returns the extension of a file
	def extension(self, fileName):
		return fileName[fileName.rfind('.')+1:].lower()
		
	# submissions - returns a list of Submission objects
	def submissions(self):
		submissions = []
		for fileName in self.mainZip.namelist():
			# ignore any submission with an extension other than zip
			if self.extension(fileName) != 'zip':
				continue
			submission = Submission(fileName)				
			submissions.append(submission)
		return submissions
		
	# extract - extracts a student's submission
	def extract(self, submission):
		try:
			# create student's folder in the extraction folder
			path = config.EXTRACTION_FOLDER + '/' + config.INVALID_FOLDER + '/' + submission.studentId + '/'
			if not os.path.exists(path): 
				os.makedirs(path)
			# extract submission file
			self.mainZip.extract(submission.fileName, path)
			# rename it using the short name
			os.rename(path + submission.fileName, path + submission.fileNameShort)
			# check if submission follows the correct format
			if submission.fileNameShort != self.correctName:
				self.logging.warning(submission.fileNameShort + ' in ' + submission.studentId + '\'s submission does not follow the correct format!')
				return False
			else:			
				# check if the zip file is not corrupted
				try:
					submittedZip = ZipFile(path + submission.fileNameShort)	
					# OK, the file is zipped, let's try to extract all of its contents
					for name in submittedZip.namelist():
						submittedZip.extract(name, path)
					submittedZip.close()
					# remove the zip file
					os.remove(path + submission.fileNameShort)
					return True
				except Exception, ex:
					self.logging.warning('zip file in ' + submission.studentId + '\'s submission appears to be corrupted!')
					return False
		except Exception, ex:
			msg = str(ex) + '!'
			self.logging.error(msg)
			raise Exception(msg)
			
	# verify - verify submission format and due date
	def verify(self, submission):
		# check if submission is past due
		if submission.dateTime > self.lateDate:
			self.logging.warning(submission.studentId + '\'s submission is past due!')
			return False
		# check proper format
		try:
			path = config.EXTRACTION_FOLDER + '/' + config.INVALID_FOLDER + '/' + submission.studentId + '/'
			if not os.path.isdir(path + 'src'):
				self.logging.warning('no src folder was found in ' + submission.studentId + '\'s submission!')
				return False
			dirList = os.listdir(path + 'src')
			for file in dirList:
				if os.path.isdir(file):
					self.logging.warning('an unexpected subfolder was found in ' + submission.studentId + '\'s src submission!')
					return False
				fileName, fileExtension = os.path.splitext(file)
				fileExtension = fileExtension.lower()
				if fileExtension != '.cpp' and fileExtension != '.h':
					self.logging.warning('unexpected file(s) was(were) found in ' + submission.studentId + '\'s src submission!')
					return False
				# everything looking good -> move student's submission folder
				if submission.dateTime < self.dueDate:
					os.rename(path, config.EXTRACTION_FOLDER + '/' + config.ON_TIME_FOLDER + '/' + submission.studentId + '/')
				else:	
					os.rename(path, config.EXTRACTION_FOLDER + '/' + config.LATE_FOLDER + '/' + submission.studentId + '/')
				return True
		except Exception, ex:
			msg = str(ex) + '!'
			self.logging.error(msg)
			raise Exception(msg)	
	
	# extractAll - extract all submissions
	def extractAll(self):
		# create a list of all submission objects
		submissions = self.submissions()
		count = 0
		for submission in submissions:
			if self.extract(submission):
				if self.verify(submission):
					count += 1				
		self.mainZip.close()		
		msg = str(count) + ' out of ' + str(len(submissions)) + ' homework submission(s) was(were) valid'
		self.logging.info(msg)
		print(msg)