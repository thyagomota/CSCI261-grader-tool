# ------------------------------------------------------------------------------- #
# SubmissionsBundle.py - Extracts and verifies student's homework submissions     #
# Author: Thyago Mota (from Yong's AssignmentAmalgamation.rb)                     #
# Date: 06/02/2014                                                                #
# ------------------------------------------------------------------------------- #

import config, zipfile, Submission, os, datetime
from zipfile import ZipFile, BadZipfile
from Submission import Submission
from datetime import datetime

class SubmissionsBundle:
	
	def __init__(self, logging, fileName):
		self.logging = logging
		# checking if zip file is valid
		try:
			self.mainZip = ZipFile(fileName)
		except Exception, ex: 
			self.logging.error(str(ex))
			raise ex
		# obtaining homework number
		msg = 'Extracting submissions for homework ' + str(config.HOMEWORK_NUMBER)
		self.logging.info(msg)		
		print(msg)
		# obtaining due date
		self.dueDate = datetime.strptime(config.HOMEWORK_DUE_DATE + ' 08:00:00', '%Y-%m-%d %H:%M:%S')
		self.logging.info('Due date for homework ' + str(config.HOMEWORK_NUMBER) + ' is ' + str(self.dueDate))			
		
	# returns a list of Submission objects
	def submissions(self):
		count = 0
		submissions = []
		for name in self.mainZip.namelist():
			if count % 2 == 0:
				submissionPair = [name, '']
			else:
				submissionPair[1] = name
				submission = Submission(submissionPair)				
				submissions.append(submission)
			count += 1
		return submissions
		
	# extracts a student's submission
	def extract(self, submission):
		try:
			# create main submission folder if doesn't exist
			if not os.path.exists(config.EXTRACTION_FOLDER): 
				os.makedirs(config.EXTRACTION_FOLDER)
			# create student's folder 
			path = config.EXTRACTION_FOLDER + '/' + submission.studentId + '/'
			if not os.path.exists(path): 
				os.makedirs(path)
			# extract submission file
			self.mainZip.extract(submission.fileNameLong, path)
			# rename it using its short name
			os.rename(path + submission.fileNameLong, path + submission.fileNameShort)
			# check if its a zip file, flag the submission and report warning otherwise
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
				submission.status = Submission.STATUS_BAD_ZIP
				self.logging.warning('bad zip file in ' + submission.studentId + '\'s submission!')
				return False
		except Exception, ex:
			msg = str(ex) + '!'
			self.logging.error(msg)
			raise Exception(msg)
			
	# verify submission format and due date
	def verify(self, submission):
		# check if submission is past due
		if submission.dateTime > self.dueDate:
			submission.status = Submission.STATUS_LATE
			self.logging.warning(submission.studentId + '\'s submission is past due!')
			return False
		# check proper format
		try:
			path = config.EXTRACTION_FOLDER + '/' + submission.studentId + '/'
			if not os.path.isdir(path + 'src'):
				submission.status = Submission.STATUS_NO_SRC
				self.logging.warning('no src folder in ' + submission.studentId + '\'s submission!')
				return False
			dirList = os.listdir(path + 'src')
			for file in dirList:
				if os.path.isdir(file):
					submission.status = Submission.STATUS_BAD_SRC
					self.logging.warning('bad src folder in ' + submission.studentId + '\'s submission!')
					return False
				fileName, fileExtension = os.path.splitext(file)
				fileExtension = fileExtension.lower()
				if fileExtension != '.cpp' and fileExtension != '.h':
					submission.status = Submission.STATUS_BAD_SRC
					self.logging.warning('bad src folder in ' + submission.studentId + '\'s submission!')
					return False
				# create tograde folder if doesn't exist
				if not os.path.exists(config.TO_GRADE_FOLDER): 
					os.makedirs(config.TO_GRADE_FOLDER)
				# move student's submission folder
				os.rename(path, config.TO_GRADE_FOLDER + '/' + submission.studentId + '/')
				return True
		except Exception, ex:
			msg = str(ex) + '!'
			self.logging.error(msg)
			raise Exception(msg)	
				
	def extractAll(self):
		submissions = self.submissions()
		count = 0
		for submission in submissions:
			if self.extract(submission):
				if self.verify(submission):
					count += 1				
		self.mainZip.close()		
		msg = str(count) + ' homework submissions were valid'		
		self.logging.info(msg)
		print(msg)