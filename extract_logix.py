# Author Rangachari Anand Copyright (C) 2022
# This is free software; you can redistribute it and/or modify it under the
# terms of version 2 of the GNU General Public License as published by the Free
# Software Foundation.

import xml.etree.ElementTree as ET
import argparse
from pprint import pprint

def getAllLogix(root):
    queryString = '.logixs/logix'
    return root.findall(queryString)

def getConditionalBySystemName(root, systemName):
    queryString = ".conditionals/conditional/systemName[.='%s']/.." % systemName
    conditionals = root.findall(queryString)
    if len(conditionals) != 1:
        return None
    else:
        return conditionals[0]

def addToFormula(formula, operator):
    if operator == '1':
        formula = formula + ' and %s'
    elif operator == '4':
        formula = formula + '%s'
    elif operator == '5':
        formula = formula + ' or %s'
    else:
        print('Error unknown operator: ' + operator)
    return formula

def processLogixConditional(root, logixSystemName, logixUserName, conditionalSystemName):
    conditional = getConditionalBySystemName(root, conditionalSystemName)
    #print( conditional.attrib['userName'], conditional.attrib['systemName'])
    guards = []
    formula = ''
    actions = []
    for child in conditional:
        if child.tag == 'conditionalStateVariable':
            csvType = child.attrib['type']
            operator = child.attrib['operator']
            csvName = child.attrib['systemName']
            csvDataString = child.attrib['dataString']
            # See the file Conditional.java in JMRI for the magic numbers used here
            if csvType == '1':
                # Sensor goes active
                guards.append(('Sensor', csvName, 'ACTIVE'))
                formula = addToFormula(formula, operator)
            elif csvType == '2':
                # Sensor goes inactive
                guards.append(('Sensor', csvName, 'INACTIVE'))
                formula = addToFormula(formula, operator)
            elif csvType == '3':
                # Turnout is thrown
                guards.append(('Turnout', csvName, 'REVERSE'))
                formula = addToFormula(formula, operator)
            elif csvType == '4':
                # Turnout is closed
                guards.append(('Turnout', csvName, 'NORMAL'))
                formula = addToFormula(formula, operator)
            elif csvType == '30':
                # Signal mast aspect equals
                guards.append(('SignalMastAspect', csvName, csvDataString))
                formula = addToFormula(formula, operator)
            elif csvType == '35':
                # EntryExit is active
                guards.append(('EntryExit', csvName, 'ACTIVE'))
                formula = addToFormula(formula, operator)
            elif csvType == '36':
                # EntryExit is active
                guards.append(('EntryExit', csvName, 'INACTIVE'))
                formula = addToFormula(formula, operator)
            else:
                print('ERROR unsuported csvType: ', csvType, logixSystemName, conditionalSystemName, csvName)
        elif child.tag == 'conditionalAction':
            # See Conditional.java
            # static final int ACTION_OPTION_ON_CHANGE_TO_TRUE = 1;
            # static final int ACTION_OPTION_ON_CHANGE_TO_FALSE = 2;
            # static final int ACTION_OPTION_ON_CHANGE = 3;
            caOption = child.attrib['option']
            if caOption == '1':
                optionModifier = 'if_true'
            elif caOption == '2':
                optionModifier = 'if_false'
            elif caOption == '3':
                optionModifier = 'if_change'
            caType = child.attrib['type']
            caName = child.attrib['systemName']
            caData = child.attrib['data']
            caString = child.attrib['string']
            # See DefaultConditionalAction.java
            if caType == '2':
                # Set turnout
                if caData == '2':
                    actions.append(('Turnout', caName, 'NORMAL', optionModifier))
                elif caData == '4':
                    actions.append(('Turnout', caName, 'REVERSE', optionModifier))
                elif caData == '8':
                    actions.append(('Turnout', caName, 'TOGGLE', optionModifier))
                else:
                    print('Error unknown data for turnout action: ' + caData, logixSystemName, conditionalSystemName, csvName)
            elif caType == '3':
                actions.append(('SignalHead', caName, caString, optionModifier))
            elif caType == '9':
                # Set sensor
                if caData == '2':
                    actions.append(('Sensor', caName, 'ACTIVE', optionModifier))
                elif caData == '4':
                    actions.append(('Sensor', caName, 'INACTIVE', optionModifier))
                elif caData == '8':
                    actions.append(('Sensor', caName, 'TOGGLE', optionModifier))
                else:
                    print('Error unknown data for sensor action: ' + caData, logixSystemName, conditionalSystemName, csvName)
            elif caType == '37':
                # Set signal mast aspect
                actions.append(('SignalMast', caName, caString, optionModifier))
            elif caType == '11':
                # Set light
                if caData == '2':
                    actions.append(('Light', caName, 'ACTIVE', optionModifier))
                elif caData == '4':
                    actions.append(('Light', caName, 'INACTIVE', optionModifier))
                elif caData == '8':
                    actions.append(('Light', caName, 'TOGGLE', optionModifier))
                else:
                    print('Error unknown data for light action: ' + caData, logixSystemName, conditionalSystemName, csvName)
            elif caType == '10':
                return None
            else:
                print('ERROR unhandled conditional action: ', caType, logixSystemName, conditionalSystemName)
    if len(guards) == 1:
        formula = ''
    result = {
        'guard' : guards,
        'formula' : formula,
        'action' : actions,
        'id' : logixSystemName + ' ' + conditionalSystemName
    }
    return result


def main(args):
    ifn = args.inputFile
    tree = ET.parse(ifn)
    root = tree.getroot()
    logixs = getAllLogix(root)
    for logix in logixs:
        logixList = []
        logixUserName = ''
        logixSystemName = ''
        for child in logix:
            if child.tag == 'userName':
                logixUserName = child.text
            elif child.tag == 'systemName':
                logixSystemName = child.text
            elif child.tag == 'logixConditional':
                conditionalSystemName = child.attrib['systemName']
                conditional = processLogixConditional(root, logixSystemName, logixUserName, conditionalSystemName)
                if conditional == None:
                    print("Skipping conditional with timed action", logixUserName, conditionalSystemName)
                else:
                    logixList.append(conditional)
        logixVarName = logixUserName.replace('/', '')
        logixVarName = logixVarName.replace(' ', '')
        objectVarName = logixVarName + 'Listener'
        fileName = logixVarName + '.py'
        with open(args.scriptDir + '/' + fileName, 'w') as fp:
            fp.write(logixVarName + '=')
            pprint(logixList, indent=4, stream=fp, sort_dicts=False)
            fp.write('\n')
            stmt = '%s = JylogixListener(%s)\n' % (objectVarName, logixVarName)
            fp.write(stmt)
            stmt = '%s.attach()\n' % objectVarName
            fp.write(stmt)
            stmt = '%s.handleStartup()\n' % objectVarName
            fp.write(stmt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deconstruct a JMRI XML formatted layout description file')
    parser.add_argument('inputFile', type=str, help='JMRI layout description file in XML format')
    parser.add_argument('--scriptDir', type=str, default='.', help='Directory to store the generated script files.')
    args = parser.parse_args()
    main(args)