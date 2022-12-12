# Support functions that will be moved into a separate file

def getEntryExit(name):
    entryExitPairs = jmri.InstanceManager.getDefault(jmri.jmrit.entryexit.EntryExitPairs)
    destinations = entryExitPairs.getNamedBeanSet()
    for d in destinations:
        if d.getUserName() == name:
            return d
    return None

# Retrieve event generating objects referenced in this Logix and
# attach a listener to them

def attachListener(logix, listener):
    # We need to keep track of objects that have already had
    # listeners attached. Don't want to attach duplicate
    # listeners!
    previouslyHandled = set()
    for l in logix:
        guardSet = set()
        l['guardSet'] = guardSet
        for g in l['guard']:
            otype = g[0]
            oid = g[1]
            #print('Object type: ' + otype + ' Object id: ' + oid)
            if (otype, oid) in previouslyHandled:
                #print('Skipping ' + otype + ' ' + oid)
                pass
            else:
                previouslyHandled.add((otype, oid))
                if otype == 'Sensor':
                    sensor = sensors.getSensor(oid)
                    if sensor is None:
                        print('ERROR Could not locate sensor ' + oid)
                    else:
                        sensor.addPropertyChangeListener(listener)
                        guardSet.add(sensor.getSystemName())
                        #print('Attached listener to sensor ' + oid)
                elif otype == 'Turnout':
                    turnout = turnouts.getTurnout(oid)
                    if turnout is None:
                        print('ERROR Could not locate turnout ' + oid)
                    else:
                        turnout.addPropertyChangeListener(listener)
                        guardSet.add(turnout.getSystemName())
                        #print('Attached listener to turnout' + oid)
                elif otype == 'EntryExit':
                    entryExit = getEntryExit(oid)
                    if entryExit is None:
                        print('ERROR Could not locate entry exit ' + oid)
                    else:
                        entryExit.addPropertyChangeListener(listener)
                        guardSet.add(entryExit.getSystemName())
                        #print('Attached listener to entry exit' + oid)
                else:
                    print ('ERROR Unknown object type ' + otype)
    print('Guard sets')
    for (i, l) in enumerate(logix):
        guards = ' '.join(l['guardSet'])
        print('Logix ' + str(i) + ' ' + guards)

def convertStateToString(state, objectType):
    if objectType == 'Turnout':
        if state == 2:
            return 'NORMAL'
        elif state == 4:
            return 'REVERSED'
        else:
            return ''
    if state == 2:
        return 'ACTIVE'
    elif state == 4:
        return 'INACTIVE'
    else:
        return ''

def evaluateGuard(guard):
    otype = guard[0]
    oid = guard[1]
    triggerState = guard[2]
    if otype == 'Sensor':
        sensor = sensors.getSensor(oid)
        state = convertStateToString(sensor.getKnownState(), otype)
        print( oid + ' ' + state + ' == ' + triggerState + '?')
        return state == triggerState
    elif otype == 'Turnout':
        turnout = turnouts.getTurnout(oid)
        state = convertStateToString(turnout.getKnownState(), otype)
        print( oid + ' ' + state + ' == ' + triggerState + '?')
        return state == triggerState
    elif otype == 'EntryExit':
        entryExit = getEntryExit(oid)
        state = convertStateToString(entryExit.getState(), otype)
        print( oid + ' ' + state + ' == ' + triggerState + '?')
        return state == triggerState
    return False

def evaluateGuards(guards, formula):
    if len(guards) == 1:
        return evaluateGuard(guards[0])
    truthValues = []
    for g in guards:
        truthValues.append(str(evaluateGuard(g)))
    f = formula % tuple(truthValues)
    print('Final formula: ' + f)
    value = eval(f)
    return value

def takeActions(actions):
    for (a_type, a_oid, a_state) in actions:
        if a_type == 'Turnout':
            t = turnouts.getTurnout(a_oid)
            if t is None:
                print('ERROR unknown turnout id ' + a_oid)
            else:
                if a_state == 'NORMAL':
                    t.state = CLOSED
                elif a_state == 'REVERSED':
                    t.state = THROWN
                else:
                    print('ERROR unknown turnout state ' + a_state)
                print( 'Setting turnout ' + a_oid + ' to ' + a_state)
        elif a_type == 'Sensor':
            s = sensors.getSensor(a_oid)
            if s is None:
                print('ERROR unknown sensor id' + a_oid)
            else:
                if a_state == 'ACTIVE':
                    s.state = ACTIVE
                elif a_state == 'INACTIVE':
                    s.state = INACTIVE
                else:
                    print('ERROR unknown sensor state ' + a_state)
                print( 'Setting sensor ' + a_oid + ' to ' + a_state )

