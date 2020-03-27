#!/usr/bin/env python3

from amoeba.helpers import Configurator
from amoeba.amlib import Amoeba


def main():
    # Process command line arguments
    Configurator.parseArgs()

    # Setup configuration bindings
    config = Configurator.getConfig()
    Configurator.printConfig()

    # Configure logging facilities
    logger = Configurator.getLogger()
    amoeba = Amoeba(config, logger)

    # Process directives

    if config['args'].datasource == 'edgar':

        if config['args'].operation == 'find-corp-name':
            amoeba.find_company_by_name(config['args'].edgar_company_name)
        elif config['args'].operation == 'find-corps-names':
            amoeba.find_company_by_names_fuzzy(config['args'].edgar_company_names_fuzzy)
        elif config['args'].operation == 'search-corp':
            amoeba.search_company_filings_by_cik(cik=config['args'].company_cik,
                                                 filing_type=config['args'].company_filing_type,
                                                 filing_subtype=config['args'].company_filing_subtype,
                                                 no_of_entries=config['args'].company_filing_no_entries,
                                                 filing_date_before=config['args'].company_filing_dateb,
                                                 filing_pattern=config['args'].company_filing_pattern,
                                                 filing_rsrc_cache=config['args'].company_filing_rsrc_cache)


if __name__ == '__main__':
    main()
