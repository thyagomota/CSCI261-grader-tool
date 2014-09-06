# ------------------------------------------------------------------------------- #
# SubmissionsBundle.py - Extracts and verifies student's homework submissions     #
# Author: Thyago Mota (from Yong's AssignmentAmalgamation.rb)                     #
# Date: 06/02/2014                                                                #
# Last update: 09/05/14                                                           #
# ------------------------------------------------------------------------------- #

import config, zipfile, Submission, os, datetime, shutil
from zipfile import ZipFile, BadZipfile
from Submission import Submission
from datetime import datetime

# SubmissionsBundle class
class SubmissionsBundle:

	# __init__ (constructor)
	def __init__(self, fileName):
	
		# checking whether zip file is valid
		try:
			self.mainZip = ZipFile(fileName)
		except Exception, ex: 
			raise ex
			
		# obtaining homework number
		print('Extracting submissions for homework ' + str(config.HOMEWORK_NUMBER))
		self.correctName = 'src' + str(config.HOMEWORK_NUMBER).zfill(2) + '.zip'
		print('Expecting submissions using format \'' + self.correctName)
		
		# checking whether zip bundle file is for the same homework number
		fields = fileName.split('_')
		id = int(fields[2][len(fields[2])-2:])
		if id != config.HOMEWORK_NUMBER:
			raise Exception('submission file ' + fileName + ' does not match homework number!')
		print('Grading for section ' + fields[1])
		
		# obtaining 1st due date
		self.dueDate = datetime.strptime(config.HOMEWORK_DUE_DATE, '%Y-%m-%d %H:%M:%S')
		print('1st due date for homework ' + str(config.HOMEWORK_NUMBER) + ' is ' + str(self.dueDate))			
		
		# obtaining 2nd due date ('late date')
		self.lateDate = datetime.strptime(config.HOMEWORK_LATE_DATE, '%Y-%m-%d %H:%M:%S')
		print('2nd due date for homework ' + str(config.HOMEWORK_NUMBER) + ' is ' + str(self.lateDate))			
		
		# opening csv file
		try:
			self.csvFile = open(config.EXTRACTION_FOLDER + '/' + config.CSV_FILE, 'wt')
		except Exception, ex:
			raise ex
		
	# extension - returns the extension given a file name
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
			
			# rename it using the expected correct name
			os.rename(path + submission.fileName, path + self.correctName)			
			
			# check if the zip file is not corrupted
			try:
				submittedZip = ZipFile(path + self.correctName)	
					
				# OK, the zip file is OK, let's extract its contents
				for name in submittedZip.namelist():
					submittedZip.extract(name, path)

				# close and remove the zip file
				submittedZip.close()
				# os.remove(path + self.correctName)
					
				return True
			except Exception, ex:
				return False
		except Exception, ex:
			raise ex
			
	# verify - verify submission format and due date
	def verify(self, submission):
		# check if submission is past due
		if submission.dateTime > self.lateDate:
			self.csvFile.write(submission.studentId + ',\"submission is past due!\"\n')
			return False
			
		# check proper format
		try:
			path = config.EXTRACTION_FOLDER + '/' + config.INVALID_FOLDER + '/' + submission.studentId + '/'
			
			# looking for source folder and valid C++ code
			dirList = os.listdir(path)
			hasSrc = False
			for name in dirList:
				# there's a folder...
				if os.path.isdir(path + name):
					# rename it to lower case
					os.rename(path + name, path + name.lower())
					# is it a source folder? 
					if name[:3] == 'src' or name == 'src' + str(config.HOMEWORK_NUMBER).zfill(2):
						if name == 'src' + str(config.HOMEWORK_NUMBER).zfill(2):
							# rename it to 'src' IF there is not src folder already
							if not os.path.isdir(path + 'src'):
								os.rename(path + name, path + 'src')
							else:
								# > 1 source folder -> remove all the subsequent ones
								shutil.rmtree(path + name)
						hasSrc = True
					# it doesn't look like a source folder
					else:
						shutil.rmtree(path + name)
				# it's a file
				else:
					# remove it if it's NOT a source code or zip
					if self.extension(name) != 'cpp' and self.extension(name) != 'h' and self.extension(name) != 'zip':
						os.remove(path + name)
						
			# create the source folder if doesn't exist
			if not hasSrc:
				os.makedirs(path + 'src')
			
			# let's move all source codes from root to the src folder 
			dirList = os.listdir(path)
			for name in dirList:
				if not os.path.isdir(path + name) and self.extension(name) != 'zip':
					os.rename(path + name, path + 'src/' + name)

			# now let's check the source folder
			dirList = os.listdir(path + 'src')
			hasSource = False
			for name in dirList:
				# we should not have folders in 'src'
				if os.path.isdir(path + 'src/' + name):
					shutil.rmtree(path + 'src/' + name)
				else:
					# remove it if it's NOT a source code					
					if self.extension(name) != 'cpp' and self.extension(name) != 'h':
						os.remove(path + 'src/' + name)
					else:
						hasSource = True
			
			if hasSource:
				if submission.dateTime <= self.dueDate:
					self.csvFile.write(submission.studentId + ',\"\"\n')
					os.rename(path, config.EXTRACTION_FOLDER + '/' + config.ON_TIME_FOLDER + '/' + submission.studentId + '/')
				else:
					self.csvFile.write(submission.studentId + ',\"homework submission was late!\"\n')
					os.rename(path, config.EXTRACTION_FOLDER + '/' + config.LATE_FOLDER + '/' + submission.studentId + '/')
				return True
			else:
				shutil.rmtree(path + 'src')
				self.csvFile.write(submission.studentId + ',\"couldn\'t find a valid source code!\"\n')			
				return False
		except Exception, ex:
			print(ex)
			self.csvFile.write(submission.studentId + ',\"' + str(ex) + '\"\n')			
			return False
	
	# extractAll - extract all submissions
	def extractAll(self):
		# create a list of all submission objects
		submissions = self.submissions()
		count = 0
		for submission in submissions:
			if self.extract(submission):
				if self.verify(submission):
					count += 1				
			else:
				self.csvFile.write(submission.studentId + ',\"zip file appears to be corrupted!\"\n')
		self.mainZip.close()		
		if count == 1:
			print('Only ' + str(count) + ' out of ' + str(len(submissions)) + ' homework submission was valid')
		else:
			print(str(count) + ' out of ' + str(len(submissions)) + ' homework submissions were valid')
		
		# closing csvfile
		self.csvFile.close()