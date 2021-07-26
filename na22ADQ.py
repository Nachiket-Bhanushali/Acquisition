import sys
import optparse
import argparse
import signal
import os
import time
import shutil
import datetime
from shutil import copy

stop_asap = False

import pyvisa as visa

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        shutil.copytree(item, d, symlinks, ignore)
def copynew(source,destination):
    for files in source:
        shutil.copy(files,destination)
"""#################SEARCH/CONNECT#################"""
# establish communication with dpo
rm = visa.ResourceManager("@py")
#dpo = rm.open_resource('TCPIP::192.168.133.159::INSTR')
dpo = rm.open_resource('TCPIP::192.168.0.182::INSTR')

#dpo.write_termination = '\n'
#dpo.read_termination = '\n'

dpo.timeout = 3000000
dpo.encoding = 'latin_1'
print(dpo.query('*idn?'))


parser = argparse.ArgumentParser(description='Run info.')

parser.add_argument('--numEvents',metavar='Events', type=str,default = 1000, help='numEvents (default 500)',required=True)
parser.add_argument('--runNumber',metavar='runNumber', type=str,default = -1, help='runNumber (default -1)',required=False)
parser.add_argument('--sampleRate',metavar='sampleRate', type=str,default = 4, help='Sampling rate (default 20)',required=True)
parser.add_argument('--horizontalWindow',metavar='horizontalWindow', type=str,default = 200, help='horizontal Window (default 125)',required=True)
# parser.add_argument('--numPoints',metavar='Points', type=str,default = 500, help='numPoints (default 500)',required=True)
parser.add_argument('--trigCh',metavar='trigCh', type=str, default='1',help='trigger Channel (default Aux (-0.1V))',required=False)
parser.add_argument('--trig',metavar='trig', type=float, default= -0.0023, help='trigger value in V (default Aux (-0.05V))',required=False)
parser.add_argument('--trigSlope',metavar='trigSlope', type=str, default= 'NEGative', help='trigger slope; positive(rise) or negative(fall)',required=False)

parser.add_argument('--vScale1',metavar='vScale1', type=float, default= 0.005, help='Vertical scale, volts/div',required=False)
#parser.add_argument('--vScale2',metavar='vScale2', type=float, default= 0.02, help='Vertical scale, volts/div',required=False)
#parser.add_argument('--vScale3',metavar='vScale3', type=float, default= 0.02, help='Vertical scale, volts/div',required=False)
#parser.add_argument('--vScale4',metavar='vScale4', type=float, default= 0.02, help='Vertical scale, volts/div',required=False)

parser.add_argument('--vPos1',metavar='vPos1', type=float, default= 0.016, help='Vertical Pos, div',required=False)
#parser.add_argument('--vPos2',metavar='vPos2', type=float, default= 3, help='Vertical Pos, div',required=False)
#parser.add_argument('--vPos3',metavar='vPos3', type=float, default= 3, help='Vertical Pos, div',required=False)
#parser.add_argument('--vPos4',metavar='vPos4', type=float, default= 3, help='Vertical Pos, div',required=False)


parser.add_argument('--timeoffset',metavar='timeoffset', type=float, default=-53, help='Offset to compensate for trigger delay. This is the delta T between the center of the acquisition window and the trigger. (default for NimPlusX: -160 ns)',required=False)

parser.add_argument('--save',metavar='save', type=int, default= 1, help='Save waveforms',required=False)
parser.add_argument('--timeout',metavar='timeout', type=float, default= -1, help='Max run duration [s]',required=False)


args = parser.parse_args()
trigCh = str(args.trigCh)
runNumberParam = int(args.runNumber)
if trigCh != "AUX": trigCh = 'CHANnel'+trigCh
trigLevel = float(args.trig)
triggerSlope = args.trigSlope
timeoffset = float(args.timeoffset)*1e-9
print ("timeoffset is ",timeoffset)
date = datetime.datetime.now()
savewaves = int(args.save)
timeout = float(args.timeout)
print (savewaves)
print ("timeout is ",timeout)
"""#################CONFIGURE INSTRUMENT#################"""
# variables for individual settings
#hScale = float(args.horizontalWindow)*1e-9
samplingrate = float(args.sampleRate)*1e+9
#seems like 10GSa is the lowest?
hScale = 1e-6 # horizontal scale in seconds
numEvents = int(args.numEvents) # number of events for each file
# numPoints = int(args.numPoints) # number of points to be acquired per event
numPoints = samplingrate*hScale
print ("numPoints is = ", numPoints)
# samplerate =  numPoints/hScale ## sampling rate
print ("samplerate is = ", samplingrate)

