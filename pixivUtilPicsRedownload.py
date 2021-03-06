# -*- coding: utf-8 -*-

'''
Created on 2015-2-28
 
@author: Valden
@module: pixivUtilErrorPicsRedownload
@note: read pixivUtil path then redownload its err pics
'''

import os
import re
import sys
import copy
import subprocess
import getopt

pixivExeFile = 'PixivUtil2.exe'
pixivErrorDir = 'errs'


def GetPixivErrImageId(filename):
	"""@param filename: like 'Error medium page for image 35664964' or 'Error Big Page for image 47367909'
@return: imageId like '35664964' or '47367909'
"""
	if re.match('^\d+$', filename):
		return filename
	m = re.split('^Error.*image ', filename)
	if len(m) < 2:
		return None
	return m[-1].split('.')[0]

def GetPixivErrMemberId(filename):
	"""@param filename: like 'Error page for member 388730'
@return: memberId like '388730'
"""
	if re.match('^\d+$', filename):
		return filename
	m = re.split('^Error.*member ', filename)
	if len(m) < 2:
		return None
	return m[-1].split('.')[0]

def GetPixivLinkImageId(filename):
	"""@param filename: like 'http://www.pixiv.net/member_illust.php?mode=manga&illust_id=49729370' or 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id=48784432'
@return: imageId like '493189'
"""
	if re.match('^\d+$', filename):
		return filename
	matchs = r'^http.*pixiv.*member_illust\.php\?mode=\w*&illust_id=(\d*)'
	m = re.split(matchs, filename)
	if len(m) < 3:
		return None
	return m[1].split('.')[0]

def GetPixivLinkMemberId(filename):
	"""@param filename: like 'http://www.pixiv.net/member_illust.php?id=493189'
@return: memberId like '493189'
"""
	if re.match('^\d+$', filename):
		return filename
	matchs = r'^http.*pixiv.*_illust\.php\?id=(\d*)'
	m = re.split(matchs, filename)
	if len(m) < 3:
		return None
	return m[1].split('.')[0]

def toShutdown():
	"shutdown system without wait"
	#p = subprocess.Popen(['notepad', r'D:\tmp\ren'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	cmd = ['shutdown', '-s', '-t', '10']
	print cmd
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print p.pid, p.stdout.read()

def reDownErrorPics(pixivutilPath):
	"download error pics in dir pixivutilPath\errs"
	if len(pixivutilPath) == 0:
		print '!---pixivutilPath cant be null'
		return 1
	if not os.path.isdir(pixivutilPath):
		print '!---pixivutilPath wrong'
		return 2
	exeFilename = os.path.join(pixivutilPath, pixivExeFile)
	errorDir = os.path.join(pixivutilPath, pixivErrorDir)
	if not os.path.isfile(exeFilename):
		print '!---pixivUtil exe not exsit'
		return 3
	if not os.path.isdir(errorDir):
		print '!---pixivUtil errs dir not exsit'
		return 5
	for file in os.listdir(errorDir):
		command = ""
		# first likely picId
		picId = GetPixivErrImageId(file)
		print 'picId:', picId
		if picId:
			# command of imiage download
			command = '"' + exeFilename + '" -x -s 2 ' + picId
		else:
			memberId = GetPixivErrMemberId(file)
			print 'memberId:', memberId
			if memberId:
				# command of member download
				command = '"' + exeFilename + '" -x -s 1 ' + memberId
		if not len(command):
			continue
		fileFull = os.path.join(errorDir, file)
		print 'run:', command
		print 'del:', fileFull
		res = os.system(command)
		print res
		if res == 0:
			os.remove(fileFull)
	print '-----all errRedown done with shut:', isDoneShut
	if isDoneShut:
		toShutdown()
	return 0

def reDownPicsByFile1(pixivutilPath, downFile, isDoneShut):
	"download pixiv pics in pixivutilPath\downFile"
	if len(pixivutilPath) == 0:
		print '!---pixivutilPath cant be null'
		return 1
	if not os.path.isdir(pixivutilPath):
		print '!---pixivutilPath wrong'
		return 2
	exeFilename = os.path.join(pixivutilPath, pixivExeFile)
	downFilePath = os.path.join(pixivutilPath, downFile)
	if not os.path.isfile(exeFilename):
		print '!---pixivUtil exe not exsit'
		return 3
	if not os.path.isfile(downFilePath):
		print '!---pixivUtil downFile not exsit'
		return 4
	#print '-----start'
	#downResFilePath = os.path.join(pixivutilPath, downFile+'_res')
	reslines_map = None
	with open(downFilePath, 'rt') as fr:
		lines_map = {}
		reslines_map = {}
		#fr.seek(0,0)
		row = 0
		for line in fr:
			lines_map[row] = line
			row += 1
		reslines_map = copy.deepcopy(lines_map)
	if not reslines_map:
		print '---nothing in file'
		return 10

	try:
		for row, line in lines_map.iteritems():
			command = ""
			line = line.replace('\n', '')
			line = line.replace('\r', '')
			print 'line %d: %s' % (row,line)
			# first likely memberId
			memberId = GetPixivLinkMemberId(line)
			if memberId:
				command = '"' + exeFilename + '" -x -s 1 ' + memberId
			else:
				picId = GetPixivLinkImageId(line)
				if picId:
					command = '"' + exeFilename + '" -x -s 2 ' + picId
			if not len(command):
				continue
			print command
			res = os.system(command)
			print 'res:', res
			if res == 0:
				reslines_map.pop(row)
				with open(downFilePath, 'wt') as fw:
					fw.writelines(reslines_map.values())
					fw.flush()
	finally:
		#if os.path.isfile(downResFilePath):
		#	os.remove(downFilePath)
		#	os.rename(downResFilePath, downFilePath)
		#else:
		#	print '---None finished'
		print '-----res in', downFilePath
	print '-----downByFile end with shut:', isDoneShut
	if isDoneShut:
		toShutdown()
	return 0

