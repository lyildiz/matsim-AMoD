"""
File: nynetworkwriter

This function takes in the data from Zhang's MATLAB code
and writes a readable XML file for MATSIM
Forked from nynetworkwriter by Federico on Oct. 10, 2016
Works with new OSM map of NYC. Reads the correct number of lanes, speed limit and capacity
(capacity=length/vehicle length * number of lanes).
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
from collections import namedtuple
import numpy as np
import scipy.io as sio
import os.path
import math
import datetime
from datetime import datetime as dt
#import matlab.engine
import planparser
import pathwriter
import scipy.sparse as sp

FREESPEED = 14 #m/s

"""
Function writeNodes

This function takes in the top of the node tree
and the location of all the nodes and then writes
all of the nodes into the XML format that MATSim understands.
"""
def writeNodes(nodetree, NodesLocation):
	for i,node in enumerate(NodesLocation):
		nodexml = ET.SubElement(nodetree, 'node')
		nodexml.set('id', str(i+1))
		nodexml.set('x', str(node[0]))
		nodexml.set('y', str(node[1]))

"""
Function writeLinks

This function takes in the top of the linktree and
the necessary information about a link and writes
the links to the XML tree in such a way that MATSim will be
able to understand it.
"""
def writeLinks(linktree, RoadGraph, RoadCap, LinkLengths, NumLanes, LinkSpeed):
	count = 1
	for i,linklist in enumerate(RoadGraph):
		for destinations in linklist:
			listofdests = destinations[0]
			for dest in listofdests:
				linkxml = ET.SubElement(linktree, 'link')
				linkxml.set('id', str(count))
				count += 1
				linkxml.set('from', str(i+1))
				linkxml.set('to', str(dest))
				linkxml.set('length', str(LinkLengths[i,dest-1] + 5))
				linkxml.set('capacity', str(RoadCap[i,dest-1]))
				linkxml.set('freespeed', str(LinkSpeed[i,dest-1]))
				linkxml.set('permlanes', str(NumLanes[i,dest-1]))


"""
Function writeNYNetwork

This function takes in the NYC data from a .mat file and
writes it to an XML file that MATSim will be able to parse
and understand as a network.
"""
def writeNYNetwork():
	print "Loading file"
	filename = 'bin/zhangNYDataOSM.mat'
	raw = planparser.loadMatData(filename)
	print "Loading variables"
	RoadGraph = raw['RoadGraph']
	NodesLocation = raw['NodesLocation']
	RoadCap = sp.csr_matrix(raw['RoadCap'])
	TravelTimes = sp.csr_matrix(raw['LinkTime'])
	LinkLengths = sp.csr_matrix(raw['LinkLength'])
	NumLanes = sp.csr_matrix(raw['NumLanes'])
	LinkSpeed = sp.csr_matrix(raw['LinkSpeed'])

	print "Creating things"
	network = ET.Element('network')
	nodes = ET.SubElement(network, 'nodes')
	links = ET.SubElement(network, 'links')
	links.set('capperiod', '01:00:00')

	print "Calling writer for nodes"
	writeNodes(nodes, NodesLocation)
	print "Calling writer for links"
	writeLinks(links, RoadGraph, RoadCap, LinkLengths, NumLanes, LinkSpeed)

	parsed = pathwriter.cleanXML(network)

	parsed = parsed[0:22] + '\n<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v1.dtd">' + \
			 parsed[22:]
	
	print('saving')
	outfilename = 'res/NYOSMnetwork_225cap.xml'
	print "Saving"
	with open(outfilename, 'w') as f:
		f.write(parsed)



if __name__ == "__main__":
	writeNYNetwork()
