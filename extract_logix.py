# Author Rangachari Anand Copyright (C) 2022
# This is free software; you can redistribute it and/or modify it under the
# terms of version 2 of the GNU General Public License as published by the Free
# Software Foundation.

import xml.etree.ElementTree as ET
import argparse

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

def processLogixConditional(root, logixSystemName, logixUserName, conditionalSystemName):
    conditional = getConditionalBySystemName(root, conditionalSystemName)
    print( conditional.attrib['userName'], conditional.attrib['systemName'])

def main(args):
    ifn = args.inputFile
    tree = ET.parse(ifn)
    root = tree.getroot()
    logixs = getAllLogix(root)
    for logix in logixs:
        print('======')
        logixUserName = ''
        logixSystemName = ''
        for child in logix:
            if child.tag == 'userName':
                logixUserName = child.text
            elif child.tag == 'systemName':
                logixSystemName = child.text
            elif child.tag == 'logixConditional':
                conditionalSystemName = child.attrib['systemName']
                processLogixConditional(root, logixSystemName, logixUserName, conditionalSystemName)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deconstruct a JMRI XML formatted layout description file')
    parser.add_argument('inputFile', type=str, help='JMRI layout description file in XML format')
    args = parser.parse_args()
    main(args)