#vertical scale
vScale_ch1 =float(args.vScale1) # in Volts for division
#vScale_ch2 =float(args.vScale2) # in Volts for division
#vScale_ch3 =float(args.vScale3) # in Volts for division
#vScale_ch4 =float(args.vScale4) # in Volts for division

#vertical position
vPos_ch1 = float(args.vPos1)#3#0 #3  # in Divisions
#vPos_ch2 = float(args.vPos2)#3#3 #3  # in Divisions
#vPos_ch3 = float(args.vPos3)#3#-1 #3  # in Divisions
#vPos_ch4 = float(args.vPos4)#3#3 #3  # in Divisions

date = datetime.datetime.now()

"""#################CONFIGURE RUN NUMBER#################"""
# increment the last runNumber by 1

if runNumberParam == -1:
	#RunNumberFile = '/home/daq/JARVIS/AutoPilot/otsdaq_runNumber.txt'
	RunNumberFile = 'F:\OSCDAta\runNumber.txt'
	with open(RunNumberFile) as file:
	    runNumber = int(file.read())

else: runNumber = runNumberParam

print('######## Starting RUN {} ########\n'.format(runNumber))
print('---------------------\n')
print(date)
print('---------------------\n')

#with open('runNumber.txt','w') as file:
#    file.write(str(runNumber+1))


"""#################SET THE OUTPUT FOLDER#################"""
# The scope save runs localy on a shared folder with
# path = r"C:\Users\Public\Documents\Infiniium\Test_Feb18"
#path = r"C:\Users\Public\Documents\Infiniium\Test_March21"
#dpo.write(':DISK:MDIRectory "{}"'.format(path)) ## what is this for?
#log_path = "/home/daq/ETL_Agilent_MSO-X-92004A/Acquisition/Logbook.txt"
#run_log_path = "/home/daq/ETL_Agilent_MSO-X-92004A/Acquisition/RunLog.txt"

log_path = 'F:\OSCDAta\Acquisition\Logbook.txt'
run_log_path = 'F:\OSCDAta\AcquisitionRunLog.txt'

#Write in the log file
logf = open(log_path,"a+")
logf.write("\n\n#### SCOPE LOGBOOK -- RUN NUMBER {} ####\n\n".format(runNumber))
logf.write("Date:\t{}\n".format(date))
logf.write("---------------------------------------------------------\n")
logf.write("Number of events per file: {} \n".format(numEvents))
logf.write("---------------------------------------------------------\n\n")


"""#################SCOPE HORIZONTAL SETUP#################"""
# dpo setup

dpo.write(':STOP;*OPC?')

dpo.write(':TIMebase:RANGe {}'.format(hScale)) ## Sets the full-scale horizontal time in s. Range value is ten times the time-per division value.
dpo.write(':TIMebase:REFerence:PERCent 70') ## percent of screen location
#dpo.write(':ACQuire:SRATe:ANALog {}'.format(samplingrate))
dpo.write(':ACQuire:SRATe:ANALog:AUTO ON')
#dpo.write(':ACQuire:SRATe:ANALog 4e9')
print(':ACQuire:SRATe:ANALog  ' + dpo.query(':ACQuire:SRATe:ANALog?'))
#dpo.write(':TIMebase:POSition 25E-9') ## offset

dpo.write(':TIMebase:POSition {}'.format(timeoffset)) ## offset
dpo.write(':ACQuire:MODE SEGMented') ## fast frame/segmented acquisition mode
dpo.write(':ACQuire:SEGMented:COUNt {}'.format(numEvents)) ##number of segments to acquire
#dpo.write(':ACQuire:POINts:ANALog {}'.format(numPoints))
dpo.write(':ACQuire:POINts:ANALog AUTO')
dpo.write(':ACQuire:INTerpolate 0') ## interpolation is set off (otherwise its set to auto, which cause errors downstream)

