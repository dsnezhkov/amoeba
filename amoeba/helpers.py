#!/usr/bin/env python
import logging
import argparse


class HelpAction(argparse._HelpAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]

        for subparsers_action in subparsers_actions:

            # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                print("\n<SOURCE:  '{}'>".format(choice))
                print(subparser.format_help())

        parser.exit()


class Configurator:
    config = {}
    logger = None

    @staticmethod
    def parseArgs():
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="""
                
                Amoeba subsidiaries
                """,
            add_help=False
        )

        parser.add_argument('--help', action=HelpAction, help='Amoeba Help')

        subparsers = parser.add_subparsers()
        subparsers.title = 'Data Sources'
        subparsers.description = 'valid datasource'
        subparsers.help = 'Valid actions: edgar'
        subparsers.required = True
        subparsers.dest = 'datasource'
        subparsers.metavar = "<datasource: edgar> [options]"

        subparser_edgar = subparsers.add_parser('edgar')

        # TOP: Always required options
        orequired = parser.add_argument_group('Required parameters')
        # orequired.add_argument( .... )

        # TOP: options
        parser.add_argument('-v', '--verbose', choices=['info', 'debug'],
                            help='Verbosity level. Default: info', default='info')

        # EDGAR arguments
        # TODO: add fetch CIK Map
        subparser_edgar.add_argument('-e', dest="endpoint", default='https://www.sec.gov')
        subparser_edgar.add_argument('-O', dest="operation",
                                     choices=[
                                         'find-corp-name',
                                         'find-corps-names',
                                         'search-corp',
                                         # 'get-cik-map'
                                     ],
                                     help="""
                                                Find corporation by name,
                                                Find corporations by name patterns,
                                                Search records of a corporation
                                     """,
                                     required=True)

        subparser_edgar.add_argument('-m', dest="cikmap", nargs=1, type=argparse.FileType('rb'),
                                     help='Path to readable CIK mapping file')

        subparser_edgar.add_argument('-n', action='store', type=str, dest='edgar_company_name',
                                     help='Company Name')

        subparser_edgar.add_argument('-N', action='append', type=str, dest='edgar_company_names_fuzzy',
                                     default=[],
                                     help='List of Approx Company Names')
        subparser_edgar.add_argument('--fuzzydetails', action='store_true', dest='edgar_company_names_fuzzy_detail',
                                     default=False,
                                     help='Details on the company address. Default: False')

        subparser_edgar.add_argument('-c', action='store', type=str, dest='company_cik',
                                     help='Main Mode: Search Findings for a Company with CIK number')

        subparser_edgar.add_argument('-t', action='store', type=str, dest='company_filing_type',
                                     default='10-K',
                                     help='Specify Filing Type: <see list of types> Default: 10-k')

        subparser_edgar.add_argument('-y', action='store', type=str, dest='company_filing_subtype',
                                     default='EX-21',
                                     help='Specify Filing Sub Type: <EX-XX[.xx]> Default: EX-21')

        subparser_edgar.add_argument('-i', action='store', type=int, dest='company_filing_no_entries',
                                     default='100',
                                     help='Specify Number of Documents to Retrieve: <n> Default: 100')

        subparser_edgar.add_argument('-b', action='store', type=str, dest='company_filing_dateb',
                                     default='20200101',
                                     help='Specify "Before" Date to Retrieve: <YYYYMMDD> Default: 20200101')

        subparser_edgar.add_argument('-P', action='append', dest='company_filing_pattern',
                                     default=[],
                                     help='<Required> Specify Patterns to search for: <"a" "b" "c"> Default: None')

        subparser_edgar.add_argument('-d', action='store_true', dest='company_filing_rsrc_cache',
                                     default=False,
                                     help='Download Filing documents but do NOT process. Default: False')

        args = parser.parse_args()

        # Save and set arguments
        Configurator.config['args'] = args
        Configurator.config['verbose'] = args.verbose
        Configurator.logger = logging.getLogger('amoeba')
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %Z',
            level=eval("logging.{0}".format(Configurator.config['verbose'].upper())))

    @staticmethod
    def getLogger():
        return Configurator.logger

    @staticmethod
    def getConfig():
        return Configurator.config

    @staticmethod
    def printConfig():
        for c in Configurator.config:
            Configurator.logger.debug("CONF: {0}: {1}".format(c, Configurator.config[c]))
