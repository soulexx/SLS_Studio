# Bitwig Track Comp Extension

from TDStoreTools import StorageManager
import TDFunctions as TDF

BitwigBaseExt = \
	mod('bitwigBase/BitwigBaseExt').BitwigBaseExt

CallbacksExt = mod('CallbacksExt').CallbacksExt

class BitwigTrackExt(CallbacksExt, BitwigBaseExt):
	"""
	BitwigTrackExt description
	"""
	def __init__(self, ownerComp):

		#CallbacksExt.__init__(self, ownerComp)
		self.CompType = "Track"
		BitwigBaseExt.__init__(self, ownerComp)
	
		# Listener properties

		# special properties to handle
		self.customTrackProperties = ['hasNext', 'hasPrev']
		# synchronized properties

		# propertyInfo [customName, live, mapPar, replyOSC, cast dataType]

		self.propertyInfo = {
			'track' : 
		    	{'active' 			: [None, True, True, True, 'b'],
				'arm' 				: [None, True, True, True, 'b'],
				'solo' 				: [None, True, True, True, 'b'],
				'mute' 				: [None, True, True, True, 'b'],
				'volume' 			: [None, True, True, True, None],
				'pan' 				: [None, True, True, True, None],
				'colorR' 			: [None, True, True, True, None],
				'colorG' 			: [None, True, True, True, None],
				'colorB' 			: [None, True, True, True, None],
				'audioEnvelope'	 	: [None, True, False, False, None],
				'name' 				: ['Track', False, True, False, None],
				'isPinned' 			: ['Pintrack', False, True, True, 'b'],
				'hasNext' 			: [None, False, False, False, False],
				'hasPrev' 			: [None, False, False, False, False],
				'trackType' 		: [None, False, True, False, None],
				'monitorMode' 		: [None, False, True, True, None],
				'crossFadeMode' 	: [None, False, True, True, None],
				'readAudioEnvelope'	: [None, False, True, True, 'b'] }
		}
		
		self.BankInfo = {}

		sendInfoTemplate = {f"send{i}":{'name':None, 'exists':None} for i in range(8)}

		# pulseFunctionInfo : <pulseParName> : 
		self.pulseFunctionInfo = {	
			'Nexttrack'				: ['track','selectNext', None], 	
			'Prevtrack' 			: ['track','selectPrev', None],
			'Stopplayback' 			: ['track', 'stop', None],
			'Returntoarrangement'	: ['track', 'returnToArrangement', None],
			'Makevisibleinarranger' : ['track','makeVisibleInArranger', None],
			'Makevisibleinmixer' 	: ['track','makeVisibleInMixer', None],
			'Selectineditor' 		: ['track','selectInEditor', None],
			'Selectinmixer' 		: ['track','selectInMixer', None],
			'Restoreautomationcontrol': ['track', 'restoreSendsAutomationControl', None]
		}

		# properties
		TDF.createProperty(self, 'TrackName', value='', dependable = True,
						   readOnly=False)
		TDF.createProperty(self, 'SendInfo', value = sendInfoTemplate, dependable = 'deep',
						   readOnly=False)
		
		return

	def setupListeners(self):
		# read through property dict and store listener objects based on 
		# the property information
		BitwigBaseExt.setupListeners(self)

		for context in self.propertyInfo.keys():
			contextInfo = self.propertyInfo[context]

			for property in contextInfo.keys():
				propertyInfo = contextInfo[property]
			
				customName = propertyInfo[0]
				isLive = propertyInfo[1]
				syncToPar = propertyInfo[2]
				replyOSC = propertyInfo[3]
				castType = propertyInfo[4]
				
				listener = (self.cursorIndex, context, property)

				if (syncToPar):
					if(customName is not None):
						par = self.ownerComp.par[customName]
					else:
						par = self.ownerComp.par[self.formatString(property)]
				else:
					par = None

				#auto use dependency
				useDependency = True if (isLive and syncToPar) else False
				
				self.addListener(listener, isLive, par, replyOSC, castType, useDependency)

				# custom setup for remote control parameters
		for i in range(8):
			'''
			propertyInfo: [customName, live, mapPar, replyOSC, cast dataType]
			'name' 	: [None, False, False, False, None],
			'exists': [None, False, False, False, None],
			'val'	: ["Remotecontrol", True, True, True, None],
			'modVal': [None, True, False, False, None]
			'''
			curIndex = self.cursorIndex
			context = f"send{i}"
			#name
			nameListener = (curIndex, context, 'name')
			self.addListener(nameListener, False, None, False, None)
			#exists
			existListener = (curIndex, context, 'exists')
			self.addListener(existListener, False, None, False, None)
			#val
			valPar = self.ownerComp.par[f"Send{i}"]
			valListener = (curIndex, context, 'val')
			self.addListener(valListener, True, valPar, True, None, True)

		return

		return
	def setupPulsePars(self):

		for pName in self.pulseFunctionInfo.keys():
			#check if par exists and is correct type
			if (self.ownerComp.par[pName] is not None):
				pulsePar = self.ownerComp.par[pName]
				if(pulsePar.isPulse):
					pulseInfo = self.pulseFunctionInfo[pName]
					context = pulseInfo[0]
					replyFunction = pulseInfo[1]
					useParData = pulseInfo[2]
					if (useParData is not None):
						if (self.ownerComp.par[useParData] is None):
							print(f"Error! : useParData name {useParData} is invalid")
						else:
							useParData = self.ownerComp.par[useParData]
					cursorIndex = self.cursorIndex
					self.addPulsePar(pulsePar, cursorIndex, context, replyFunction, useParData)
				else:
					print('Error! Parameter: {pName} is not a pulse parameter')
			else:
				print(f"Error! Parameter: {pName} does not exist")

		return
	
	def handleInfoUpdate(self, listener, val):
		return
	
	def OnParValueChange(self, par, prev):
		
		name = par.name
		val  = par.eval()

		if name == 'Synccompcolortotrackcolor':
			if val == 1:
				self.ownerComp.color = self.ownerComp.parGroup.Color.eval()
		
		if name in ['Colorr', 'Colorg', 'Colorb']:
			if self.ownerComp.par.Synccompcolortotrackcolor:
				self.ownerComp.color = self.ownerComp.parGroup.Color.eval()