print("# SCOPE HORIZONTAL SETUP #")
print('Horizontal scale set to {} s for range\n'.format(hScale))
print('Horizontal offset set to {} s \n'.format(timeoffset))
logf.write("HORIZONTAL SETUP\n")
logf.write('Horizontal scale set to {} s for range\n'.format(hScale))
logf.write('Horizontal offset set to {} s\n'.format(timeoffset))


"""#################SCOPE CHANNELS BANDWIDTH#################"""
#dpo.write(':ACQuire:BANDwidth MAX') ## set the bandwidth to maximum
# dpo.write('CHANnel1:ISIM:BANDwidth 2.0E+09')
# dpo.write('CHANnel2:ISIM:BANDwidth 2.0E+09')
# dpo.write('CHANnel3:ISIM:BANDwidth 2.0E+09')
# dpo.write('CHANnel4:ISIM:BANDwidth 2.0E+09')

# dpo.write('CHANnel1:ISIM:BWLimit 1')
# dpo.write('CHANnel2:ISIM:BWLimit 1')
# dpo.write('CHANnel3:ISIM:BWLimit 1')
# dpo.write('CHANnel4:ISIM:BWLimit 1')

dpo.write(':ACQuire:BANDwidth 5.E10')
print('Bandwidth set to 500 MHz')
logf.write('Bandwidth set to 500 MHz \n')
"""#################SCOPE VERTICAL SETUP#################"""
#vScale expressed in Volts
dpo.write('CHANnel1:SCALe {}'.format(vScale_ch1))
#dpo.write('CHANnel2:SCALe {}'.format(vScale_ch2))
#dpo.write('CHANnel3:SCALe {}'.format(vScale_ch3))
#dpo.write('CHANnel4:SCALe {}'.format(vScale_ch4))
dpo.write('CHANnel1:OFFSet {}'.format(vPos_ch1))
#dpo.write('CHANnel1:OFFSet {}'.format(-vScale_ch1 * vPos_ch1))
#dpo.write('CHANnel2:OFFSet {}'.format(-vScale_ch2 * vPos_ch2))
#dpo.write('CHANnel3:OFFSet {}'.format(-vScale_ch3 * vPos_ch3))
#dpo.write('CHANnel4:OFFSet {}'.format(-vScale_ch4 * vPos_ch4))

print("# VERTICAL SETUP #")
print('- CH1: vertical scale set to {} V for division\n'.format(vScale_ch1))
#print('- CH2: vertical scale set to {} V for division\n'.format(vScale_ch2))
#print('- CH3: vertical scale set to {} V for division\n'.format(vScale_ch3))
#print('- CH4: vertical scale set to {} V for division\n'.format(vScale_ch4))

#print('- CH1: vertical offset set to {} V \n'.format(-vScale_ch1 * vPos_ch1))
print('- CH1: vertical offset set to {} V \n'.format(vPos_ch1))
#print('- CH2: vertical offset set to {} V \n'.format(-vScale_ch2 * vPos_ch2))
#print('- CH3: vertical offset set to {} V \n'.format(-vScale_ch3 * vPos_ch3))
#print('- CH4: vertical offset set to {} V \n\n'.format(-vScale_ch4 * vPos_ch4))


logf.write("VERTICAL SETUP\n")
logf.write('- CH1: vertical scale set to {} V for division\n'.format(vScale_ch1))
#logf.write('- CH2: vertical scale set to {} V for division\n'.format(vScale_ch2))
#logf.write('- CH3: vertical scale set to {} V for division\n'.format(vScale_ch3))
#logf.write('- CH4: vertical scale set to {} V for division\n'.format(vScale_ch4))

#logf.write('- CH1: vertical offset set to {} V \n'.format(-vScale_ch1 * vPos_ch1))
logf.write('- CH1: vertical offset set to {} V \n'.format(vPos_ch1))
#logf.write('- CH2: vertical offset set to {} V \n'.format(-vScale_ch2 * vPos_ch2))
#logf.write('- CH3: vertical offset set to {} V \n'.format(-vScale_ch3 * vPos_ch3))
#logf.write('- CH4: vertical offset set to {} V \n\n'.format(-vScale_ch4 * vPos_ch4))


"""#################TRIGGER SETUP#################"""
dpo.write('TRIGger:MODE EDGE; :TRIGger:EDGE:SOURce %s; :TRIGger:LEVel %s, %f'%(trigCh, trigCh, trigLevel))
dpo.write(':TRIGger:EDGE:SLOPe %s;' %(triggerSlope))

