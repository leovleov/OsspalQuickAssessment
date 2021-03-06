# coding=utf-8
# query openhub and github
import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET

import urllib, urlparse, string, time
import urllib2, base64, json
from urlparse import urlparse

# Import modules
from xml.dom import minidom

def queryGithub(searchTerm):
    username = 'osspal'
    password = 'Practicum2017Osspal@CMU'
    maturity_score = 0

    #searchTerm = raw_input('Search GitHub repo: ')
    qs = {'q': searchTerm}
    qsEncoded = urllib.urlencode(qs)
    queryURL = "https://api.github.com/search/repositories?o=desc&sort=stars&" + qsEncoded

    # e.g. 'https://api.github.com/search/repositories?q=electron'
    searchReq = urllib2.Request(queryURL)
    base64string = base64.b64encode('%s:%s' % (username, password))
    searchReq.add_header("Authorization", "Basic %s" % base64string)
    searchRes = urllib2.urlopen(searchReq)
    jsonSearch = json.loads(searchRes.read())

    githubURL =  'http://github.com/' + jsonSearch['items'][0]['full_name']

    print 'Top result: ', githubURL

    parsedURL = urlparse(githubURL)
    owner = parsedURL.path.split('/')[1]
    repoName = parsedURL.path.split('/')[2]

    # e.g. 'https://github.com/electron/electron'
    basicReq = urllib2.Request("https://api.github.com/repos/" + owner + "/" + repoName)
    base64string = base64.b64encode('%s:%s' % (username, password))
    basicReq.add_header("Authorization", "Basic %s" % base64string)
    basicRes = urllib2.urlopen(basicReq)
    

    map={}
    map["github_url"] = githubURL
    map["query_github_success"] = "succeeded"
    # e.g. 'https://api.github.com/repos/electron/electron/releases/latest '
    latestJson = ''
    try:
        latestReq = urllib2.Request("https://api.github.com/repos/" + owner + "/" + repoName + "/releases/latest")
        latestReq.add_header("Authorization", "Basic %s" % base64string)
        latestRes = urllib2.urlopen(latestReq)
        latestJson = latestRes.read();
    except urllib2.HTTPError as err:
        if err.code == 404:
            #print 'Unable to retrive latest release info.'
            latestJson = '{"published_at":"NA"}'
            #map["query_github_success"] = "failed"

    # e.g. 'https://api.github.com/repos/$owner/$repoName/license'
    licenseJson = ''
    try:
        licenseReq = urllib2.Request("https://api.github.com/repos/" + owner + "/" + repoName + "/license")
        licenseReq.add_header("Authorization", "Basic %s" % base64string)
        licenseRes = urllib2.urlopen(licenseReq)
        licenseJson = licenseRes.read()
    except urllib2.HTTPError as err:
        if err.code == 404:
            #print 'Unable to retrive license info.'
            licenseJson = '{"license":{"name":"NA"}}'
            #map["query_github_success"] = "failed"

    # parsed json responses
    jsonBasic = json.loads(basicRes.read())
    jsonLatest = json.loads(latestJson)
    jsonLicense = json.loads(licenseJson)

    # print '# of stars: ', jsonBasic['watchers_count']
    # print '# of forks: ', jsonBasic['forks_count']
    # print 'latest release publish date: ', jsonLatest['published_at']
    # print 'Licesne: ', jsonLicense['license']['name']
    # print 'Open Issues Count: ', jsonBasic['open_issues_count']
    # print 'Subscribers Count: ', jsonBasic['subscribers_count']
     

    number_of_stars = jsonBasic['watchers_count']
    number_of_forks = jsonBasic['forks_count']
    open_issues_count = jsonBasic['open_issues_count']
    subscribers_count = jsonBasic['subscribers_count']

    map["number_of_stars"] = number_of_stars
    if number_of_stars >= 100:
        map["number_of_stars_filter"] = "√"
    else:
        map["number_of_stars_filter"] = "×"

    map["number_of_forks"] = number_of_forks
    map["total_score_stars"] = 10
    map["total_score_forks"] = 10;
    score_stars = 0;
    score_forks = 0;
    if number_of_forks >= 100:
        map["number_of_forks_filter"] = "√"
    else:
        map["number_of_forks_filter"] = "×"
    if number_of_stars >= 100 and number_of_forks >= 100:
        score_stars = 10
        score_forks = 10
    else:        
        if number_of_stars >= 100:
            score_stars = 10        
        elif number_of_stars != None:
            score_stars = number_of_stars/10
        if number_of_forks >= 100:
            score_forks = 10
        elif number_of_forks != None:
            score_forks = number_of_forks/10
    maturity_score = maturity_score + score_stars + score_forks
    map["score_stars"] = score_stars
    map["score_forks"] = score_forks
          

    map["latest_release_publish_date"] = jsonLatest['published_at']

    map["license"] = jsonLicense['license']['name']

    map["open_issues_count"] = open_issues_count
    map["total_score_open_issues"] = 20
    score_open_issues = 0
    if open_issues_count >= 50:
        map["open_issues_count_filter"] = "√"
        score_open_issues = 20
    else:
        map["open_issues_count_filter"] = "×"
        if open_issues_count != None:
            score_open_issues = open_issues_count*2/5
    maturity_score = maturity_score + score_open_issues
    map["score_open_issues"] = score_open_issues

    map["subscribers_count"] = subscribers_count
    if subscribers_count >= 50:
        map["subscribers_count_filter"] = "√"
    else:
        map["subscribers_count_filter"] = "×"

    map["project_maturity_score"] = maturity_score
    #print json.dumps({"result":map})
    #return json.dumps({"result": map})
    return map


