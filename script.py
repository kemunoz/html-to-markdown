#!/usr/bin/python
import html2text
from bs4 import BeautifulSoup
import os
from os import remove
from os import listdir
from os.path import isfile, join, isdir, relpath
import shutil
import time
import queue


# TODO:
# - [x]Read in whole file
# - [x]Convert whole file to markdown
# - [x]Write to a new file
# - [x]read in line by line until ##
# - [x]copy the rest of file into new samename markdown file
# - [x] fix document links
# - [] create a directory with the filename
# - [] store images used in the directory
# - [] keep relative path for links

# helper function that checks if a link is valid
images = {}
rootpath = "~/"
q = queue.Queue()
mypath = os.getcwd()
filedict = {
    "AP-OVERVIEW.htm": "AP-OVERVIEW",
    "AP-OVERVIEW.htm": "AP-OVERVIEW",
    "AR-OVERVIEW.htm": "AR-OVERVIEW",
    "DOC-OVERVIEW.htm": "DOC-OVERVIEW",
    "ENG-OVERVIEW.htm": "ENG-OVERVIEW",
    "EXEC-OVERVIEW.htm": "EXEC-OVERVIEW",
    "FS-OVERVIEW.htm": "FS-OVERVIEW",
    "GL-OVERVIEW.htm": "GL-OVERVIEW",
    "INV-OVERVIEW.htm": "INV-OVERVIEW",
    "MFG-OVERVIEW.htm": "MFG-OVERVIEW",
    "MRK-OVERVIEW.htm": "MRK-OVERVIEW",
    "PRO-OVERVIEW.htm": "PRO-OVERVIEW",
    "PUR-OVERVIEW.htm": "PUR-OVERVIEW",
    "ACE-OVERVIEW.htm": "ACE-OVERVIEW"
}
linkset = {}
for key in filedict:
    filedict[key] = join(mypath, filedict[key])

visited = set()


def valid_link(link):
    return isfile(link)

# helper funciton that decomposes prev and next links


def sanitize_links(soup):
    for item in soup.find_all('a'):
        title = item.string
        if title == "Previous" or title == "Next":
            item.decompose()

# Helper function that gets specified link from soup and decomposes if link is not valid


def move_images(images, path):
    if(len(images) > 0):
        for image in images:
            shutil.move(image, path)


def get_images(soup, path, foldername):
    images = []
    for image in soup.find_all('img'):
        imagepath = image.get('src')
        if valid_link(imagepath):
            imagename = imagepath[7:len(imagepath)]
            image['src'] = "./" + imagename
            images.append(imagepath)
    return images


def get_master_parent(path):
    tokens = path.split("\\")
    found = False
    for folder in tokens:
        if found:
            return folder
    return ""


def get_links(parentfolder, soup):
    links = []
    if 'AP-E' in parentfolder:
        debug = 1
    for atag in soup.find_all('a'):
        href = atag['href']
        childfolder = href.split(".")[0]
        if href in visited:
            storedpath = filedict[href]
            relative = relpath(storedpath, join(
                filedict[parentfolder], childfolder))
            atag['href'] = relative
        elif valid_link(href):
            currpath = join(filedict[parentfolder], childfolder)
            filedict[href] = currpath
            atag['href'] = get_prepend_diff(
                currpath, parentfolder) + "\\README.md"
            links.append(href)
        else:
            atag.decompose
    return links


def get_prepend_diff(currpath, parentfolder):
    tokens = currpath.split('\\')
    parent = parentfolder.split('.')[0]
    toconcat = False
    path = []
    for str in tokens:
        if toconcat:
            path.append(str)
        if str == parent:
            toconcat = True

    return '\\'.join(path)
# Helper function to create directory


def create_dir(path):
    if not isdir(path):
        os.mkdir(path)

# Helper funciton to create README file


def create_base_readme(path):
    filename = join(path, "README.md")
    if not isfile(filename):
        f = open(filename, "x")
        f.close()
        return 1
    return 0

# Format the version badge


def version(path):
    f = open(join(path, "README.md"), 'r+')
    string = f.readline()
    content = ""
    while string != '':
        tempstring = string[0: 7]
        if 'Version' == tempstring:
            break
        elif 'Copyright' in string:
            break
        content += string
        string = f.readline()
    while 'Version' not in string and string != '':
        string = f.readline()
        string = string.strip()
    tokenizedstring = string.split(' ')
    string = tokenizedstring[0] + ' ' + tokenizedstring[1]
    content += '<badge text= "' + string + '" vertical="middle" ' + '/>'
    return content


def sanitize_html(path):
    f = open(path)
    line = f.readline()
    content = ""
    while not "<H2" in line:
        line = f.readline()
    while line != "":
        content += line
        line = f.readline()
    f.close()
    return content

# helper fucntion that writes content to a readme file


def write_to_readme(content, path):
    f = open(join(path, "README.md"), 'w')
    h = html2text.HTML2Text()
    h.ignore_tables = True
    h.wrap_links = False
    f.write(h.handle(content))
    f.close()
    content = version(path)
    os.remove(join(path, "README.md"))
    f = open(join(path, "README.md"), 'x')
    f.write(content)


def visit(file):
    # Path is the path to the file directory
    # example for AP-Overview it will be C://Users/kevinm/desktop/M3Doc/AP-Overview
    path = join(mypath, file)
    content = sanitize_html(path)
    # Create soup object from sanitized html
    soup = BeautifulSoup(content, 'html.parser')
    # Get validated links and images

    sanitize_links(soup)
    imagelinks = get_images(soup, path.split('.')[0], file.split('.')[0])
    links = get_links(file, soup)
    if not file in filedict:
        path = path[0:len(path) - 4]
    else:
        path = filedict[file]
    create_dir(path)
    move_images(imagelinks, path)
    create_base_readme(path)
    write_to_readme(soup.prettify(), path)
    return links


onlyfiles = ["AP-OVERVIEW.htm", "AR-OVERVIEW.htm", "DOC-OVERVIEW.htm", "ENG-OVERVIEW.htm", "EXEC-OVERVIEW.htm", "FS-OVERVIEW.htm",
             "GL-OVERVIEW.htm", "INV-OVERVIEW.htm", "MFG-OVERVIEW.htm", "MRK-OVERVIEW.htm", "PRO-OVERVIEW.htm", "PUR-OVERVIEW.htm", "ACE-OVERVIEW.htm"]


for file in onlyfiles:
    if file != "script.py":
        q.put(file)
        while not q.empty():
            node = q.get()
            if not node in visited:
                childNodes = visit(node)
                visited.add(node)
                for child in childNodes:
                    q.put(child)
