from defconQt import representationFactories as baseRepresentationFactories
from simplefont import __version__, representationFactories
from simplefont.objects import settings
from simplefont.objects.application import Application
from simplefont.tools import errorReports, platformSpecific
from simplefont.windows.outputWindow import OutputWindow
from PyQt5.QtCore import (
    Qt, QCommandLineParser, QTranslator, QLocale, QLibraryInfo)
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
import qdarkstyle
import os
import sys


def main():
    global app

    # Register representation factories
    baseRepresentationFactories.registerAllFactories()
    representationFactories.registerAllFactories()

    # initialize the app
    app = Application(sys.argv)
    app.setOrganizationName("SimpleFont")
    app.setOrganizationDomain("elih.blog/simplefont")
    app.setApplicationName("SimpleFont")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(":app.png"))
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    appFont = platformSpecific.UIFontOverride()
    if appFont is not None:
        app.setFont(appFont)
    # app.setStyleSheet(platformSpecific.appStyleSheet())
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # Install stream redirection
    app.outputWindow = OutputWindow()
    # Exception handling
    sys.excepthook = errorReports.exceptionCallback

    # Qt's translation for itself. May not be installed.
    # qtTranslator = QTranslator()
    # qtTranslator.load("qt_" + QLocale.system().name(),
    #                   QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    # app.installTranslator(qtTranslator)

    # appTranslator = QTranslator()
    # appTranslator.load("simplefont_" + QLocale.system().name(),
    #                    os.path.dirname(os.path.realpath(__file__)) +
    #                    "/resources")
    # app.installTranslator(appTranslator)

    # parse options and open fonts
    parser = QCommandLineParser()
    parser.setApplicationDescription(QApplication.translate(
        "Command-line parser", "The SimpleFont font editor."))
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument(QApplication.translate(
        "Command-line parser", "files"), QApplication.translate(
        "Command-line parser", "The UFO files to open."))
    parser.process(app)
    
    # load menu
    if platformSpecific.useGlobalMenuBar():
        app.fetchMenuBar()
        app.setQuitOnLastWindowClosed(False)

    # bootstrap extensions

    # process files
    args = parser.positionalArguments()
    if not args:
        # maybe load recent file
        loadRecentFile = settings.loadRecentFile()
        if loadRecentFile:
            recentFiles = settings.recentFiles()
            if len(recentFiles) and os.path.exists(recentFiles[0]):
                app.openFile(recentFiles[0])
    else:
        for fontPath in args:
            app.openFile(fontPath)
    # if we did not open a font, spawn new font or go headless
    if not app.allFonts():
        if platformSpecific.shouldSpawnDocument():
            app.newFile()
        else:
            # HACK: on OSX we may want to trigger native QMenuBar display
            # without opening any window. Since Qt infers new menu bar on
            # focus change, fire the signal.
            app.focusWindowChanged.emit(None)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