def queryOpenHub(queryTerm):
    def query_man_month():
        man_month, codeDiff = 0, 0
        size_facts_query_url = "https://www.openhub.net/projects/" + str(project_id) + "/analyses/latest/size_facts" + ".xml?api_key=" + api_key
        print size_facts_query_url
        dom = minidom.parse(urllib2.urlopen(size_facts_query_url)) # parse the data

        sizeFact = dom.getElementsByTagName('size_fact')
        manMonthList = sizeFact[-1].getElementsByTagName('man_months')
        m = manMonthList[-1]
        total = m.childNodes[0].nodeValue
        man_month = int(total)

        if not sizeFact[-1].getElementsByTagName('code'):
            codeDiff = 0
        else:
            codeCurr, codePrev = 0, 0
            monthDiff = 6 # the latest 6 month
            for ind in range(1, monthDiff + 1): # 1, 7
                node = sizeFact[-ind]
                codeLineList = node.getElementsByTagName('code')
                codeCurr = codeLineList[-1].childNodes[0].nodeValue
                if ind != 1:
                    codeDiff += abs( int(codeCurr) - int(codePrev) )
                codePrev = codeCurr
        return man_month, codeDiff
        
    map={}
    map["query_term"] = queryTerm
    api_key = "85690631252ec7681f0e7ac7f46725c4fcc8b56cd2f6c38cb4a7cf7961512f98"
    #query_term = "electron"
    maturity_score = 0
    value_score = 0;
    page_num = "1"
    url = "https://www.openhub.net/projects.xml?api_key=" + api_key + "&query=" + queryTerm + "&page=" + page_num
    resp = requests.get(url,verify=False)
    print url
    soup = BeautifulSoup(resp.content, "html.parser")
    # we use beautiful soup to get the #1 rank project id & url on Openhub
    try:
        map["query_openhub_success"] = "succeeded"
        project_id = soup.find('id').get_text()
    except:
        # query openhub failed, quit
        map["query_openhub_success"] = "failed"
        project_id = None
    print project_id
    try:
        project_html_url = soup.find('html_url').get_text()
    except:
        project_html_url = ''
    print project_html_url

    if map["query_openhub_success"] == "succeeded":
        project_query_url = "https://www.openhub.net/projects/" + str(project_id) + ".xml?api_key=" + api_key
        print project_query_url
        openhub_resp_content = requests.get(project_query_url,verify=False).content

        # handle exception

        openhub_soup = BeautifulSoup(openhub_resp_content, "html.parser")
    try:
        project_twelve_month_contributor_count = int(openhub_soup.find('twelve_month_contributor_count').get_text())
    except:
        project_twelve_month_contributor_count = None
    try:
        project_total_contributor_count = int(openhub_soup.find('total_contributor_count').get_text())
    except:
        project_total_contributor_count = None

    try:
        project_twelve_month_commit_count = int(openhub_soup.find('twelve_month_commit_count').get_text())
    except:
        project_twelve_month_commit_count = None

    try:
        project_total_commit_count = int(openhub_soup.find('total_commit_count').get_text())
    except:
        project_total_commit_count = None
    try:
        project_total_code_lines = int(openhub_soup.find('total_code_lines').get_text())
    except:
        project_total_code_lines = None
    try:
        project_main_language_name = openhub_soup.find('main_language_name').get_text()
    except:
        project_main_language_name = None
    try:
        project_license = openhub_soup.find('license').find('name').get_text()
    except:
        project_license = None
    try:
        project_project_activity_index_description = openhub_soup.find('project_activity_index').find('description').get_text()
    except:
        project_project_activity_index_description = None
    try:
        project_user_count = int(openhub_soup.find('user_count').get_text())
    except:
        project_user_count = None

    map["project_html_url"] = project_html_url
    map["project_twelve_month_contributor_count"] = project_twelve_month_contributor_count
    map["total_score_twelve_month_contributor"] = 20
    score_twelve_month_contributor = 0
    if project_twelve_month_contributor_count >= 2:
        map["project_twelve_month_contributor_count_filter"] = "√"
        score_twelve_month_contributor = 20
    else:
        map["project_twelve_month_contributor_count_filter"] = "×"
        if project_twelve_month_contributor_count != None:
            score_twelve_month_contributor = project_twelve_month_contributor_count * 10
    maturity_score = maturity_score + score_twelve_month_contributor
    map["score_twelve_month_contributor"] = score_twelve_month_contributor

    map["project_total_contributor_count"] = project_total_contributor_count
    map["total_score_total_contributor"] = 20
    score_total_contributor = 0
    if project_total_contributor_count >= 5:
        map["project_total_contributor_count_filter"] = "√"
        score_total_contributor = 20        
    else:
        map["project_total_contributor_count_filter"] = "×"
        if project_total_contributor_count != None:
            score_total_contributor = project_total_contributor_count*4
    maturity_score = maturity_score + score_total_contributor
    map["score_total_contributor"] = score_total_contributor;

    map["project_twelve_month_commit_count"] = project_twelve_month_commit_count
    if project_twelve_month_commit_count >= 50:
        map["project_twelve_month_commit_count_filter"] = "√"
    else:
        map["project_twelve_month_commit_count_filter"] = "×"

    map["project_total_commit_count"] = project_total_commit_count
    if project_total_commit_count >= 1000:
        map["project_total_commit_count_filter"] = "√"
    else:
        map["project_total_commit_count_filter"] = "×"

    map["project_total_code_lines"] = project_total_code_lines
    map["project_main_language_name"] = project_main_language_name
    map["project_license"] = project_license
    map["project_project_activity_index_description"] = project_project_activity_index_description
    map["project_user_count"] = project_user_count
     
    map["total_score_user_count"] = 50
    score_user_count = 0
    if project_user_count >= 50:
        score_user_count = 50
    else:
        map["project_user_count_filter"] = "×"
        if project_user_count != None:
            score_user_count = project_user_count
    map["score_user_count"] = score_user_count
    value_score = value_score + score_user_count
    
    try:
        project_man_month, project_code_diff = query_man_month()
    except:
        project_man_month, project_code_diff = None, None
    
    map["total_score_man_month"] = 50
    score_man_month = 0
    if project_man_month >= 500:
        map["project_man_month_filter"] = "√"
        score_man_month = 50
    else:
        map["project_man_month_filter"] = "×"
        if project_man_month != None:
            score_man_month = project_man_month/10
    value_score = value_score + score_man_month
    map["score_man_month"] = score_man_month
    
    map["total_score_code_diff"] = 20
    score_code_diff = 0
    if project_code_diff >= 10000 or (project_total_code_lines != None and project_code_diff/float(project_total_code_lines) >= 0.05):
        map["project_code_diff_filter"] = "√"
        score_code_diff = 20
    else:
        map["project_code_diff_filter"] = "×"
        if project_code_diff != None:
            #score_code_diff = project_code_diff/500
            score_code_diff = max(project_code_diff/500, int(project_code_diff/float(project_total_code_lines)*20*20+0.5))
    map["score_code_diff"] = score_code_diff
    maturity_score = maturity_score + score_code_diff

    map["project_man_month"] = project_man_month # test
    map["project_code_diff"] = project_code_diff # test
    map["project_maturity_score"] = maturity_score
    map["project_value_score"] = value_score
    map["total_value_score"] = 100

    print json.dumps({"result": map})




    #return json.dumps({"result": map})
    return map

    # print project_total_contributor_count
    # print project_twelve_month_commit_count
    # print project_total_commit_count
    # print project_total_code_lines
    # print project_main_language_name
    # print project_license
    # print project_project_activity_index_description

def calculateScores(map_github, map_openhub):
    maturity_score = 0;
    if map_openhub["query_openhub_success"] == "succeeded" and map_github["query_github_success"] == "succeeded":
        total_maturity_score = 100;
        maturity_score = maturity_score + map_openhub["project_maturity_score"];
        maturity_score = maturity_score + map_github["project_maturity_score"];
        query_result = "succeeded";
        license = map_openhub["project_license"];    
    elif map_openhub["query_openhub_success"] == "succeeded":
        total_maturity_score = 60;
        maturity_score = maturity_score + map_openhub["project_maturity_score"];
        query_result = "partially succeeded";
        license = map_openhub["project_license"];
    elif map_github["query_github_success"] == "succeeded":
        total_maturity_score = 40;
        maturity_score = maturity_score + map_github["project_maturity_score"];
        query_result = "partially succeeded";
        license = map_github["license"];
    else:
        query_result = "Failed";
    map = {}
    map["total_maturity_score"] = total_maturity_score;
    map["maturity_score"] = maturity_score;
    map["query_result"] = query_result;
    map["license"] = license;
    return map;

if __name__ == "__main__":
    searchTerm = raw_input('Search GitHub repo: ')
    queryOpenHub(searchTerm)
    #queryGithub(searchTerm)
