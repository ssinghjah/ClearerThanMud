#!/usr/bin/env python
import sys
from sklearn.feature_extraction import DictVectorizer
from sklearn import cluster
from scipy.spatial import distance
import numpy
import os
import csv
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hcluster
import sklearn.preprocessing as preprocessing
from collections import Counter
from sklearn.metrics import silhouette_samples, silhouette_score
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.cm as cm
from json import encoder
sys.path.append('../Yang')
import normalBehaviour as normalBehaviourYang
import simplejson as json

vec = DictVectorizer()
# Relative path to config files
featureUnitsFile = '../Config/featureUnits.json' 
featuresToClusterFile = "../Config/clusters.csv"

# Settings
trainingDbPath = '../FeatureExtractor/database/'
normalBehaviourDirPath = './NormalBehaviour/'

# Globals
FEATURE_UNITS=None

# Reads configuration files
def readConfig():
        featuresToCluster = []
        global FEATURE_UNITS
        # Read the cluster config file - specifies the feature combinations to cluster upon
        with open(featuresToClusterFile, 'rb') as csvfile:
                csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvReader:
                        featuresToClusterJoint=row[0]
                        featuresToClusterSplit = featuresToClusterJoint.split('_')
                        featuresToCluster.append({"features":featuresToClusterSplit}) 
        # Read the feature units, e.g. framelength is in bytes, inter-arrival in sec, etc
        with open(featureUnitsFile) as jsonFile:
                FEATURE_UNITS = json.load(jsonFile)
                
        return featuresToCluster

# Saves the normal behaviour as a json file
def saveNormalBehaviour(deviceId, normalBehaviour):
        deviceSpecDir = os.path.join(normalBehaviourDirPath, deviceId)
        if not os.path.isdir(deviceSpecDir):
                os.mkdir(deviceSpecDir)
        deviceSpecFile = os.path.join(deviceSpecDir, 'normalBehaviour.json')
        with open(deviceSpecFile, 'w') as outfile:
                json.dump(normalBehaviour, outfile)

# Saves the normal behaviour as a YANG file
def saveNormalBehaviourYANG(deviceId, normalBehaviour):
        deviceSpecDir = os.path.join(normalBehaviourDirPath, deviceId)
        if not os.path.isdir(deviceSpecDir):
                os.mkdir(deviceSpecDir)
        deviceSpecFile = os.path.join(deviceSpecDir, 'normalBehaviourYang.json')
        yangInstance = normalBehaviourYang.normalBehaviour()

        # Add feature stats
        for feature in normalBehaviour['featureStats']:
                featureStats = normalBehaviour['featureStats'][feature]
                # Add a feature
                featureStats = yangInstance.features.feature.add(feature)
                featureStats.mean = normalBehaviour['featureStats'][feature]['mean']
                featureStats.standardDeviation = normalBehaviour['featureStats'][feature]['std']

        normalCentroids = normalBehaviour['normalClusterCentroids']
        for featureCombination in normalCentroids:
                featureCombinationInfo = yangInstance.normalClusterDescription.normalClusters.add(featureCombination)
                features = featureCombination.split('_')
                centroidIndex = 0
                # Add centroids
                for centroid in normalCentroids[featureCombination]:
                        centroidInfo = featureCombinationInfo.centroids.add('centroid' + str(centroidIndex + 1))
                        centroidIndex += 1
                        # Add coordinates of a centroid
                        coordinateIndex = 0
                        for feature in features:
                                coordInfo = centroidInfo.coordinate.add(feature)
                                coordInfo.value = centroid[coordinateIndex]
                                coordinateIndex += 1
        with open(deviceSpecFile, 'w') as outfile:
                json.dump(yangInstance.get(), outfile)

