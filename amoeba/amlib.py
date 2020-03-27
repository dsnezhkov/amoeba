import os
import re
import xml
from urllib.parse import urlparse
from collections import OrderedDict

import requests
import xmltodict
from edgar import Edgar, Company
from lxml import etree
import html2text


class Amoeba:
    def __init__(self, config, logger):
        self.alogger = logger
        self.aconfig = config

    def find_company_by_names_fuzzy(self, names):
        """
        Requests EDGAR for a company by name pattern to obtain a list of potentials
        :param names: A pattern for a name
        :return: None. Prints list of possible matches
        """
        if len(names) != 0:
            edgar = Edgar()
            for n in names:
                if not "".__eq__(n):
                    possible_companies = edgar.find_company_name(n)
                    for pc in possible_companies:
                        cik = edgar.get_cik_by_company_name(pc)
                        # Provide more details to help choose the right one
                        if self.aconfig['args'].edgar_company_names_fuzzy_detail:

                            print("\nName/CIK: {0}:{1}".format(pc, cik))
                            cik_feed = self.aconfig['args'].endpoint + \
                                       "/cgi-bin/browse-edgar?action=getcompany&CIK=" + \
                                       cik + "&output=atom"
                            try:
                                response = requests.get(cik_feed)
                                od = xmltodict.parse(response.content)
                                state_inc = od['feed']['company-info']['state-of-incorporation']
                                state_loc = od['feed']['company-info']['state-location']
                                print("{0:>10} : {1}/{2}".format("State Incorporated/State Located", state_inc, state_loc))

                                print("{0:>5}".format("Addresses:"))
                                for k, addresses in od['feed']['company-info']['addresses'].items():
                                    for addr in addresses:
                                        print()
                                        for k, v in addr.items():
                                            print("{0:>10} {1}".format(k,v))

                            except requests.ConnectionError as ce:
                                print("Error fetching atom feed: ", ce)
                            except xml.parsers.expat.ExpatError as xe:
                                print("Error fetching atom feed: ", xe)
                            print("---")
                        else:
                            print("{0}:{1}".format(pc, cik))

                else:
                    print("Skipping empty name")
        else:
            print("No names provided (-N option)")

    def find_company_by_name(self, name):
        """
        Requests EDGAR for a company by name and obtains it's CIK number
        :param name: Company name
        :return: None.
        """
        if not "".__eq__(name):
            edgar = Edgar()

            try:
                company_cik = edgar.get_cik_by_company_name(name=name.upper())
                print("{0}:{1}".format(name.upper(), company_cik))
            except Exception as e:
                print("Error: ", e)
        else:
            print("No name provided (-n|-N options)")

    def search_string(self, string_to_search, before, after, pattern_to_search_for):
        """
        Highlight the pattern and provide contextual awareness of it in the output
        :param string_to_search: What are we searching
        :param before: number of lines before the line identified with pattern
        :param after: number of lines after the line identified with pattern
        :param pattern_to_search_for: Pattern we are searching for
        :return: None
        """
        all_lines = string_to_search.splitlines()
        last_line_number = len(all_lines)
        for current_line_no, current_line in enumerate(all_lines):
            if pattern_to_search_for in current_line:
                start_line_no = max(current_line_no - before, 0)
                end_line_no = min(last_line_number, current_line_no + after + 1)
                print("\t>>> {0}\n".format(current_line))
                print("\n-- Context -- ")
                for i in range(start_line_no, current_line_no): print(all_lines[i])
                for i in range(current_line_no, end_line_no): print(all_lines[i])
                print("----\n")
                break

    def search_company_filings_by_cik(self, cik, filing_type, filing_subtype, no_of_entries, filing_date_before,
                                      filing_pattern, filing_rsrc_cache):
        # TODO: build dynamic from file
        filing_types = ["425", "8-K", "10-K", "10-Q"]
        filing_subtypes = ["EX-1", "EX-2", "EX-3", "EX-4", "EX-5", "EX-6", "EX-7", "EX-8", "EX-9", "EX-10", "EX-11",
                           "EX-12", "EX-13", "EX-14", "EX-15", "EX-16", "EX-17", "EX-18", "EX-19", "EX-20", "EX-21",
                           "EX-22", "EX-23", "EX-24", "EX-25", "EX-25", "AEX-26", "EX-28", "EX-29", "EX-31", "EX-32",
                           "EX-33", "EX-34", "EX-35", "EX-99"]

        if filing_type in filing_types:
            if filing_subtype in filing_subtypes or \
                    re.match(r'EX-\d\d\.*', filing_subtype, re.IGNORECASE) or \
                    filing_subtype in filing_types :

                edgar = Edgar()
                self.alogger.debug("Getting company registration from endpoint")
                company_name = edgar.get_company_name_by_cik(cik=cik)
                self.search_company(company_name, cik,
                                    filing_type, filing_subtype,
                                    no_of_entries, filing_date_before, filing_pattern, filing_rsrc_cache)
            else:
                print("{} not a recognized filing subtype.".format(filing_subtype))
                print("Supported filing subtypes:")
                for filing_subtype in filing_subtypes:
                    print(filing_subtype)
        else:
            print("{} not a recognized filing type.".format(filing_type))
            print("Supported filing types:")
            for filing_type in filing_types:
                print(filing_type)

    def search_company(self, name, cik,
                       filing_type, filing_subtype, no_of_entries, filing_date_before, filing_pattern,
                       filing_rsrc_cache):
        base_url = self.aconfig['args'].endpoint
        acquirePatterns = OrderedDict()

        if len(filing_pattern) == 0 and not filing_rsrc_cache:
            print("Ambiguous options: no pattern search: (-P [-P] , and no download of resources: -d. Choose one mode")
            return

        for pattern in filing_pattern:
            acquirePatterns[pattern] = re.compile(pattern)

        self.alogger.debug("Name:{0} CIK:{1} Filing:{2} Subtype:{3}".format(name, cik, filing_type, filing_subtype))
        company = Company(name, cik)

        print("Filings endpoint:", company.get_filings_url())
        tree = company.get_all_filings(filing_type=filing_type,
                                       no_of_entries=no_of_entries, prior_to=filing_date_before)

        url_groups = company._group_document_type(tree, filing_type)
        result = OrderedDict()
        for url_group in url_groups:
            for url in url_group:
                url = base_url + url
                self.alogger.debug("In Content page: {0} ".format(url))
                content_page = Company.get_request(url)
                try:
                    table = content_page.find_class("tableFile")[0]
                    for row in table.getchildren():

                        # Match on 4th column of the row `Type`
                        if filing_subtype in row.getchildren()[3].text:
                            self.alogger.debug("Subtype found: {0}".format(row.getchildren()[3].text))
                            href = row.getchildren()[2].getchildren()[0].attrib["href"]
                            href_txt = row.getchildren()[2].getchildren()[0].text_content()

                            if href and not href_txt:
                                self.alogger.debug(" but no link for the resource posted. skipping")
                                continue

                            # SEC XRBL. Remove that cruft, get raw document if applicable
                            href = href.replace("/ix?doc=", "")
                            href = base_url + href

                            self.alogger.debug("Processing resource: {0}".format(href))
                            # Fetch the filing doc and process
                            if filing_rsrc_cache:
                                rsrc_cache_path = urlparse(href).path.strip("/")
                                rsrc_cache_dir = os.path.dirname(rsrc_cache_path)
                                r = requests.get(href)
                                self.alogger.debug("Making repository structure")
                                os.makedirs(rsrc_cache_dir, exist_ok=True)
                                print("Storing {} from {} locally: {}".format(href_txt, href, rsrc_cache_path))
                                with open(rsrc_cache_path, 'wb') as f:
                                    f.write(r.content)
                            else:
                                print("Working on {} ...".format(href))
                                doc = Company.get_request(href)
                                tree_str = str(etree.tostring(doc), 'utf-8')
                                tree_str_text = html2text.html2text(tree_str)
                                result[href] = tree_str_text

                except IndexError as ie:
                    pass

        if not filing_rsrc_cache and len(filing_pattern) != 0:
            self.alogger.debug("Matched filing types count: {} ".format(len(result)))

            self.alogger.debug("Performing pattern matching")
            for filing_resource, filing_text in result.items():
                for pattern, cpattern in acquirePatterns.items():
                    if re.search(cpattern, filing_text):
                        self.alogger.debug("Pattern Matches: {0}".format(filing_resource))
                        self.search_string(filing_text, 1, 1, pattern)
