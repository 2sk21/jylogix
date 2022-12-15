# Support functions for the Jython implementation of Logix
# Copyright (c) 2022 Rangachari Anand

def getEntryExit(name):
    entryExitPairs = jmri.InstanceManager.getDefault(jmri.jmrit.entryexit.EntryExitPairs)
    destinations = entryExitPairs.getNamedBeanSet()
    for d in destinations:
        if d.getUserName() == name:
            return d
        elif d.getSystemName() == name:
            return d
    return None

# Retrieve event generating objects referenced in this Logix and
# attach a listener to them

def attachListener(logix, listener):
    # We need to keep track of objects that have already had
    # listeners attached. Don't want to attach duplicate
    # listeners!
    previouslyHandled = set()
    for conditional in logix:
        guardSet = set()
        conditional['guardSet'] = guardSet
        for g in conditional['guard']:
            otype = g[0]
            oid = g[1]
            if otype == 'Sensor':
                sensor = sensors.getSensor(oid)
                if sensor is None:
                    print('ERROR Could not locate sensor ' + oid)
                else:
                    guardSet.add(sensor.getSystemName())
                    if (otype, oid) in previouslyHandled:
                        pass
                    else:
                        sensor.addPropertyChangeListener(listener)
                        previouslyHandled.add((otype, oid))
                        print('Attached listener to sensor ' + oid)
            elif otype == 'Turnout':
                turnout = turnouts.getTurnout(oid)
                if turnout is None:
                    print('ERROR Could not locate turnout ' + oid)
                else:
                    guardSet.add(turnout.getSystemName())
                    if (otype, oid) in previouslyHandled:
                        pass
                    else:
                        turnout.addPropertyChangeListener(listener)
                        previouslyHandled.add((otype, oid))
                        print('Attached listener to turnout' + oid)
            elif otype == 'EntryExit':
                entryExit = getEntryExit(oid)
                if entryExit is None:
                    print('ERROR Could not locate entry exit ' + oid)
                else:
                    guardSet.add(entryExit.getSystemName())
                    if (otype, oid) in previouslyHandled:
                        pass
                    else:
                        entryExit.addPropertyChangeListener(listener)
                        previouslyHandled.add((otype, oid))
                        print('Attached listener to entry exit' + oid)
            else:
                print ('ERROR Unknown object type ' + otype)
    print('Guard sets')
    for (i, l) in enumerate(logix):
        guards = ' '.join(l['guardSet'])
        print('Conditional ' + l['id'] + ' Guards:' + guards)

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
                print( 'Action setting turnout ' + a_oid + ' to ' + a_state)
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
                print( 'Action setting sensor ' + a_oid + ' to ' + a_state )

# Sample event
# java.beans.PropertyChangeEvent[propertyName=KnownState; oldValue=4; newValue=2; propagationId=null; source=IS5001]
def handleEvent(event, logix):
    sname = event.getSource().getSystemName()
    print('Event source: ' + sname + ' New value ' + str(event.getNewValue()))
    for l in logix:
        if sname in l['guardSet']:
            print('Event captured by logix ' + l['id'])
            # Now evaluate the actual conditions
            evaluation = evaluateGuards(l['guard'], l['formula'])
            print('Evaluated to: ' + str(evaluation))
            if evaluation:
                takeActions(l['action'])
        else:
            #print('Event not captured by logix ' + str(i))
            pass