# Standardizes all features, columnwise
def standardize(matrix):
        standardizedMatrix = numpy.zeros(matrix.shape)
        numColumns = matrix.shape[1]
        for colNum in range(0, numColumns):
                arr = matrix[:, colNum]
                arrMean = numpy.mean(arr)
                arrStd = numpy.std(arr)
                minusMean = (arr - arrMean)
                if arrStd != 0 :
                        standardizedMatrix[:, colNum] = minusMean/arrStd
                else :
                        standardizedMatrix[:, colNum] = minusMean
        return standardizedMatrix

def getNormalClusters(clusters):
        normalClusters=[]
        populationString=""
        counterOfClusters=Counter(clusters)
        #print(counterOfClusters)
        for clusterNum in counterOfClusters:
                populationString += "Cluster " + str(clusterNum) + ":" + str(counterOfClusters[clusterNum]) + " instances \n"
                normalClusters.append(clusterNum)
        return normalClusters

# Calculates centroids of clusters
def calculateCentroids(clusters, featuresArr, normalClusters):
        normalCentroids=[]
        clusterSizes = []
        for clusterNum in normalClusters:
                clusterIndices = [i for i, x in enumerate(clusters) if x == clusterNum]
                clusterMembers = (featuresArr[clusterIndices, :])
                centroid = numpy.average(clusterMembers, axis=0)
                clusterSize = -1
                farthestMember = []
                for member in clusterMembers:
                        distanceFromCentroid = distance.euclidean(centroid, member)
                        if distanceFromCentroid > clusterSize:
                                clusterSize = distanceFromCentroid
                                farthestMember = member
                normalCentroids.append(centroid)
                clusterSizes.append(clusterSize)
        return normalCentroids

# Calculates radius/size of each cluster
def calculateClusterSizes(clusters, centroids, featuresArr):
        clusterSizes = []
        counterOfClusters=Counter(clusters)
        for clusterNum in counterOfClusters:
                clusterIndices = [i for i, x in enumerate(clusters) if x == clusterNum]
                clusterMembers = (featuresArr[clusterIndices, :])
                centroid = centroids[clusterNum-1]      
                # Calculate cluster sizes
                clusterSize = -1
                farthestMember = []
                for member in clusterMembers:
                        distanceFromCentroid = distance.euclidean(centroid, member)
                        if distanceFromCentroid > clusterSize:
                                clusterSize = distanceFromCentroid
                                farthestMember = member
                clusterSizes.append(clusterSize)
                                         
        return clusterSizes


def calculateAllCentroids(clusters, featuresArr, normalClusters):
        centroids = []
        clusterSize = []
        clusterSizes = []
        centroids = []
        counterOfClusters=Counter(clusters)
        for clusterNum in counterOfClusters:
                clusterIndices = [i for i, x in enumerate(clusters) if x == clusterNum]
                clusterMembers = (featuresArr[clusterIndices, :])
                centroid = numpy.average(clusterMembers, axis=0)
                centroids.append(centroid)
                        
        return centroids

# Parses all the saved features of a device into a structure
def parseAllTrainingData(deviceId):
        numPackets = 0
        packetFeatures={}
        deviceTrainingData = os.path.join(trainingDbPath, deviceId)
        for filename in os.listdir(deviceTrainingData):
                if filename.endswith(".json"):
                        with open(os.path.join(deviceTrainingData, filename)) as f:
                                recordedFeatures = json.load(f)
                                validPacket = True
				for recordedFeature in recordedFeatures:
                                        if(not recordedFeature in packetFeatures):
                                                packetFeatures[recordedFeature]=[]
                                        # Do not parse invalid packets - e.g. first packet has an undefined inter-arrival time
                                        if(recordedFeatures[recordedFeature] is None):
						validPacket = False
                                                break
                                        
                                        packetFeatures[recordedFeature].append(recordedFeatures[recordedFeature])
				if validPacket:
					numPackets += 1
        return packetFeatures, numPackets
        