# Sample event
# java.beans.PropertyChangeEvent[propertyName=KnownState; oldValue=4; newValue=2; propagationId=null; source=IS5001]
def handleEvent(event, logix):
    sname = event.getSource().getSystemName()
    print('Source: ' + sname)
    print('New value: ', + event.getNewValue())
    for i, l in enumerate(logix):
        if sname in l['guardSet']:
            print('Event captured by logix ' + str(i))
            # Now evaluate the actual conditions
            evaluation = evaluateGuards(l['guard'], l['formula'])
            print('Evaluated to: ' + str(evaluation))
            if evaluation:
                takeActions(l['action'])
        else:
            print('Event not captured by logix ' + str(i))


#----------------------------------------------------------------
# Actual code for Dover Logix begins here

doverLogix = [
# IX:AUTO:0007C1  Dover 1
{
    'guard' : [
        ('Sensor', 'Dover - Track 1', 'INACTIVE') 
        ],
    'formula' : '',
    'action': [
        ('Sensor', 'Dover - Track 2', 'ACTIVE'),
        ('Sensor', 'Dover - Track 3', 'ACTIVE'),
        ('Sensor', 'Dover - Track 4', 'ACTIVE'),
        ('Sensor', 'Dover - Track 5', 'ACTIVE'),
        ('Sensor', 'Dover - DOB Reverse', 'ACTIVE'),
        ('Turnout', 'DOCW', 'NORMAL'),
        ('Turnout', 'DODW', 'NORMAL'),
        ('Turnout', 'DOFW', 'NORMAL'),
        ('Turnout', 'DOBe-xbW', 'NORMAL'),
        ('Sensor', 'IS5010', 'INACTIVE')
        ]
},
# IX:AUTO:0007C3  Dover 2
{
    'guard' : [ 
        ('Sensor', 'IS5002', 'INACTIVE')
    ],
    'formula' : '',
    'action' : [
        ('Turnout', 'DOBe-xbW', 'NORMAL'),
        ('Turnout', 'DOCW', 'REVERSED'),
        ('Turnout', 'DODW', 'NORMAL'),
        ('Turnout', 'DOFW', 'NORMAL'),
        ('Sensor', 'IS5001', 'ACTIVE'),
        ('Sensor', 'IS5003', 'ACTIVE'),
        ('Sensor', 'IS5004', 'ACTIVE'),
        ('Sensor', 'IS5005', 'ACTIVE'),
        ('Sensor', 'IS5007', 'ACTIVE'),
        ('Sensor', 'IS5010', 'INACTIVE')
    ]
},
# IX:AUTO:0007C23  DOB Normal Track 3 
{
    'guard' : [
        ('Sensor', 'IS5010', 'INACTIVE'),
        ('Turnout', 'DOFW', 'NORMAL'),
        ('Turnout', 'DODW', 'REVERSED')
    ],
    'formula' : '%s and %s and %s',
    'action' : [
        ('Sensor', 'IS5003', 'INACTIVE')
    ]
 },
 # IX:AUTO:0007C24  DOB Normal Track 4
{
    'guard' : [
        ('Sensor', 'IS5010', 'INACTIVE'),
        ('Turnout', 'DOFW', 'REVERSED'),
        ('Turnout', 'DOEW', 'NORMAL')
    ],
    'formula' : '%s and %s and %s',
    'action' : [
        ('Sensor', 'IS5004', 'INACTIVE')
        ]
},
# IX:AUTO:0007C17  DOK Normal
{
    'guard' : [ ('Sensor', 'IS5015', 'INACTIVE')],
    'formula' : '',
    'action' : [
        ('Turnout', 'DOK-xW', 'NORMAL'),
        ('Sensor', 'IS5011', 'ACTIVE')
    ]
},
# IX:AUTO:0007C37  Dover NX 3-11
{
    'guard' : [ 
        ('EntryExit', 'Dover NX 3 (G-DO-4RA) to Dover NX 11 (G-DO-10R)', 'ACTIVE') 
    ],
    'formula' : '',
    'action' : [ 
        ('Sensor', 'IS5006', 'INACTIVE'),
        ('Sensor', 'IS5007', 'INACTIVE')
    ]
}
]

class DoverListener(java.beans.PropertyChangeListener):
    def propertyChange(self, event):
        handleEvent(event, doverLogix)

def dover_virtual():
    dl = DoverListener()
    attachListener(doverLogix, dl)

dover_virtual()