#!/bin/python

import re,sys,os,requests

WANTED=[
    'build-log.txt',
    'artifacts/e2e.*/gather-must-gather/artifacts/must-gather.tar',
    'artifacts/e2e.*/baremetalds-devscripts-gather/artifacts/sosreport-ipi-ci-op-.*.tar.xz',
    'artifacts/e2e.*/gather-extra/artifacts/nodes/.*/journal',
    'artifacts/e2e.*/baremetalds-e2e-test/build-log.txt',
    'artifacts/e2e.*/baremetalds-e2e-test/artifacts/junit/junit_e2e_.*.xml',
]
_WANTED={}
def parseWanted():
    for w in WANTED:
        position=_WANTED
        parts = w.split('/')
        for part in parts:
            if part == parts[-1]:
                position[part] = None
            else:
                position = position.setdefault(part, {})

def getFile(url, path):
    if os.path.exists(path):
        return
    r = requests.get(url)
    if r.headers.get('content-type') == 'application/gzip':
        path = path+".gz"
    fp = open(path, 'wb')
    fp.write(r.content)
    fp.close()

re_href = re.compile('href="([^"]*)"')
def getEntries(basedir, url, wanted):
    page = requests.get(url).text
    hrefs = re_href.findall(page)

    for href in hrefs:
        hreftype='f'
        if href[-1] == '/':
            hreftype='d'
            href = href[:-1]
        href = href.split('/')[-1]
        for w in wanted.keys():
            if re.match(w+"$", href):
                if hreftype == 'f':
                    if not wanted[w]:
                        print("Getting file", os.path.join(url,href).replace(sys.argv[1], ""))
                        href = os.path.join(url,href)
                        getFile(href, basedir + "/" + ("_".join(href.split("/")[-2:])))
                else:
                    getEntries(basedir, os.path.join(url, href), wanted[w])

def run(args):
    basedir=args[1].strip('/').split('/')[-1]
    os.makedirs(basedir, exist_ok=True)
    parseWanted()
    getEntries(basedir, args[1], _WANTED)

if __name__ == '__main__':
    run(sys.argv)