def showSilhouette(data, clusterLabels, title, destandardizedNormalCentroids):
        fig = plt.figure()
        ax = plt.gca()
        ax.set_xlim([-0.1, 1])
        silhouette_avg = silhouette_score(data, clusterLabels)
        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(data, clusterLabels)
        y_lower = 10
        nClusters = len(set(clusterLabels))
        for i in range(1, nClusters+1):
                # Aggregate the silhouette scores for samples belonging to
                # cluster i, and sort them
                ith_cluster_silhouette_values = \
                                        sample_silhouette_values[clusterLabels == i]
                ith_cluster_silhouette_values.sort()
                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                         
                y_upper = y_lower + size_cluster_i
                color = cm.spectral(float(i) / nClusters)
                ax.fill_betweenx(numpy.arange(y_lower, y_upper),
                          0, ith_cluster_silhouette_values,
                          facecolor=color, edgecolor=color, alpha=0.7)

                # Label the silhouette plots with their cluster numbers at the middle
                # Avoid cluster labels overlapping with each other
                if(size_cluster_i < 6):
                        size_cluster_i = 20
                        y_upper = y_lower + size_cluster_i
                ax.text(0.2, y_lower + 0.5 * size_cluster_i, "Cluster-" + str(i) + ": " + destandardizedNormalCentroids[i-1])
                
                
                # Compute the new y_lower for next plot
                y_lower = y_upper + 10  # 10 for the 0 samples
                
        ax.set_xlabel("Silhouette coefficient values")
        ax.set_ylabel("")
        # The vertical line for average silhouette score of all the values
        ax.axvline(x=silhouette_avg, color="red", linestyle="--")
        #ax.set_yticks([1, data.shape[0])  # Clear the yaxis labels / ticks
        ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
        plt.suptitle((title),
                 fontsize=14, fontweight='bold')
        fig.show()

# Shows a histogram of cluster populations
def createHistogram(clusters, featuresToClusterStr, deviceName):
        numClusters = len(set(clusters)) + 1
        fig = plt.figure()
        barWidth = 0.1
        index = numpy.arange(numClusters) - barWidth/2
        ax = plt.gca()
        counterOfClusters=Counter(clusters)
        counts=numpy.zeros(numClusters)
        yOffset = 1 
        for clusterIndex in counterOfClusters:
                counts[clusterIndex] = counterOfClusters[clusterIndex]
                ax.text(clusterIndex - 0.1, counts[clusterIndex] + yOffset, "C" + str(clusterIndex) + ": " + str(int(counts[clusterIndex])))
        ax.set_xticks(numpy.arange(numClusters))
        ax.set_xlabel("Cluster number")
        ax.set_ylabel("Cluster population")
        ax.bar(index, counts, barWidth)
        plt.title("Cluster population, " + deviceName + ": " + str(featuresToClusterStr))
        fig.show()

# Destandardizes centroids, so that they can be displayed and interpreted        
def destandardizeCentroids(features, normalCentroids, packetFeatures):
        displayStrs=[]
        displayStr=""
        destdCentroids = []
        numNormalCentroids=len(normalCentroids)
        normalCentroidCounter=0
        means=calculateMeans(packetFeatures)
        stds=calculateStds(packetFeatures)
        for normalCentroid in normalCentroids:
                displayStr=""
                featureCounter=0
                numFeatures=len(features)
                destdCentroid = []
                for feature in features:
                        destandardizedFeatureValue = normalCentroid[featureCounter]*stds[feature] + means[feature]
                        numDecimalPlaces=2
                        # Frame length should not be displayed in decimals
                        if feature == "frameLength":
                                featureValue = str(int(destandardizedFeatureValue))
                        else :
                                featureValue = str(round(destandardizedFeatureValue, numDecimalPlaces))
                        displayStr += feature + " = " + featureValue + " " + FEATURE_UNITS[feature]
                        if featureCounter < (numFeatures - 1):
                                displayStr += " and "
                        featureCounter += 1
                        destdCentroid.append(destandardizedFeatureValue)
                displayStrs.append(displayStr)
                destdCentroids.append(destdCentroid)
        return displayStrs, destdCentroids

