from evtx import PyEvtxParser
import json
import magic  # Be sure to run `brew install libmagic` first
from pathlib import Path
import argparse
import shutil
from datetime import datetime
from pathvalidate import sanitize_filename

homeDir = Path.home()
invDir = str(homeDir) + "/investigations"
archiveDir = invDir + "/evtx-archives"


def main():
    argsParser = argparse.ArgumentParser(prog="evtx-tool")
    argsParser.add_argument(
        "-v",
        "--verbose",
        help="Display actions being taken verbosely",
        action="store_true",
    )

    subParser = argsParser.add_subparsers()

    # Rename command
    renameParser = subParser.add_parser(
        "rename", help='Renames evtx files to be "HOSTNAME-LOGTYPE.evtx"'
    )
    renameMutex = renameParser.add_mutually_exclusive_group()
    renameMutex.add_argument("-f", "--file", help="Specify a single file to act on.")
    renameMutex.add_argument("-d", "--directory", help="Specify a directory to act on.")
    renameParser.set_defaults(func="rename")

    # List command
    listParser = subParser.add_parser(
        "list", help="List all evtx files in a given directory."
    )
    listParser.add_argument("-d", "--directory", help="Specify a directory to act on.")
    listParser.set_defaults(func="list")

    # Archive command
    archiveParser = subParser.add_parser(
        "archive",
        help="Archives all evtx files in a given directory to an output directory.",
    )
    archiveParser.add_argument(
        "-d", "--directory", help="Specify a directory to act on."
    )
    archiveParser.add_argument(
        "-o", "--output", help="Specify an output directory", default=archiveDir
    )
    archiveParser.add_argument("-v", "--verbose", action="store_true")
    archiveParser.set_defaults(func="archive")

    args = argsParser.parse_args()

    try:
        match args.func:
            case "rename":
                if args.file:
                    RenameEvtxLog(args.file, verbose=args.verbose)
                elif args.directory:
                    RenameEvtxLog(args.directory, verbose=args.verbose)
            case "list":
                FindEventLogs(args.directory, verbose=args.verbose)
            case "archive":
                ArchiveEvtxLogs(args.directory, args.output, verbose=args.verbose)
    except Exception as exc:
        print(exc)
        argsParser.print_help()


def ReadEventLog(eventLogPath):

    eventLogList = []
    fullPath = Path(eventLogPath).resolve()  # Use pathlib to get the absolute path
    parser = PyEvtxParser(str(eventLogPath))
    for item in parser.records_json():
        jsonItem = json.loads(item["data"])
        eventLogList.append(jsonItem)
    logName = sanitize_filename(
        eventLogList[-1]["Event"]["System"]["Channel"]
    )  # Get the event log type
    computerName = eventLogList[-1]["Event"]["System"][
        "Computer"
    ]  # Take the most recent log event and grab the hostname
    return (
        computerName.split(".")[0],
        logName,
        fullPath,
    )  # Returns the computer name without domain, log name (e.g., "Windows PowerShell", "Security", "Application", etc.) and the absolute path.


def FindEventLogs(searchPath, verbose=False):
    evtxFiles = []
    pathObj = Path(searchPath)
    for file in pathObj.iterdir():
        if file.is_file():
            fileMagic = magic.from_file(file.absolute())
            if "Event Log" in fileMagic:
                evtxFiles.append(file)
                if verbose:
                    print("Found evtx file: ", file)
    return evtxFiles


def ArchiveEvtxLogs(inputDirectory, outputDirectory, verbose=True):
    timestamp = datetime.now()
    formatted_date = timestamp.strftime("%Y-%m-%dT%H_%M_%S")
    outputDirectory = Path(outputDirectory)
    outputFile = outputDirectory.joinpath(formatted_date)
    if not outputDirectory.is_dir():
        outputDirectory.mkdir(parents=True, exist_ok=True)
        if verbose:
            print("Creating ", outputDirectory)
    tempDirectory = Path.joinpath(outputDirectory, "temp")
    if not tempDirectory.is_dir():
        tempDirectory.mkdir(parents=True, exist_ok=True)
        if verbose:
            print("Creating ", tempDirectory)
    # First get a list of the files to cleanup
    evtxFiles = FindEventLogs(inputDirectory)
    # Move them to a temp archive directory
    for file in evtxFiles:
        renamedFile = RenameEvtxLog(
            file
        )  # Rename the files, returns a path-like object
        if verbose:
            print("Moving %s to %s" % (renamedFile, tempDirectory))
        shutil.move(renamedFile, tempDirectory)
    print("Creating archive at " + str(outputFile) + ".tar.xz")
    shutil.make_archive(
        outputFile, format="xztar", root_dir=outputDirectory, base_dir=tempDirectory
    )
    shutil.rmtree(tempDirectory)


def RenameEvtxLog(fileName, verbose=False):
    evtxInfo = ReadEventLog(fileName)
    evtxParentDir = evtxInfo[2].parent
    newName = str(evtxParentDir) + "/" + evtxInfo[0] + "-" + evtxInfo[1] + ".evtx"
    if verbose:
        print("Renaming %s to %s" % (fileName, newName))
    evtxInfo[2].rename(newName)
    return newName


if __name__ == "__main__":
    main()
