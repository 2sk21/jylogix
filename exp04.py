# Support functions that will be moved into a separate file

def getEntryExit(name):
    entryExitPairs = jmri.InstanceManager.getDefault(jmri.jmrit.entryexit.EntryExitPairs)
    destinations = entryExitPairs.getNamedBeanSet()
    for d in destinations:
        if d.getUserName() == name or d.getSystemName() == name :
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
        for j in l['guard']:
            otype = j[0]
            oid = j[1]
            print 'Object type', otype, 'Object id', oid
            if (otype, oid) in previouslyHandled:
                print('Skipping ' + otype + ' ' + oid)
            else:
                previouslyHandled.add((otype, oid))
                if otype == 'Sensor':
                    sensor = sensors.getSensor(oid)
                    if sensor is None:
                        print('Could not locate sensor ' + oid)
                    else:
                        sensor.addPropertyChangeListener(listener)
                        print('Attached listener to sensor ' + oid)
                elif otype == 'Turnout':
                    turnout = turnouts.getTurnout(oid)
                    if turnout is None:
                        print('Could not locate turnout ' + oid)
                    else:
                        turnout.addPropertyChangeListener(listener)
                        print('Attached listener to turnout' + oid)
                elif otype == 'EntryExit':
                    entryExit = getEntryExit(oid)
                    if entryExit is None:
                        print('Could not locate entry exit ' + oid)
                    else:
                        entryExit.addPropertyChangeListener(listener)
                        print('Attached listener to entry exit' + oid)
                else:
                    print ('Unknown object type ' + otype)

#----------------------------------------------------------------
# Actual code for Dover Logix begins here

doverLogix = [
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
{
    'guard' : [
        ('Sensor', 'IS5010', 'INACTIVE'),
        ('Turnout', 'DOFW', 'REVERSED'),
        ('Turnout', 'DOEW', 'NORMAL')
    ],
    'formula' : '{0} and {1} and {2}',
    'action' : [
        ('Sensor', 'IS5004', 'INACTIVE')
        ]
}
]

class DoverListener(java.beans.PropertyChangeListener):
    def propertyChange(self, event):
        print(event)

def dover_virtual():
    dl = DoverListener()
    attachListener(doverLogix, dl)

dover_virtual()