def createFeaturesArray(featuresToCluster, packetFeatures, numPackets):
	featuresArr=[]
        arr2d=numpy.empty([numPackets, len(featuresToCluster)])
        columnNumber = 0
        for featureToCluster in featuresToCluster:
                arr2d[:, columnNumber] = (packetFeatures[featureToCluster])[0:numPackets]
                columnNumber += 1
        return arr2d


def doClustering(featuresToCluster, packetFeatures, deviceName, numPackets):
        featuresToClusterStr = ','.join(featuresToCluster)        
        # Read the desired features of all packets in the training database 
        featuresArr = createFeaturesArray(featuresToCluster, packetFeatures, numPackets)
        # Preprocess, i.e. standardize
        preprocessedFeaturesArr = standardize(featuresArr)
        # Generate a linkage matrix to find the best cutoff distance value for hierarchical clustering
        Z = linkage(preprocessedFeaturesArr, 'single')
	distanceJumps = numpy.diff(Z[:,2])
        maxJumpIndices = distanceJumps.argsort()[-10:][::-1]
        maxJumpIndex = numpy.argmax(Z[:,2])
        cutoffDistance = Z[maxJumpIndex-1, 2]
        maxSilhouetteScore = -1
        optimumClusterLabels = []
        #Iterate over each max jump index                       
        for maxJumpIndex in maxJumpIndices:
                # The jump is calculated between this and the next index, so calculate cutoff distance as halfway in between                 
                thisIndexDist = Z[maxJumpIndex, 2]
                nextIndexDist = Z[maxJumpIndex + 1, 2]
                cutoffDistance = (nextIndexDist + thisIndexDist)/2.0

                # Perform hierarchical clustering                                                       
                candidateClusterLabels = hcluster.fclusterdata(preprocessedFeaturesArr, cutoffDistance, criterion="distance")
                if(len(set(candidateClusterLabels)) > 1):
                        # Calculate the silhouette score
                        candidateSilhouetteScore = silhouette_score(featuresArr, candidateClusterLabels, metric='euclidean')
                else:
                        candidateSilhouetteScore = -1
                        optimumClusterLabels = candidateClusterLabels
                        # Check if this is the max silhouette score                                         
                if candidateSilhouetteScore > maxSilhouetteScore:
                        maxSilhouetteScore  = candidateSilhouetteScore
                        optimumClusterLabels = candidateClusterLabels

  	# Get normal clusters
        normalClusters = getNormalClusters(optimumClusterLabels)

        # Calculate centroids of normal clusters
        centroids = calculateAllCentroids(optimumClusterLabels, preprocessedFeaturesArr, normalClusters)
        
        # Histogram analysis                                                                                                                  
        #createHistogram(clusterLabels, featuresToClusterStr, deviceName)                                                                     

        destandardizedNormalCentroids,destdCentroidValues = destandardizeCentroids(featuresToCluster, centroids, packetFeatures)

        sizes = calculateClusterSizes(optimumClusterLabels, destdCentroidValues, featuresArr)

        
#        if(len(set(optimumClusterLabels)) > 1):                                                                                              
#                showSilhouette(featuresArr, optimumClusterLabels, deviceName + ": " + featuresToClusterStr, destandardizedNormalCentroids)   
        #print("-----------------------------------------")                                                                                   
        return centroids

	
	
	
def updateNormalDescription(normalCentroids, features, normalBehaviour):
        featureStr = '_'.join(features)
        numNormalCentroids = len(normalCentroids)
        centroidsArr = []
        for normalCentroid in normalCentroids:
                centroidsArr.append(normalCentroid.tolist())                
        normalBehaviour['normalClusterCentroids'][featureStr] = centroidsArr

