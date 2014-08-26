# ------------------------------------------------------------------------------- #
# Submission.py - Defines a student's homework submission                         #
# Author: Thyago Mota (from Yong's BaseSubmission.rb)                             #
# Date: 06/02/2014                                                                #
# ------------------------------------------------------------------------------- #

import datetime
from datetime import datetime

class Submission:
	STATUS_OK      = 0
	STATUS_BAD_ZIP = 1
	STATUS_NO_SRC  = 2
	STATUS_BAD_SRC = 3
	STATUS_LATE    = 4
	
	def __init__(self, submissionPair):
		self.fileNameLong = submissionPair[0]				
		submissionPair[0] = submissionPair[0].split(' ')[1]
		self.fileNameShort = submissionPair[0].split('_')[4]
		submissionPair[1] = submissionPair[1].split(' ')[1]
		submissionPair[1] = submissionPair[1][:len(submissionPair[1])-4].split('_')
		self.homework = int(submissionPair[1][0])
		self.studentId = submissionPair[1][1]
		self.dateTime = datetime.strptime(submissionPair[1][3], '%Y-%m-%d-%H-%M-%S')
		self.status = self.STATUS_OK