def reDownPicsByFile2(pixivutilPath, downFile):
	"download pixiv pics in pixivutilPath\downFile"
	if len(pixivutilPath) == 0:
		print '!---pixivutilPath cant be null'
		return 1
	if not os.path.isdir(pixivutilPath):
		print '!---pixivutilPath wrong'
		return 2
	exeFilename = os.path.join(pixivutilPath, pixivExeFile)
	downFilePath = os.path.join(pixivutilPath, downFile)
	if not os.path.isfile(exeFilename):
		print '!---pixivUtil exe not exsit'
		return 3
	if not os.path.isfile(downFilePath):
		print '!---pixivUtil downFile not exsit'
		return 4

	#print '-----start'
	doingLineNum = 0 # start from lines[0]
	isFistRead = True
	
	while True:
		lines = []
		with open(downFilePath, 'rt') as fr:
			lines = fr.readlines()

		rowCnt = len(lines)
		if isFistRead:
			isFistRead = False
			if not rowCnt:
				print '---nothing in file'
				return 10
		if rowCnt <= doingLineNum:
			print '----line %d over indexing' % doingLineNum
			break

		line = originLine = lines[doingLineNum]
		line = line.replace('\n', '')
		line = line.replace('\r', '')
		print 'line %d: %s' % (doingLineNum,line)
		if not len(line):
			print '----line %d is end' % doingLineNum
			break

		# first likely memberId
		command = ""
		memberId = GetPixivLinkMemberId(line)
		if memberId:
			command = '"' + exeFilename + '" -x -s 1 ' + memberId
		else:
			picId = GetPixivLinkImageId(line)
			if picId:
				command = '"' + exeFilename + '" -x -s 2 ' + picId
		if not len(command):
			doingLineNum += 1
			continue
		print command
		res = os.system(command)
		print 'res:', res
		if res != 0:
			lines[doingLineNum] = '_'+str(res)+'_ '+originLine
			doingLineNum += 1
		else:
			#remainLines = lines[:doingLineNum]+lines
			lines.pop(doingLineNum)
		with open(downFilePath, 'wt') as fw:
			fw.writelines(lines)
			fw.flush()
	print '-----res in', downFilePath
	print '-----downByFile end with shut:', isDoneShut
	if isDoneShut:
		toShutdown()
	return 0


defaultPixivUtilPath = r'D:\Program Files\pixivutil20150403-beta'


def usage():
	print '******\nusage:\n python cmdFile [options] [downFile]'
	print '******\noptions:'
	print ' --help/-h:\t\tusage of commands'
	print ' --path=/-p (default):\t', defaultPixivUtilPath
	print ' --shut/-s:\t\tshut down system when shell finished'
	print ' --force/-f:\t\tnot show args'
	print ' --err:\t\t\tError Redown Mode. path/%s/* redownload' % pixivErrorDir

if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hsp:f", ["err", "help", "shut", "path=", "force"])
	except getopt.GetoptError as err:
		usage()
		print "!!ARG error!!"
		sys.exit(-2)

	# global settings
	isDoneShut = False
	pixivutilPath = defaultPixivUtilPath
	handleErrs = False
	toListArgs = True

	#print opts, args
	for opt, arg in opts:
		if opt in ['-h', '--help']:
			usage()
			sys.exit(0)
		elif opt in ['-s', '--shut']:
			isDoneShut = True
		elif opt in ['-p', '--path']:
			pixivutilPath = arg
		elif opt in ['--err']:
			handleErrs = True
		elif opt in ['-f', '--force']:
			toListArgs = False
		else:
			assert False, "unhandled option: " + opt

	if (len(args) < 1):
		#print "no downFile!!"
		downFile = ""
	else:
		downFile = args[0]

	if toListArgs:
		print "Your args:------"
		print " downFile:\t", repr(downFile)
		print " pixivutilPath:\t", pixivutilPath
		print " isDoneShut:\t", isDoneShut
		print " handleErrMode:\t", handleErrs
		print "----------------"
		if 'y' != raw_input('start? (y/n)'):
			sys.exit(0)

	if handleErrs:
		res = reDownErrorPics(pixivutilPath)
	else:
		#res = reDownPicsByFile1(pixivutilPath, downFile)
		res = reDownPicsByFile2(pixivutilPath, downFile)
	sys.exit(res)
