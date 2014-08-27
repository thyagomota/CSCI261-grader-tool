# ------------------------------------------------------------------------------- #
# Submission.py - Defines a student's homework submission                         #
# Author: Thyago Mota (from Yong's BaseSubmission.rb)                             #
# Date: 06/02/2014                                                                #
# ------------------------------------------------------------------------------- #

import datetime
from datetime import datetime

class Submission:
	def __init__(self, fileName):
		self.fileName = fileName
		fields = self.fileName.split(' ')[1].split('_')
		self.studentId = fields[1]
		self.dateTime = datetime.strptime(fields[3], '%Y-%m-%d-%H-%M-%S')	
		self.fileNameShort = fields[4].lower()
		#print(self.studentId + ', ' + str(self.dateTime) + ', ' + self.fileName + ', ' + self.fileNameShort)