means={}
stds={}
def calculateMeans(packetFeatures):
        means={}
        for feature in packetFeatures:
                means[feature]=numpy.mean(packetFeatures[feature])
        return means

def calculateStds(packetFeatures):
        stds={}
        for feature in packetFeatures:
                stds[feature]=numpy.std(packetFeatures[feature])
        return stds

def calculateFeatureStats(packetFeatures):
        featureStats = {}
        means = calculateMeans(packetFeatures)
        stds = calculateStds(packetFeatures)
        for feature in packetFeatures:
                featureStats[feature] = {}
                featureStats[feature]['mean'] = means[feature]
                featureStats[feature]['std'] = stds[feature]
        return featureStats
        
def addAction(normalBehaviour):
        normalBehaviour["action"] = "DROP"

def printNormalBehaviour(deviceName, normalBehaviour):
        print("The normal behaviour for " + deviceName + " is - ")
        for clusteringType in normalBehaviour['normalClusterCentroids']:
                features = clusteringType.split("_")
                normalCentroids = normalBehaviour['normalClusterCentroids'][clusteringType]
                displayStr=""
                numNormalCentroids = len(normalCentroids)
                normalCentroidCounter = 0
                for normalCentroid in normalCentroids:     
                        featureCounter = 0
                        numFeatures=len(features)
                        for feature in features:
                                destandardizedFeatureValue = normalCentroid[featureCounter]*normalBehaviour['stds'][feature] + normalBehaviour['means'][feature]
                                numDecimalPlaces=2
                                if feature == "frameLength":
                                        featureValue = str(int(destandardizedFeatureValue))
                                else :
                                        featureValue = str(round(destandardizedFeatureValue, numDecimalPlaces))
                                displayStr += feature + " = " + featureValue + " " + FEATURE_UNITS[feature]
                                if featureCounter < (numFeatures - 1):
                                        displayStr += " and "
                                featureCounter += 1
                        if normalCentroidCounter < (numNormalCentroids - 1):
                                displayStr += " or "
                        normalCentroidCounter += 1
        print(displayStr)
        print("---------------------------------------------------------------------------")

# Generates the normal behaviour model for a device
def processDeviceData(deviceId):
        # Get the list of features to cluster on
        featuresToClusterList=readConfig()
        normalBehaviour={'normalClusterCentroids':{}}
        # Parse all saved features from the database
        packetFeatures,numPackets=parseAllTrainingData(deviceId)
        # Perform clustering for each feature combination
        for featuresToCluster in featuresToClusterList:
                deviceName = deviceId
                # Get the cluster centroids as a result of clustering
                normalCentroids = doClustering(featuresToCluster["features"], packetFeatures, deviceName, numPackets)
                # Save the centroids to the normal behaviour model
                updateNormalDescription(normalCentroids, featuresToCluster["features"], normalBehaviour)
        # Save the mean and std of all features to the normal behaviour mode. These values will be used by the enforcer to standardize real time observations and then check if they are close enough to the normal cluster centroids.
        normalBehaviour['featureStats'] = calculateFeatureStats(packetFeatures)
        normalBehaviour["means"] = calculateMeans(packetFeatures)
        normalBehaviour["stds"] = calculateStds(packetFeatures)
        # Add action to drop all traffic
        addAction(normalBehaviour)
        # Save the normal behaviour model in both JSON and YANG formats
        saveNormalBehaviour(deviceId, normalBehaviour)
        saveNormalBehaviourYANG(deviceId, normalBehaviour)
        # Display the normal behaviour model
        printNormalBehaviour(deviceId, normalBehaviour)

# Generates normal behaviour models for each device
def run():
        # Iterate over the database folder for each device
        deviceIds=[folder for folder in os.listdir(trainingDbPath) if os.path.isdir(os.path.join(trainingDbPath, folder))]
        for deviceId in deviceIds:
                processDeviceData(deviceId)
        raw_input("Enter to quit ...")
                
run()
