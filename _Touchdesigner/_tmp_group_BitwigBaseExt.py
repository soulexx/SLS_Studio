"""

"""

from TDStoreTools import StorageManager
import TDFunctions as TDF
import asyncio

class BitwigBaseExt:
	"""
	bitwigBaseExt description
	"""
	# --------------------------------- INIT ---------------------------------

	def __init__(self, ownerComp):
		# Operators
		self.ownerComp = ownerComp
		
		# Data Storage
		#self.Listeners = {}
		self.InfoListeners = {}
		self.SyncChannels = {}
		self.OutPars = {}
		self.PulsePars = {}
		self.asyncTasks = {}
		self.SyncData = {}

		self.defaultColor = (0.5, 0.3499999940395355, 0.05000000074505806)
		
		# properties
		TDF.createProperty(self, 'OutParNames', value = set(), dependable='deep',
						   readOnly=False)
		TDF.createProperty(self, 'PulseParNames', value = set(), dependable='deep',
		     				readOnly=False)
		TDF.createProperty(self, 'Connected', value = False, dependable=True,
						   readOnly = True)
		TDF.createProperty(self, 'Listeners', value = {}, dependable = 'deep',
						   readOnly = False)
		#TDF.createProperty(self, 'CursorIndex', value = None, dependable = True,
		#     				readOnly = False)
		
		self.defaultCursorIndex = None
		storedItems = [
			{	
				'name' : 'cursorIndex',
				'default' : self.defaultCursorIndex,
				'dependable' : True
			}
		]
		self.stored = StorageManager(self, ownerComp, storedItems)
		
		self.OscInCHOP = self.ownerComp.op('bitwigBase/oscListen')
		self.OscInDAT = self.ownerComp.op('bitwigBase/oscInfo')

		self.setTDBitwigComp()
		self.checkTDBitwigComp()
		self.checkTDBitwigVersion()

		self.clearOSC()
		run("op(" + str(self.ownerComp.id) +
						").ext.BitwigBaseExt.tryConnection() " \
						"if op(" + str(self.ownerComp.id) + ") else None",
				delayFrames=1, delayRef=op.TDResources)
		
	def setTDBitwigComp(self):
		try:
			self.TDBitwigComp = self.ownerComp.par.Tdbitwigcomp.eval()
		except:
			self.TDBitwigComp = None

	@property
	def cursorCountSettingName(self):
		if self.CompType == 'ProjectControlPage':
				settingName = 'Project Cursor Page Count'
		else:
			if self.CompType == 'Song':
				settingName = None
			else:
				settingName = 'Cursor Track Count'
		return settingName
	

	def checkTDBitwigComp(self):

		self.ownerComp.clearScriptErrors(recurse = False, error = '*')

		
		if self.ownerComp.par.Tdbitwigcomp:
			self.ownerComp.clearScriptErrors(recurse = False, error = 'Missing bitwigMain COMP*')
		else:
			if hasattr(op, 'TDBitwigPackage') and self.ownerComp.parent(2).par.opshortcut.eval() == "TDBitwigPackage":
				pass
			else:
				self.ownerComp.addScriptError('Missing bitwigMain COMP. System requires bitwigMain COMP in project,' \
											'import from the palette in the TDBitwig folder.')
			
		return
	
	def checkTDBitwigVersion(self):

		self.ownerComp.clearScriptErrors(recurse = False, error = 'Version Mismatch')

		if self.TDBitwigComp:
			mainVersion = self.TDBitwigComp.par.Version.eval()
			compVersion = self.ownerComp.par.Version.eval()

			if mainVersion != compVersion:
				if hasattr(op, 'TDBitwigPackage') and self.ownerComp.parent(2).par.opshortcut.eval() == "TDBitwigPackage":
					pass
				else:
					self.ownerComp.addScriptError('Version Mismatch. This component version does not match bitwigMain version,' \
				  									'use tdBitwigPackage to update all Components to the most recent version.')
					
			else:
				self.ownerComp.clearScriptErrors(recurse = False, error = 'Version Mismatch*')
	
	def onCreate(self):
		pass

	# ---------------------------- CURSOR MAPPINGS -----------------------------

	def resetCursorIndex(self):
		if self.CompType != 'Song':
			self.setCursorIndex(None)
		return

	def checkIfConnectionMapped(self):
		'''
		-if BW comp type requires a cursor index
			- check if we are already have an assigned cursorIndex
			- if not, make a request to find an available index
		- only newly create comps should not have an index
		- any comp which already exists in the project should have a 
			non null cursorIndex value
		'''
		# if (self.CompType in ['Song']):
		# 	return
		if self.debugLog:
			print(f"Base Ext: {self.ownerComp.name} : checkIfConnectionMapped Called")
		if self.ownerComp.par.Connect.eval():
			validConnection = self.requestListenerConnection()
			if validConnection:
				self.ownerComp.clearScriptErrors(recurse = False, error = 'No available cursor slots*')
			else:
				self.ownerComp.addScriptError(f'No available cursor slots for comp {self.ownerComp.path}')
			return validConnection
		return False
	
	def checkIfInvalidCursorIndex(self):
		'''
		'''
		if self.debugLog:
			print(f"Base Ext: {self.ownerComp.name} : checkIfInvalidCursorIndex Called")
		if self.TDBitwigComp:
			self.ownerComp.clearScriptErrors(recurse = False, error = 'Cursor index * outside of*')
			settingName = self.cursorCountSettingName
			invalid = self.TDBitwigComp.CheckCursorOutsideOfCapacity(self.ownerComp)
			if invalid:
				self.ownerComp.addScriptError(f'Cursor index {self.GetCursorIndex()} above the controller limit. '\
				 							f'Adjust the {settingName} setting in the Bitwig Controller Settings '\
												f'and restart the extension by toggling off and on.')
				return True
			else:
				self.ownerComp.clearScriptErrors(recurse = False, error = 'Cursor index * above the *')
				return False
				
	def GetCursorIndex(self):
		return self.cursorIndex

	def setCursorIndex(self, index):
		self.cursorIndex = index
		if (index is None):
			setattr(self.ownerComp.par, 'Listenerindex', -1)
		else:	
			setattr(self.ownerComp.par, 'Listenerindex', index)

	# --------------------------- NOTIFICATION ----------------------------------

	def OnNotificationReceived(self, info):
		# receive notification from the main extension
		# info : dictionary containing relevant notification info
		# parse info and delegate to the appropriate method
		type = info['notificationType']
		
		if (self.debugLog):
			print(f"{self.ownerComp.name}: BaseExt: On Notification Received:{type}")

		if (type == 'disconnected'):
			self.disconnect()
		elif (type == 're-init'):
			self.setTDBitwigComp()
			self.tryConnection()
			#check this
			# TODO
		elif (type == 'checkVersion'):
			self.checkTDBitwigVersion()
		elif (type == 'invalidCursorIndex'):
			# add 
			pass
		elif (type == 'connected'):
			# if song comp, need to pull global stored cue/scene bank info
			# if cursor-based comp, need to setup and activate listeners
			self.setupConnection()
			self.checkTDBitwigVersion()
		elif (type == 'reflush'):
			# TODO
			return
		elif (type == "listenerMappingConfirmed"):
			cursorIndex = info['cursorIndex']
			self.setCursorIndex(cursorIndex)
		elif (type == "onListenerRemoved"):
			self.OnListenerDisconnected()
		elif (type == "listenerUpdated"):
			listener = info['listener']
			val = info['listenerVal']
			self.onInfoListenerUpdate(listener, val)
		elif (type == "bankUpdated"):
			context = info['context']
			bankInfo = info['bankInfo']
			self.onBankUpdate(context, bankInfo)
		return

	# ------------------------------- CONNECTION -------------------------------
	'''

	'''

	def tryConnection(self):
		self.setTDBitwigComp()
		if (self.ownerComp.par.Connect.eval()):
			if (self.TDBitwigComp is not None and self.ownerComp.par.Tdbitwigcomp):
				if(self.TDBitwigComp.Connected):
					#
					if not self.checkIfConnectionMapped():
						return
					if self.checkIfInvalidCursorIndex():
						return
					self.OnNotificationReceived({'notificationType' : 'connected'})
				else:
					self.OnNotificationReceived({'notificationType' : 'disconnected'})

	def setupConnection(self):
		if not self.checkIfConnectionMapped():
			self.disconnect()
			return
		if self.checkIfInvalidCursorIndex():
			self.disconnect()
			return
		self.disconnect()
		if(self.debugLog):
			print(f"{self.ownerComp.name}: BaseExt: Connection Initializing...")
		
		self.OscInCHOP.par.port = self.TDBitwigComp.par.Touchdesignerinport.val
		self.OscInDAT.par.port = self.TDBitwigComp.par.Touchdesignerinport.val

		self.setupListeners()
		self.setupPulsePars()
		#if (self.CompType not in ['Song']):
		self.updateCompInfo()
		self.TDBitwigComp.ActivateCompListener(self.ownerComp)
		# else:
		# 	# if comptype is Song, bypass adding comp to the listener mapping
		# 	# make listener request to the controller ext directly
		# 	self.sendOSC('/listener/add', [None, 'Song'])
		
		self._Connected.val = True
		return
	
	def requestListenerConnection(self):
		if(self.debugLog):
			print("BaseExt: Connection requested...")
		# tell the main extension we want to request a listener connection
		if(self.TDBitwigComp):
			return self.TDBitwigComp.AddCompListenerToMap(self.ownerComp, self.CompType)
		
	def OnCompConnected(self, cursorIndex):
		# callback for when main extension confirms it has connected
		# perform any actions after listener index confirmed
		# setup the osc listener scope with the newly updated cursorIndex
		self.setupListeners()
		self.setupPulsePars()
		# call main extension to add our confirmed listener
		#self._Connected = True
		#self.TDBitwigComp.AddCompListener(self.ownerComp)

		if(self.debugLog):
			print(f"BaseExt: Connection confirmed : {cursorIndex}")

		#TODO

	def disconnect(self):
		'''
		- disconnect this Comp
		- clear the stored listener data
		- set cursorIndex to null value
		'''
		self.setTDBitwigComp()
		if (self.debugLog):
			print(f"{self.ownerComp.name}: BaseExt: disconnect called")
		if self.TDBitwigComp is None:
			return
		self._Connected.val = False
		# CHECK FOR BUGS
		#self.resetControlPars(0)
		#
		self.clearOutPars()
		self.removeAllListeners()
		# if (self.CompType not in ['Song']):
		if self.checkIfInvalidCursorIndex():
			return

		self.TDBitwigComp.DeactivateCompListener(self.ownerComp.id)
		# else:
		# 	self.sendOSC('/listener/remove', ["Song"])
		return
	
	def enableControlPars(self, pageIndex, enable):
		controlPage = self.ownerComp.customPages[pageIndex]
		for par in controlPage.pars:
			par.enable = enable
		return
	
	def resetControlPars(self, pageIndex):
		controlPage = self.ownerComp.customPages[pageIndex]
		for par in controlPage.pars:
			if par.mode not in [ParMode.EXPRESSION, ParMode.EXPORT]:
				if par.enable:
					par.val = par.default
				

	# -------------------------- STORING LISTENER PROPERTIES ----------------------------
	'''
	Listener:
		(context, property) : {'live': if property is live or info,
								'par': parObject or None if read only,
								''}
	SyncChannels:
		<channelName> : parName
	InfoProperties:
		(context, property) : parName
	CustomProperties:
		(context, property) : #TODO
	OutPars:
		<parName> : {'includeData' : true if oscReply should have info in args,
					'dataType' : describes the data type to send
					'replyAddress' : osc address to send out }

	'''
	def setupOSCListeners(self):
		# 
		self.setupListeners()
		return

	def setupListeners(self):
		self.clearOSC()
		# TODO
		return

	def addListener(self, listener, isLive, outPar = None, replyOSC = False, 
		 								castType = None, useDependency = False):
		'''
		# adds new listener to listener dict
		'''
		# Debug
		if (self.debugLog):
			print(f"{self.ownerComp.name}: addListener: ( {listener}, {isLive}, {outPar}, {replyOSC}, {castType})")
		#
		self.Listeners[listener] = {'live' : isLive, 'par' : None, 'depend' : useDependency}
		
		if (useDependency):
			self.addDependencyData(listener)

		if (isLive):
			# property received directly from API via osc CHOP
			self.Listeners[listener]['channel'] = listener[2]
			# add property channel to osc in listener scope
			
			self._addListenerToOSCChopScope(listener)
			if (outPar is not None and self.ownerComp.par[outPar.name] is not None):
				# add listener to dat scope
				self._addListenerToOSCDatScope(listener)
				# map osc channel to comp parameter
				self.Listeners[listener]['par'] = getattr(self.ownerComp.par, outPar.name)
				# ---CHANGED ---
				self.addSyncChannel(listener, outPar, replyOSC, castType, useDependency)
		else:
			# property received indirectly from API via TDBitwig extension
			self.addInfoListener(listener, outPar, replyOSC, castType)

			return
		return
	
	# ---CHANGE---
	def addDependencyData(self, listener):

		self.SyncData[listener] = tdu.Dependency(None)
		self.SyncData[listener].callbacks = [self.syncDataCallback]
		return 

	
	def addInfoListener(self, listener, outPar = None, replyOSC = None, castType = None):
		'''
		# store listener info for properties received from TDBitwig Extension
		'''
		self.InfoListeners[listener] = {'par' : outPar}
		if(replyOSC):
			self.addOutPar(outPar, listener, castType)
		return
	
	def _addListenerToOSCChopScope(self, listener, add = True):
		'''
		'''
		chopScope = self.OscInCHOP.par.oscaddressscope.val
		datScope = self.OscInDAT.par.addscope.val

		addCHOPChannel = self.formatChannelFromListener(listener, True)

		if (add):
			if (addCHOPChannel not in chopScope):
				self.OscInCHOP.par.oscaddressscope.val = \
									f"{chopScope} {addCHOPChannel}"
		else:
			self.OscInCHOP.par.oscaddressscope.val = \
						" ".join([i for i in chopScope.split() if i != chopScope])
	
	def _removeListenerFromOSCChopScope(self, listener):
		self._addListenerToOSCScope(listener, False)

	def _addListenerToOSCDatScope(self, listener, add = True):
		'''
		- only called if the osc channel is mapped to a parameter
		- in case where initial flush is called, defining the osc dat scope 
			allows us to force the incoming osc chop channels to push updates to 
			the comp parameters
		'''
		datScope = self.OscInDAT.par.addscope.val
		index = listener[0]
		context = listener[1]
		addDATChannel = f"/{index}/{context}/flush"
		if self.CompType == 'Song':
			addDATChannel = f"/{context}/flush"
		if self.CompType == 'ProjectControlPage':
			addDATChannel = f"/p{index}/{context}/flush"
		if (add):
			if (addDATChannel not in datScope):
				self.OscInDAT.par.addscope.val = \
									f"{datScope} {addDATChannel}"
		else:
			self.OscInCHOP.par.addscope.val = \
						" ".join([i for i in datScope.split() if i != datScope])
		return

	def _removeListenerFromOSCDatScope(self, listener):
		self._addListenerToOSCDatScope(listener, False)

	def addSyncChannel(self, listener, outPar, replyOSC = False, castType = None, useDependency = False):
		#
		if (self.debugLog):
			print(f"BaseExt: addSyncChannel: ( {listener}, {outPar}, {replyOSC}, {castType})")
		'''

		'''
		channel = self.formatChannelFromListener(listener)
		# ---CHANGE ---
		self.SyncChannels[channel] = {'par' : outPar,
									'dependency' : listener if useDependency else None}

		if (replyOSC):
			# create a mapping from parameter to outgoing osc message
			# ---CHANGE ---
			self.addOutPar(outPar, listener, castType, useDependency)

		return
	
	def addOutPar(self, outPar, listener, castType = None, useDependency = False):
		#
		if (self.debugLog):
			print(f"addOutPar: ( {listener}, {outPar}, {castType})")
		'''
		Desc:
			- 
		Inputs:
			outPar: parameter which triggers the outgoing osc message
			listener: listener object parameter corresponds to
			castType: 
			autoSend:
		'''
		replyAddress = self.formatReplyAddressFromListener(listener)
		if ("Color" in outPar.name):
			replyAddress = self.formatReplyAddressFromListener((listener[0], listener[1], "color"))
		self.OutPars[outPar.name] = {'address' : replyAddress,
			       					'castType' : castType,
									'dependency' : listener if useDependency else None}
		self.OutParNames.add(outPar.name)
		return
	
	def addPulsePar(self, pulsePar, cursorIndex, context, replyFunction, useParData):
		'''
		'''
		replyAddress = self.formatReplyAddressFromPulsePar(cursorIndex, context, replyFunction)
		self.PulsePars[pulsePar.name] = {'replyAddress': replyAddress,
				   						'useParData' : None}
		if(useParData is not None):
			self.PulsePars[pulsePar.name]['useParData'] = useParData

		self.PulseParNames.add(pulsePar.name)

		return
	
	def formatChannelFromListener(self, listener, osc = False):
		path = "/".join([str(i) for i in listener])

		if (self.CompType == 'Song'):
			path = "/".join([str(i) for i in listener][1:])
		if (self.CompType == 'ProjectControlPage'):
			path = "/".join([f"p{listener[0]}", listener[1], listener[2]])

		if (osc):
			path = f"/{path}"
		return path
		
	def formatReplyAddressFromListener(self, listener):
		# TODO
		# need to configure the result of this based on the comp type
		# if (self.CompType == 'Track'):
		# 	address = f"/cursor/{'/'.join([str(i) for i in listener])}/set"

		if (self.CompType == 'Song'):
			address = f"/{'/'.join([str(i) for i in listener][1:])}/set"
		elif(self.CompType == 'ProjectControlPage'):
			address = f"/projectRemotes/{'/'.join([str(i) for i in listener])}/set"
		else:
			address = f"/cursor/{'/'.join([str(i) for i in listener])}/set"
		return address
	
	def formatReplyAddressFromPulsePar(self, cursorIndex, context, functionName):
		# handle based on comp type
		
		if (self.CompType == 'Song'):
			address = f"/{context}/{functionName}"
		elif (self.CompType == 'ProjectControlPage'):
			address = f"/projectRemotes/{cursorIndex}/{context}/{functionName}"
		else:
			address = f"/cursor/{cursorIndex}/{context}/{functionName}"
		return address
	
	def removeListener(self, listener):
		#TODO
		# handle removing the listener
		
		return
	
	def removeAllListeners(self):
		'''
		TODO : figure out if listeners should be removed via
				osc individually, or removed all as a group
		'''
		self.clearOSC()
		#self.sendOSC(f"/listener/remove", [self.GetCursorIndex(), self.CompType])
		self.Listeners.clear()
		self.InfoListeners.clear()
		self.SyncChannels.clear()
		return
	
	def clearOutPars(self):
		self.OutPars.clear()
		self.OutParNames.clear()
	
	def clearOSC(self, justReset = False):
		self.OscInCHOP.par.resetchannelspulse.pulse()
		if (justReset):
			return
		else:
			self.OscInCHOP.par.resetchannelspulse.pulse()
			self.OscInCHOP.par.oscaddressscope = ''
			self.OscInDAT.par.clear.pulse()
			self.OscInDAT.par.addscope = ''	

	# ---------------------------- DEPENDENCY HANDLING ------------------------------

	#---CHANGE---
	def syncDataCallback(self, info):
		'''
		dependency callback for sync data
		called whenever a change to dependant occurs from calling setVal
		sources
			- onOSCChannelChange
			- onOutParValueChange
			- (TODO) onInfoListenerUpdate
		based on the method which called it, will either reply over OSC or sync the 
			associated parameter
		'''
		dependObj = info['dependency']
		dependVal = dependObj.val

		if info['setInfo']:
			setInfo = info['setInfo']
			sourceMethod = setInfo['sourceMethod']

			if sourceMethod == 'onOSCChannelChange':
				listener = setInfo['listener']
				syncParName = self.Listeners[listener]['par'].name
				self.syncParToData(syncParName, dependVal)

			elif sourceMethod == 'onOutParValueChange': 
				replyMessage = setInfo['replyMessage']
				replyAddress = replyMessage['address']
				replyArgs = replyMessage['args']
				self.sendOSC(replyAddress, replyArgs)

			#TODO

		return
	
	def syncParToData(self, parName, val):
		par = self.ownerComp.par[parName]
		if par is not None and par.mode not in [ParMode.EXPRESSION, ParMode.EXPORT]:
			# special handling for signature denominator
			if (par.name == 'Signaturedenominator'):
				par.menuIndex = [2,4,8,16].index(val)
				return
			self.ownerComp.par[parName].val = val
		return
	
	def setDependencyValue(self, listener, val, method, replyMessage = None):

		if self.debugLog:
			print(f"BaseExt: setDependencyValue : listener{listener} : val {val}")
		dataKey = listener
		setInfo = {'listener' : listener, 
	     			'sourceMethod' : method, 
					'replyMessage' : replyMessage}
		self.SyncData[dataKey].setVal(val, setInfo = setInfo)

	# ---------------------------- LISTENER CALLBACKS ------------------------------

	def onOSCChannelChange(self, channel, val, prev = None):
		'''
		inputs:
			 - channel : oscChop channel which changed
			 - val : current channel value
			 - prev : previous channel value
		'''
		#debugLog
		if (self.debugLog):
			print(f"BaseExt: OSC Channel changed: ( {channel.name}, {val}, {prev})")
		#
		chanName = channel.name 
		if(chanName in self.SyncChannels.keys() and self.ownerComp.par.Connect.eval()):

			#---CHANGE---
			#sync data
			if self.SyncChannels[chanName]['dependency']:
				self.setDependencyValue(self.SyncChannels[chanName]['dependency'], val, 
			    										"onOSCChannelChange")
				return

			#sync parameter
			mapPar = self.SyncChannels[chanName]['par']

			if mapPar.mode not in [ParMode.EXPRESSION, ParMode.EXPORT]:

				# special handling for signature denominator
				if (mapPar.name == 'Signaturedenominator'):
					self.SyncChannels[chanName]['par'].menuIndex = [2,4,8,16].index(val)
					return
				
				self.SyncChannels[chanName]['par'].val = val
		return
	
	async def tryOscChannelChange(self, channelName):
		channelObject = self.OscInCHOP[channelName]

		if channelObject is None:
			if self.debugLog:
				print(f'BaseExt: channel: {channelName} does not exist yet trying again. {self.ownerComp.path}')

			self.tryOscChannelChange(self, channelName)
		else:
			self.onOSCChannelChange(channelObject, channelObject[0])
			return


	def onOSCDatReceive(self, address, args):
		# implemented this to account for osc chop behaviour
		# reference the osc in DAT for details
		if (address.endswith("flush")):
			# flush property receieved
			# the osc address of the incoming osc chop val
			#debugLog
			if (self.debugLog):
				print(f"BaseExt: OSC Dat Receive: ( address:{address}, args:{args})")
			
			channelName = args[0][1:]
			
			self.runTask(self.tryOscChannelChange(channelName))

		return	
	
	def onInfoListenerUpdate(self, listener, val):
		'''
		desc :
			- Handle listener updates received from the main extensions
			- if listener is mapped to a par, update par
			- if not mapped, push update to the owner Component to handle
		inputs :
			- listener : (cursorIndex, context, property)
			- val : value of listener property
		'''
		# special handling for updating name properties
		if(self.debugLog):
				print(f"BaseExt: onInfoListenerUpdate : {listener} {val}")
		if (listener[2] == 'name'):
			# TODO: figure out how to handle name properties for different Comp types
			if (listener[1] == 'track'):
				self.TrackName = val
				if self.CompType == 'Note':
					self.ownerComp.par['Resetoscchannels'].pulse()
			elif (listener[1] == 'clip'):
				self.ClipName = val
			elif (listener[1] == 'device'):
				self.DeviceName = val
			elif (listener[1] == 'page'):
				self.PageName = val
		if (listener[1].startswith('par')):
			self.ownerComp.ParInfo[listener[1]][listener[2]] = val
			controlPar = self.ownerComp.par[f"Remotecontrol{listener[1][-1]}"]
			if (listener[2] == 'name'):
				controlPar.label = val
			elif(listener[2] == 'exists'):
				controlPar.enable = val
		elif (listener[1].startswith('send')):
			self.ownerComp.SendInfo[listener[1]][listener[2]] = val
			sendPar = self.ownerComp.par[f"Send{listener[1][-1]}"]
			if (listener[2] == 'name'):
				sendPar.label = val
			elif(listener[2] == 'exists'):
				sendPar.enable = val
		
		if listener[2] in ['hasPrev', 'hasNext', 'isNested']:
			self.handleNavUpdate(listener, val)
		if (listener in self.InfoListeners.keys()):
			mapPar = self.InfoListeners[listener]['par']
			if (mapPar is not None and val is not None):
				
				# check if par should ignore default value from bitwig
				if mapPar.name in ['Followplayingclip', 'Readmodulatedvalues', 
		       						'Readaudioenvelope', 'Remotecontrolpage', 
									'Pintrack', 'Pindevice', 'Pinclip']:
					self.bounceListener(mapPar, val)
					return
				if self.CompType == 'ProjectControlPage':
					if mapPar.name == 'Remotecontrolpage':
						self.bounceListener(mapPar,val)
						return
				# set the par 
				self.ownerComp.par[mapPar.name].val = val
		return
	
	def bounceListener(self, par, val):
		if par.isMenu and isinstance(val, int):
			if par.menuIndex != val:
				self.onOutParValueChange(par, None)
				return
		if par.val != val:
			self.onOutParValueChange(par, None)
		return
	
	def handleNavUpdate(self, listener, val):
		if val is None:
			return
		if listener[1] == 'track':
			if listener[2] == 'hasPrev':
				prevPar = self.ownerComp.par.Prevtrack
				if val:
					prevPar.enable = True
				else:
					prevPar.enable = False
			elif listener[2] == 'hasNext':
				nextPar = self.ownerComp.par.Nexttrack
				if val:
					nextPar.enable = True
				else:
					nextPar.enable = False
		elif listener[1] == 'device':
			if listener[2] == 'hasPrev':
				prevPar = self.ownerComp.par.Prevdevice
				if val:
					prevPar.enable = True
				else:
					prevPar.enable = False
			elif listener[2] == 'hasNext':
				nextPar = self.ownerComp.par.Nextdevice
				if val:
					nextPar.enable = True
				else:
					nextPar.enable = False
			elif listener[2] == 'isNested':
				parentPar = self.ownerComp.par.Selectparent
				if val:
					parentPar.enable = True
				else:
					parentPar.enable = False
		
		return
	
	# -------------------------- OUT PAR CALLBACKS ------------------------------
	
	def onOutParValueChange(self, par, prev):

		#if (self.debugLog):
			#print(f"{self.ownerComp.name}:BaseExt:OutParValueChange:{par}")


		outParInfo = self.OutPars[par.name]
		replyAddress = outParInfo['address']
		castType = outParInfo['castType']

		if(castType is not None):
			if (castType == 'b'):
				arg = bool(par.eval())
			if (castType == 'i'):
				arg = int(par.eval())
		else:
			arg = par.eval()
		# special handling for signature denominator
		if (par.name == 'Signaturedenominator'):
			arg = int(par.eval())
		# special handling for clipSlot index
		if (par.name in ['Clipslot', 'Remotecontrolpage']):
			arg = par.menuIndex
			if (arg is None):
				return
			
		args = [arg]
		# special handling for color
		if ("Color" in par.name):
			args = [c for c in self.ownerComp.parGroup.Color.eval()]
		
		if (self.Connected):

			if outParInfo['dependency']:
				self.setDependencyValue(outParInfo['dependency'], arg, 
			    							'onOutParValueChange',
			   									{'address' : replyAddress,
	      											'args': args})
				return
			
			if (self.debugLog):
				print(f"{self.ownerComp.name}:BaseExt:OutParValueChange:{par}: prev: {prev} : OSC SENDING")

			self.sendOSC(replyAddress, args)
			# else:
			# 	return
		return

	def onPulseParPulse(self, par):

		pulseParInfo = self.PulsePars[par.name]
		replyAddress = pulseParInfo['replyAddress']
		useParData = pulseParInfo['useParData']
		args = [""]
		if (useParData is not None):
			if useParData.isMenu:
				val = useParData.menuIndex
				args = [val]
			if par.name == 'Enterslot':
				args = [useParData.eval()]
		if (self.ownerComp.par.Connect.eval()):
			self.sendOSC(replyAddress, args)
		return

	# --------------------------- PULL SONG INFO --------------------------------

	def updateCompInfo(self):
		'''
		- called whenever comp is re-init, during connection setup
		- pull relevant information from TDBitwigComp Song Info
		- includes info based properties
		- includes bank info
		'''
		info = self.TDBitwigComp.SongInfo

		for listener in self.InfoListeners:
			if listener[0] is None:
				context = listener[1]
				property = listener[2]
				updateVal = info[context][property]
				self.onInfoListenerUpdate(listener, updateVal)
			else:
				cursorInfo = info['cursors']
				if self.CompType == 'ProjectControlPage':
					cursorInfo = info['projectRemotes']
				cursorIndex = listener[0]
				context = listener[1]
				property = listener[2]
				updateVal = cursorInfo[cursorIndex][context][property]
				self.onInfoListenerUpdate(listener, updateVal)

		for bank in self.BankInfo.keys():
			if bank in ['cues', 'scenes', 'tracks']:
				bankInfo = info[bank]
				self.onBankUpdate(bank, bankInfo)
			else:
				if (self.CompType == 'Song'):
					return
				else:
					cursorIndex = self.GetCursorIndex()
					cursorInfo = info['cursors'][cursorIndex]
					#handle for project remotes type
					if self.CompType == "ProjectControlPage":
						cursorInfo = info['projectRemotes'][cursorIndex]

					
					#handle nested bank information
					if bank in ['siblingDevices', 'deviceLayers', 'slotNames']:
						bankInfo = cursorInfo['device'][bank]
					elif bank in ['pageNames']:
						bankInfo = cursorInfo['page'][bank]
					else:
						bankInfo = cursorInfo[bank]
					self.onBankUpdate(bank, bankInfo)

		return

	# --------------------------- BANK UPDATES ----------------------------------

	def onBankUpdate(self, context, bankInfo):
		if(self.debugLog):
				print(f"BaseExt : OnBankUpdate : {context}")

		if (context == 'cues'):
			self.Cues = bankInfo
		elif (context == 'scenes'):
			self.Scenes = bankInfo
		elif (context == 'tracks'):
			#TODO
			return
		elif (context == 'clipSlots'):
			self.ownerComp.ClipSlots = bankInfo
			self.formatClipSlotMenu()
		elif (context == 'sends'):
			pass
		elif (context == 'siblingDevices'):
			self.SiblingDevices = bankInfo
		elif (context == 'slotNames'):
			self.SlotNames = bankInfo
			self.mapBankToParMenu(context, self.SlotNames)
		elif (context == 'deviceLayers'):
			self.DeviceLayers = bankInfo
			self.mapBankToParMenu(context, self.DeviceLayers)
		elif (context == 'pageNames'):
			self.PageNames = bankInfo
			self.mapBankToParMenu(context, self.PageNames)
		
		return
	
	def formatPageNamesMenu(self, pageNames):
		pass
	
	def mapBankToParMenu(self, context, bankProperty):
		menuPar = self.BankInfo[context]['par']
		isDict = self.BankInfo[context]['isDict']
		auxPar = self.BankInfo[context]['auxPar']

		if (self.debugLog):
			print(f"BaseExt: mapBankToParMenu: {context} {menuPar.name}")

		if (bankProperty is None):
			return
		if (len(bankProperty) == 0):
			menuPar.enable = False
			if auxPar is not None:
				auxPar.enable = False
		else:
			menuPar.enable = True
			if auxPar is not None:
				auxPar.enable = True
			if (isDict):
				menuVals = [bankProperty[i]['name'] for i in range(len(bankProperty)) \
							if i in bankProperty.keys()]
			else:
				menuVals = bankProperty
			self.mapToMenuSource(menuPar, menuVals)
		return
	# ----------------------- SYSTEM PAR CALLBACKS --------------------------------

	def onParValueChange(self, par, prev):
		name = par.name
		val = par.eval()
		if (name == "Connect"):
			if (val == 1):
				self.tryConnection()
			else:
				self.disconnect()
		if (name == 'Tdbitwigcomp'):
			self.checkTDBitwigComp()

		if (name == 'Timesliceoscchop'):
			self.tryConnection()
			
			if self.ownerComp.CompType == 'Note':
				#force formatChannel Comp to Cook to resolve channels getting stuck
				#self.ownerComp.op('formatChannels').cook(force = True)
				pass
			pass
		
		return
	
	# ----------------------------- UTILITY -------------------------------------

	def sendOSC(self, address, args):
		if (self.TDBitwigComp):
			self.TDBitwigComp.SendOSC(address, args)

	def runTask(self, coroutine):
		if (self.TDBitwigComp):
			self.TDBitwigComp.RunTask(coroutine)

	def formatString(self, string):
		return string.replace(" ", "").lower().capitalize()
		
	def mapToMenuSource(self, par, listVals):
		if par.name in ["Remotecontrolpage"]:
			if self.PageNames and self.PageName:
				if self.PageName in self.PageNames:
					index = self.PageNames.index(self.PageName)
					script = "args[0].menuIndex = args[1]"
					run(script, par, index, delayFrames = 5, delayRef = op.TDResources)
					if self.debugLog:
						print(f"{self.ownerComp.name} : BaseExt: mapToMenuSource : setting menuIndex")
						print(f"Page Names : {self.PageNames}, Current Page : {self.PageName} : menuIndex : {index}")
			return
	
	def strippedChannel(self, channelName):
		# return channel after adjusted for stripped segments
		return '/'.join(channelName.split('/')
							[1 + self.ownerComp.par.Stripchopprefixsegments:])
	
	def ChanNameStripped(self, name, rename = False, chanIndex = '', numSegments=None):
		"""
		Strip initial segments in same way that "Strip CHOP Prefix Segments"
			parameter does. REMOVES INITIAL SLASH

		:param name: channel name you want to strip
		:param numSegments: number of segments to strip. Defaults to value of
				Strip CHOP Prefix Segments parameter
		:return: stripped channel name
		"""
		if numSegments is None:
			numSegments = self.ownerComp.par.Stripchopprefixsegments
		splitName = name.split('/')
		
		if rename:
			splitName, ignoreStrip = self.nameHeader(splitName, chanIndex)
			if ignoreStrip:
				numSegments = 0

		if self.CompType == 'ProjectControlPage' and not rename:
			splitName = [f'p{splitName[0]}'] + splitName[1:]

		strippedList = splitName[numSegments:]
		strippedStr = '/'.join(strippedList)

		validPath = tdu.validPath(strippedStr)
		
		if (self.CompType == 'Note'):
			if self.ownerComp.par['Translateindextopitch'].eval():
				lastElement = strippedList[-1:]
				if lastElement[0] in self.negNoteNames:
					newList = (validPath.split('/')[:-1]) + lastElement
					validPath = '/'.join(newList)
			else: 
				if len(strippedList) == 1:	
					validPath = strippedStr

		return validPath
	
	def resetDockedPosition(self):
		docked = self.ownerComp.docked
		if docked:
			for op in docked:
				if "Callbacks" in op.name:
					op.nodeX = self.ownerComp.nodeX - 150
					op.nodeY = self.ownerComp.nodeY
		return

	@property
	def debugLog(self):
		return self.ownerComp.par.Debugmessages.eval()
		
	def nameHeader(self, listKey, index):
		compType = self.CompType
		newKey = listKey
		ignoreStrip = False
		if compType == 'Track':
			pass
		elif(compType == 'ClipLauncher'):
			pass
		elif(compType == 'DeviceControlPage'):
			parInfo = self.ParInfo[listKey[1]]
			parExist = parInfo['exists']
			if not parExist:
				newKey = [f'None{index}', listKey[2]]
				return (newKey, True)
			newKey = [self.TrackName, self.DeviceName, 
						self.PageName if self.PageName != '' else 'None'] + \
						[ self.ParInfo[listKey[1]]['name'], listKey[2]]
		elif(compType == 'TrackControlPage'):
			parInfo = self.ParInfo[listKey[1]]
			parExist = parInfo['exists']
			if not parExist:
				newKey = [f'None{index}', listKey[2]]
				return (newKey, True)
			newKey = [self.TrackName, 
						self.PageName if self.PageName != '' else 'None' ] + \
						[self.ParInfo[listKey[1]]['name'], listKey[2] ]
		elif(compType == 'ProjectControlPage'):
			parInfo = self.ParInfo[listKey[1]]
			parExist = parInfo['exists']
			if not parExist:
				newKey = [f'None{index}', listKey[2]]
				return (newKey, True)
			newKey = [self.PageName if self.PageName != '' else 'None'] + \
						[self.ParInfo[listKey[1]]['name'], listKey[2]] 
		elif(compType == 'Note'):
			pass
		return (newKey, ignoreStrip)

