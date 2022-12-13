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
    print( conditional.attrib['userName'], conditional.attrib['systemName'])
    guards = []
    formula = ''
    actions = []
    for child in conditional:
        if child.tag == 'conditionalStateVariable':
            csvType = child.attrib['type']
            operator = child.attrib['operator']
            csvName = child.attrib['systemName']
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
                guards.append(('Turnout', csvName, 'REVERSED'))
                formula = addToFormula(formula, operator)
            elif csvType == '4':
                # Turnout is closed
                guards.append(('Turnout', csvName, 'NORMAL'))
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
                print('ERROR unsuported csvType: ', csvType)
        elif child.tag == 'conditionalAction':
            caType = child.attrib['type']
            caName = child.attrib['systemName']
            caData = child.attrib['data']
            if caType == '2':
                # Set turnout
                if caData == '2':
                    actions.append(('Turnout', caName, 'NORMAL'))
                elif caData == '4':
                    actions.append(('Turnout', caName, 'REVERSED'))
                else:
                    print('Error unknown data for turnout action: ' + caData)
            elif caType == '9':
                # Set sensor
                if caData == '2':
                    actions.append(('Sensor', caName, 'ACTIVE'))
                elif caData == '4':
                    actions.append(('Sensor', caName, 'INACTIVE'))
                else:
                    print('Error unknown data for sensor action: ' + caData)
    if len(guards) == 1:
        formula = ''
    result = {
        'guard' : guards,
        'formula' : formula,
        'action' : actions
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
                logixList.append(conditional)
        fileName = logixUserName + '.py'
        fileName = fileName.replace('/', ' ')
        with open(fileName, 'w') as fp:
            pprint(logixList, indent=4, stream=fp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deconstruct a JMRI XML formatted layout description file')
    parser.add_argument('inputFile', type=str, help='JMRI layout description file in XML format')
    args = parser.parse_args()
    main(args)