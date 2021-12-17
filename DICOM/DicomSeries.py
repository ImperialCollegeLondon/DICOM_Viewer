import numpy as np
import pydicom
from pydicom import dicomio

from DICOM import DicomAbstractContainer
from DICOM.DicomAbstractContainer import ViewMode
from DICOM.DicomFileWrapper import DicomFileWrapper


class DicomSeries(DicomAbstractContainer.DicomAbstractContainerClass):
    """
    This type represents a Dicom series as a list of Dicom files sharing a series UID. The assumption is that the images
    of a series were captured together and so will always have a number of fields in common, such as patient name, so
    Dicoms should be organized by series. This type will also cache loaded Dicom tags and images
    """

    def __init__(self, seriesID, rootDir):

        super().__init__()
        self.seriesID = seriesID  # ID of the series or ???
        self.rootDir = rootDir  # directory Dicoms were loaded from, files for this series may be in subdirectories
        self.filenames = []  # list of filenames for the Dicom associated with this series
        self.dicomFilesList = {}
        self.sortedFileNamesList = []  # list of filenames but sorted according to SliceLocation field
        self.dicomFilesIndexesDict = {}
        self.dicomFilesPathsDicts = {}
        self.loadTags = []  # loaded abbreviated tag->(name,value) maps, 1 for each of self.filenames
        self.imgCache = {}  # image data cache, mapping index in self.filenames to arrays or None for non-images files
        self.tagCache = {}  # tag values cache, mapping index in self.filenames to OrderedDict of tag->(name,value) maps
        self._size = 0
        self.pixelsDataTuple = None
        self.dicomFileIndexesCache = []
        self.supportDcmFiles = None
        self.slice_thickness = None

    @property
    def size(self):
        return self._size

    def addFile(self, filename, loadTag):
        """Add a filename and abbreviated tag map to the series."""
        self.filenames.append(filename)
        self.loadTags.append(loadTag)

    def getExtraTagValues(self):
        """Return the extra tag values calculated from the series tag info stored in self.filenames."""
        start, interval, numTimes = self.getTimestepSpec()
        extraVals = {
            "NumImages":    len(self.filenames),
            "TimestepSpec": "start: %i, interval: %i, # Steps: %i"
                            % (start, interval, numTimes),
            "StartTime":    start,
            "NumTimesteps": numTimes,
            "TimeInterval": interval,
        }

        return extraVals

    def getTagValues(self, names, index = 0):
        """Get the tag values for tag names listed in `names' for image at the given index."""
        if not self.filenames:
            return ()

        if self.pixelsDataTuple is None:
            dcm = self.getDicomRawImage(index = index).getDicomFile()

        else:
            dcm = self.getDicomFile(index)

        extraVals = self.getExtraTagValues()

        # TODO: kludge? More general solution of telling series apart
        # dcm.SeriesDescription=dcm.get('SeriesDescription',dcm.get('SeriesInstanceUID','???'))

        return tuple(str(dcm.get(n, extraVals.get(n, ""))) for n in names)

    def getPixelData(self, index, mode: ViewMode = ViewMode.ORIGINAL):
        """Get the pixel data array for file at position `index` in self.filenames, or None if no pixel data."""

        return self.getDicomFile(index).getPixelData(mode)

    def computeDicomFile(self, index):

        currentSlice = self.supportDcmFiles[index]
        currentSlice.SliceThickness = self.slice_thickness
        originalImg = self.pixelsDataTuple[index]

        dcmFile = DicomFileWrapper(fileName = self.sortedFileNamesList[index], dicomData = currentSlice,
                                   originalImg = originalImg)
        self.dicomFilesList[index] = dcmFile
        self.dicomFilesIndexesDict[index] = dcmFile

    def loadPixelDataTuple(self):
        if self.pixelsDataTuple is None:
            self.pixelsDataTuple = self.get_pixels_hu(self.supportDcmFiles)

    def getPixelDataList(self, mode: ViewMode = ViewMode.ORIGINAL):

        pixelData = []

        for index in range(0, self._size):
            data = self.getPixelData(index, mode)[0, :, :]
            pixelData.append(np.uint8(data))

        return pixelData

    def getDicomFile(self, index):

        if index not in self.dicomFileIndexesCache:
            self.computeDicomFile(index = index)
            self.dicomFileIndexesCache.append(index)

        return self.dicomFilesList[index]

    def getDicomRawImage(self, index: int):
        if self.pixelsDataTuple is None:
            return DicomFileWrapper(fileName = self.sortedFileNamesList[index])
        else:
            return self.getDicomFile(index = 0)

    def getPixelDataFromPath(self, path, mode: ViewMode = ViewMode.ORIGINAL):
        try:
            index = self.getIndexFromPath(path)
            return self.getPixelData(index, mode)
        except:
            return None

    def getIndexFromPath(self, path):
        try:
            return self.dicomFilesPathsDicts.get(path)
        except:
            return None

    def addSeries(self, series):
        """Add every loaded dcm file from DicomSeries object `series` into this series."""
        for f, loadTag in zip(series.filenames, series.loadTags):  # TODO FIX THIS
            self.addFile(f, loadTag)

    def getTimestepSpec(self, tag = "TriggerTime"):
        """Returns (start time, interval, num timesteps) triple."""
        times = sorted(set(int(loadTag.get(tag, 0)) for loadTag in self.loadTags))

        if not times or times == [0]:
            return 0.0, 0.0, 0.0
        else:
            if len(times) == 1:
                times = times * 2

            avgSpan = np.average([b - a for a, b in zip(times, times[1:])])
            return times[0], avgSpan, len(times)

    def computeSliceThickness(self):
        if self.slice_thickness is None:
            try:
                self.slice_thickness = np.abs(
                        self.supportDcmFiles[0].ImagePositionPatient[2] - self.supportDcmFiles[1].ImagePositionPatient[2])
            except:
                self.slice_thickness = np.abs(self.supportDcmFiles[0].SliceLocation - self.supportDcmFiles[1].SliceLocation)

    def sortSeries(self):

        self.supportDcmFiles = []
        # skip files with no SliceLocation (eg scout views)

        for i in range(len(self.filenames)):
            dcm = pydicom.dcmread(self.filenames[i])
            if "SliceLocation" in dcm:
                filename = self.filenames[i]
                self.supportDcmFiles.append((dcm, filename))

        # ensure they are in the correct order
        self.supportDcmFiles = sorted(self.supportDcmFiles, key = lambda s: s[0].SliceLocation, reverse = True)

        cleanSupport = []

        for i in range(len(self.supportDcmFiles)):
            self.sortedFileNamesList.append(self.supportDcmFiles[i][1])
            cleanSupport.append(self.supportDcmFiles[i][0])
            self.dicomFilesPathsDicts[self.sortedFileNamesList[i]] = i

        self.supportDcmFiles = cleanSupport

        self._size = len(self.supportDcmFiles)
