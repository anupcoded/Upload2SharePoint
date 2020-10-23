import os
import requests
import sys
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
from requests_ntlm import HttpNtlmAuth


proxies = {
  #'http': '',
  #'https': '',
}

#release =  ["5.19"]
release = sys.argv[1].split(",")
url = sys.argv[2]
#Enter your SharePoint site and target library
sharePointUrl = sys.argv[3]
mainFolderUrl = sys.argv[4]
subFolder = sys.argv[5].split(",")
#Enter your SharePoint username and password
username = sys.argv[6]
password = sys.argv[7]

#authentication
auth = HttpNtlmAuth(username,password)

#Setup the required headers for communicating with SharePoint 
headers = {'Content-Type': 'application/json; odata=verbose', 'accept': 'application/json;odata=verbose'}

#Execute a request to get the FormDigestValue. This will be used to authenticate our upload request
r = requests.post(sharePointUrl + "/_api/contextinfo",proxies=proxies,auth=auth,headers=headers)
print(r.text)
formDigestValue = r.json()['d']['GetContextWebInformation']['FormDigestValue']
#Update headers to use the newly acquired FormDigestValue
headers = {'Content-Type': 'application/json; odata=verbose', 'accept': 'application/json;odata=verbose', 'x-requestdigest' : formDigestValue}

#Sets up the url for requesting a file upload
#requestUrl = sharePointUrl + '/_api/web/getfolderbyserverrelativeurl(\'' + folderUrl + '\')/Files/add(url=\'' + 'test.zip' + '\',overwrite=true)'
#p = requests.post(sharePointUrl+"/_api/web/folders",proxies=proxies,auth=auth, headers=headers, 
#json={
#    "__metadata": { "type": "SP.Folder" },
#    "ServerRelativeUrl": folderUrl + '/Patches' 
#    })

def get_url_paths(url, ext='', params={}):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent

for x in release:
    fullUrl = url + x + '/'
    print('FTP Url: ' + fullUrl)
    ext = 'zip'
    result = get_url_paths(fullUrl, ext)
    folderName = fullUrl.split("/")[-2]
    print('Patch release Version: ' + folderName)
    subFolderUrl = [s for s in subFolder if folderName in s]
    folderUrl = mainFolderUrl + '/' + subFolderUrl[0]
    print('Adding to Folder' + folderUrl)

    for a in result:
        fileName = (os.path.basename(urlparse(a).path))
        #Sets up the url for requesting a file upload
        requestUrl = sharePointUrl + '/_api/web/getfolderbyserverrelativeurl(\'' + folderUrl + '\')/Files/add(url=\'' + fileName + '\',overwrite=false)'
        response = urlopen(a)
        zipcontent= response.read()
        uploadResult = requests.post(requestUrl,proxies=proxies,auth=auth, headers=headers,data=zipcontent)
        print('Patch ' + fileName )


        