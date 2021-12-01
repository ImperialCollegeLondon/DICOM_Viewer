from functools import partial

from PyQt6 import QtCore, QtWidgets
from DICOM.DicomAbstractContainer import ViewMode
from GUI.menus.AbstractMenu import AbstractMenu


class MenuAlterations(AbstractMenu):

    def __init__(self, menuBar):
        super().__init__(menuBar, "menuAlterations")

        self.__defineActions()
        self.__addActions()
        self.__retranslateUI()

        self.viewModeMenuOptions = self.ViewModeMenuOptions(self)
        self.selectedViewModeMenuOption = self.viewModeMenuOptions.ORIGINAL
        self.disableOptions()
        self.__connectActions()

    class ViewModeMenuOptions:

        def __init__(self, menuAlterations):
            self.ORIGINAL = menuAlterations.actionDefaultView
            self.LUNGS_MASK = menuAlterations.actionLungsMask
            self.SEGMENTED_LUNGS = menuAlterations.actionSegmentedLungsMask
            self.SEGMENTED_LUNGS_W_INTERNAL = menuAlterations.actionSegmentedLungsMaskWInternal

    def __selectViewModeMenuOption(self, viewModeOption, viewMode: ViewMode):
        self.selectedViewModeMenuOption.setEnabled(True)
        self.selectedViewModeMenuOption = viewModeOption
        self.selectedViewModeMenuOption.setDisabled(True)
        self.menuBar.window.changeViewMode(viewMode)

    def __defineActions(self):
        self.actionDefaultView = QtWidgets.QWidgetAction(self.menuBar)
        self.actionDefaultView.setObjectName("actionDefaultView")

        self.actionLungsMask = QtWidgets.QWidgetAction(self.menuBar)
        self.actionLungsMask.setObjectName("actionLungsMask")

        self.actionSegmentedLungsMask = QtWidgets.QWidgetAction(self.menuBar)
        self.actionSegmentedLungsMask.setObjectName("actionSegmentedLungs")

        self.actionSegmentedLungsMaskWInternal = QtWidgets.QWidgetAction(self.menuBar)
        self.actionSegmentedLungsMaskWInternal.setObjectName("actionSegmentedLungsWithInternal")

    def __connectActions(self):
        self.actionDefaultView.triggered.connect(partial(self.__selectViewModeMenuOption, self.viewModeMenuOptions.ORIGINAL,
                                                 ViewMode.ORIGINAL))

        self.actionLungsMask.triggered.connect(partial(self.__selectViewModeMenuOption, self.viewModeMenuOptions.LUNGS_MASK,
                                               ViewMode.LUNGS_MASK))

        self.actionSegmentedLungsMask.triggered.connect(
                partial(self.__selectViewModeMenuOption, self.viewModeMenuOptions.SEGMENTED_LUNGS, ViewMode.SEGMENTED_LUNGS))

        self.actionSegmentedLungsMaskWInternal.triggered.connect(
                partial(self.__selectViewModeMenuOption, self.viewModeMenuOptions.SEGMENTED_LUNGS_W_INTERNAL,
                ViewMode.SEGMENTED_LUNGS_W_INTERNAL))

    def __addActions(self):
        self.addAction(self.actionDefaultView)
        self.addAction(self.actionLungsMask)
        self.addAction(self.actionSegmentedLungsMask)
        self.addAction(self.actionSegmentedLungsMaskWInternal)

    def __retranslateUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.setTitle(_translate("MainWindow", "Alterations"))

        self.actionLungsMask.setText(_translate("MainWindow", "Lungs Mask"))
        self.actionLungsMask.setStatusTip(_translate("MainWindow", "Lungs Mask"))
        self.actionLungsMask.setShortcut(_translate("MainWindow", "-"))

        self.actionDefaultView.setText(_translate("MainWindow", "Default View"))
        self.actionDefaultView.setStatusTip(_translate("MainWindow", "DefaultView"))
        self.actionDefaultView.setShortcut(_translate("MainWindow", "+"))

        self.actionSegmentedLungsMask.setText(_translate("MainWindow", "Segmented Lungs Mask"))
        self.actionSegmentedLungsMask.setStatusTip(_translate("MainWindow", "Segmented Lungs Mask"))
        self.actionSegmentedLungsMask.setShortcut(_translate("MainWindow", "/"))

        self.actionSegmentedLungsMaskWInternal.setText(_translate("MainWindow", "Lungs Internal Structure"))
        self.actionSegmentedLungsMaskWInternal.setStatusTip(_translate("MainWindow", "Lungs Internal Structure"))
        self.actionSegmentedLungsMaskWInternal.setShortcut(_translate("MainWindow", "*"))

    def disableOptions(self):

        self.actionDefaultView.setEnabled(False)
        self.actionLungsMask.setEnabled(False)
        self.actionSegmentedLungsMask.setEnabled(False)
        self.actionSegmentedLungsMaskWInternal.setEnabled(False)

    def toggleActions(self, value: bool):

        self.actionLungsMask.setEnabled(value)
        self.actionSegmentedLungsMask.setEnabled(value)
        self.actionSegmentedLungsMaskWInternal.setEnabled(value)