trigprint='%.3f'%(trigLevel)
print("# TRIGGER SETUP #")
print('Trigger Channel set to %s\n'%(trigCh))
print('Trigger scale set to %s V\n'%(trigprint))
print('Trigger on %s edge \n\n\n\n'%(triggerSlope))

logf.write("TRIGGER SETUP\n")
logf.write('- Trigger Channel set to %s\n'%(trigCh))
logf.write('- Trigger scale set to %s V\n'%(trigprint))
logf.write('- Trigger on %s edge \n\n\n\n'%(triggerSlope))
logf.close()

print('Horizontal, vertical, and trigger settings configured.\n')
#print("Trigger!")

status = ""
status = "busy"

run_logf = open(run_log_path,"w")
run_logf.write(status)
#run_logf.write("\n")
run_logf.close()
#raise exception("suck it")

"""#################DATA TRANSFERRING#################"""
# configure data transfer settings
#dpo.timeout = 600000
time.sleep(2)
#dpo.write(':DIGitize')
#print ("digitize")

print(dpo.write(':CDISplay'))

dpo.write('*CLS;:SINGle')
start = time.time()
end_early = False
while True:
#	print "Ader is ",dpo.query(':ADER?')
#	print "OPC is ",dpo.query('*OPC?')
	if (int(dpo.query(':ADER?')) == 1):
		print ("Acquisition complete")
		break
	else:
		#print "Still waiting"
		time.sleep(0.1)
		# if not savewaves and timeout > 0 and time.time() - start > timeout:
		if timeout > 0 and time.time() - start > timeout:
			end_early=True
			dpo.write(':STOP;*OPC?')
			break

end = time.time()
#print(dpo.query('*OPC?'))
# print("Trigger!")

tmp_file = open(run_log_path,"w")
status = "writing"
tmp_file.write(status)
tmp_file.write("\n")
tmp_file.close()

duration = end - start
trigRate = float(numEvents)/duration

if not end_early: print ("\nRun duration: %0.2f s. Trigger rate: %.2f Hz\n" % (duration,trigRate))
else: print ("\nRun duration: %0.2f s. Trigger rate: unknown\n" % (duration))
if savewaves:
	output_path = 'C:\\LCE_BTL_Module\\'
	#output_path = '\\DESKOP-KSABE0R\OSCDAta\na22_40V'
	dpo.write(':DISK:SEGMented ALL') ##save all segments (as opposed to just the current segment)
	print(dpo.query('*OPC?'))
	print("Ready to save all segments")
	time.sleep(0.5)
	#dpo.write(':DISK:SAVE:WAVeform CHANnel1 ,"C:\\Users\\Public\\Public Documents\\AgilentWaveform\\Wavenewscope_CH1_%s",BIN,ON'%(runNumber))
	dpo.write(':DISK:SAVE:WAVeform CHANnel1 ,"'+output_path+'Wavenewscope_CH1_run%s",BIN,ON'%(runNumber))
	#dpo.write(':DISK:SAVE:WAVeform CHANnel1 ,"C:\\Users\\Public\\Documents\\AgilentWaveform\\Wavenewscope_CH1_test_4000events",BIN,ON')

	print(dpo.query('*OPC?'))
	print("Saved Channel 1 waveform")
	time.sleep(1)
'''
	dpo.write(':DISK:SAVE:WAVeform CHANnel2 ,"'+output_path+'Wavenewscope_CH2_run%s",h5,ON'%(runNumber))

	print(dpo.query('*OPC?'))
	print("Saved Channel 2 waveform")
	time.sleep(1)
	dpo.write(':DISK:SAVE:WAVeform CHANnel3 ,"'+output_path+'Wavenewscope_CH3_run%s",h5,ON'%(runNumber))
	print(dpo.query('*OPC?'))
	print("Saved Channel 3 waveform")
	time.sleep(1)


	dpo.write(':DISK:SAVE:WAVeform CHANnel4 ,"'+output_path+'Wavenewscope_CH4_run%s",h5,ON'%(runNumber))


	print(dpo.query('*OPC?'))
	print("Saved Channel 4 waveform")
'''

tmp_file2 = open(run_log_path,"w")
status = "ready"
tmp_file2.write(status)
tmp_file2.write("\n")
tmp_file2.close()


dpo.close()
