
# Amoeba: Subsidiary Search and Corp Intel

> Amoebas eat algae, bacteria, plant cells, and microscopic protozoa and metazoa – some amoebas are parasites. They eat by surrounding tiny particles of food with pseudopods, forming a bubble-like food vacuole. The food vacuole digests the food.


It is surprisingly complex to get a quick answer to the question of what subsidiaries does even a _public_ company own. There are several companies that have created paid products to aggregate corporate information, and do a good job of providing access to their paid API. 

_"Where you must go; where the path of the One ends."_

Most (or some?) of the data can be accessed for free from SEC EDGAR portal, if you are willing to dive deep into scraping :) (more on challenges later). 
Amoeba shaves some minutes/hours from operator's time by providing tool assisted retrieval of data to answer the question of corporate subsidiary search.  

## Finding Corporation Entity w/SEC EDGAR

**Problem**: Need to find a corporation CIK number. We have the name of the entity.
> The Central Index Key or CIK is a 10-digit number used on the Securities and Exchange Commission's computer systems to identify corporations and individuals who have filed disclosure with the SEC

**Solution**: Find the CIK by the exact name known to us:
```
$ ./amoeba.py edgar -O find-corp-name -n "important data corp"
IMPORTANT CORP CORP:0000994980
```

**Problem:** However, sometimes we don't know the official name used for SEC registration. Let's say we only know part of the name.


```
$ ./amoeba.py edgar -O find-corp-name -n "IMPORTANT data"
Error:  'IMPORTANT CORP'
```
We may need to find similar sounding corps and then choose the right one.

**Solution** Let's `fuzzy` search the corporations:

```
$ ./amoeba.py  edgar -O find-corps-names -N "Important Corp" -N "ImportantCorp"
IMPORTANT CORP AVIATION LLC:0001442062
IMPORTANT CORP CAPITAL, INC.:0001442061
IMPORTANT CORP CARD SOLUTIONS, INC.:0001442052
IMPORTANT CORP COMMERCIAL SERVICES HOLDINGS, INC.:0001442050
IMPORTANT CORP COMMUNICATIONS CORP:0001442048
IMPORTANT CORP CORP:0000994980
IMPORTANT CORP CORPORATION:0000994980
IMPORTANT CORP DIGITAL CERTIFICATES INC.:0001442047
IMPORTANT CORP EC, LLC:0001467812
IMPORTANT CORP FINANCIAL SERVICES, L.L.C.:0001442046
IMPORTANT CORP GOVERNMENT SOLUTIONS, INC.:0001442045
IMPORTANT CORP GOVERNMENT SOLUTIONS, LLC:0001442044
IMPORTANT CORP GOVERNMENT SOLUTIONS, LP:0001442043
IMPORTANT CORP HOLDINGS INC.:0001611166
IMPORTANT CORP INTEGRATED SERVICES INC.:0001442042
IMPORTANT CORP LATIN AMERICA INC.:0001442041
IMPORTANT CORP MERCHANT SERVICES CORP:0001442040
IMPORTANT CORP MERCHANT SERVICES NORTHEAST, LLC:0001442038
IMPORTANT CORP MERCHANT SERVICES SOUTHEAST, L.L.C.:0001442037
IMPORTANT CORP MOBILE HOLDINGS, INC.:0001442036
IMPORTANT CORP PAYMENT SERVICES, LLC:0001442034
IMPORTANT CORP PITTSBURGH ALLIANCE PARTNER INC.:0001442033
IMPORTANT CORP PS ACQUISITION INC.:0001442032
IMPORTANT CORP REAL ESTATE HOLDINGS L.L.C.:0001442031
IMPORTANT CORP RESOURCES, LLC:0001442030
IMPORTANT CORP RETAIL ATM SERVICES L.P.:0001442029
IMPORTANT CORP SECURE LLC:0001442028
IMPORTANT CORP SOLUTIONS INC:0001141473
IMPORTANT CORP SOLUTIONS L.L.C.:0001442027
IMPORTANT CORP TECHNOLOGIES, INC.:0001442026
IMPORTANT CORP TRANSPORTATION SERVICES, INC.:0001442077
IMPORTANT CORP VOICE SERVICES:0001442024
IMPORTANT CORP, L.L.C.:0001442023
IMPORTANT SOURCE CORP, INC.:0001350573
```

**Problem** : How do we know which one is the correct one?
**Solution** : Let's get some pointers on the entities to help us decide

```
$ ./amoeba.py  edgar -O find-corps-names -N "Important Corp" --fuzzydetails

Name/CIK: IMPORTANT CORP AVIATION LLC:0001442062
State Incorporated/State Located : DE/CO
Addresses:

     @type mailing
      city OMAHA
     state NE
   street1 6855 PACIFIC STREET, AK-310
       zip 68106

     @type business
      city GREENWOOD VILLAGE
     phone 402-951-7008
     state CO
   street1 6200 S. QUEBEC STREET
       zip 80111
---

Name/CIK: IMPORTANT CORP CAPITAL, INC.:0001442061
State Incorporated/State Located : DE/CO
Addresses:

     @type mailing
      city OMAHA
     state NE
   street1 6855 PACIFIC STREET, AK-310
       zip 68106

     @type business
      city GREENWOOD VILLAGE
     phone 402-222-3002
     state CO
   street1 6200 S. QUEBEC STREET
       zip 80111
---

Name/CIK: IMPORTANT CORP CARD SOLUTIONS, INC.:0001442052
State Incorporated/State Located : MD/CO
Addresses:

     @type mailing
      city OMAHA
     state NE
   street1 6855 PACIFIC STREET, AK-310
       zip 68106

     @type business
      city GREENWOOD VILLAGE
     phone 402-222-3002
     state CO
   street1 6200 S. QUEBEC STREET
       zip 80111
---

Name/CIK: IMPORTANT CORP CORP:0000994980
State Incorporated/State Located : DE/NY
Addresses:

     @type mailing
      city NEW YORK
     state NY
   street1 225 HELLO STREET
   street2 29TH FLOOR
       zip 10284

     @type business
      city NEW YORK
     phone (800) 765-3660
     state NY
   street1 225 HELLO STREET
   street2 29TH FLOOR
       zip 10284
---
```
The last entry looks good! CIK number `0000994980` 

## Searching for Corporation subsidiaries w/SEC EDGAR
We need to have some tools to be able to find corporate subsidiaries. The list may fluctuate as companies acquire or merge with others.

There are over 338 _Types_ of filing forms developed by SEC, and these forms have at least 40 types of _Exhibits_ to go with the forms. Not every company uses all, not every company uses the right ones, not every company discloses appropriate information due to variations in legal structure of subsidiaries, not every parent company is US-based and registered with SEC. 

Let's take the most common scenario when a Corporation is registered in the US, and discloses it's subsidiaries. 

### SEC filing and Exhibit 21.X 
The preferred way to disclose ownership of a subsidiary by a corporation is to find the company's 10-K filing and locate their _Exhibit 21_ (or `EX-21.X`) form. This document should list the names of subsidiaries and their incorporation state and operating locations.

_Note_: SEC forms formats are not consistent and have mutated over the years. This is also true for the exhibits. Most of the newer submissions are done with XRBL format but the submissions are not consistent and there is arguably limited structure to retrieve the exhibit data.

**Problem** Where are the _EX-21.X_? And how do we get them?

**Solution A**: We can locate and download documents from SEC.GOV EDGAR Database by doing web scraping of the data posted in their portal. Due to the issues with formatting, it may be a preferred method to assist the analyst with data retrieval.

**Solution B**: We can enable realtime retrieval of different types of Filings and perform a pattern search across the data. This is useful when the company does not disclose it's subsidiaries in one place (EX-21.X) but refer to acquisitions in their other documents filed with SEC. This method is a lot more fuzzy, and more involved but may augment analyst's research efforts when the pickings are slim. For example, _EX-99.X_ documents may disclose such news. 

### Solution A: EX-21 document retrieval

```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 10-K -y EX-21 -d

Storing dex21.htm from https://www.sec.gov/Archives/edgar/data/883980/000119312511061160/dex21.htm locally: Archives/edgar/data/883980/000119312511061160/dex21.htm
Storing dex21.htm from https://www.sec.gov/Archives/edgar/data/883980/000119312510052892/dex21.htm locally: Archives/edgar/data/883980/000119312510052892/dex21.htm
Storing dex21.htm from https://www.sec.gov/Archives/edgar/data/883980/000119312509062390/dex21.htm locally: Archives/edgar/data/883980/000119312509062390/dex21.htm
Storing 0008.txt from https://www.sec.gov/Archives/edgar/data/883980/000104596901000322/0001045969-01-000322-0008.txt locally: Archives/edgar/data/883980/000104596901000322/0001045969-01-000322-0008.txt
```

```
EX-21 5 dex21.htm LIST OF IMPORTANT CORP CORPORATION SUBSIDIARIES
Exhibit 21


LIST OF IMPORTANT CORP CORPORATION SUBSIDIARIES

(as of February 24, 2004)
 

Name of Subsidiary

  	
Jurisdiction of Incorporation

Achex, Inc. *

  	Delaware
ACT (Computer Services) Limited

  	United Kingdom
Active Business Services Limited

  	United Kingdom
American Rapid Corporation

  	Delaware
Atlantic Bankcard Properties Corporation

  	North Carolina
Atlantic States Bankcard Association, Inc.

  	Delaware
B1 PT Services Inc.

  	Delaware
Banc One Payment Services, L.L.C. *

  	Delaware
Bankcard Investigative Group Inc.

  	Delaware
BidPay.com, Inc.

  	Delaware
Business Office Services, Inc.

  	Delaware
Call Interactive Holdings LLC

  	Delaware
CallTeleservices, Inc.

  	Nebraska
CanPay Holdings, Inc.

  	Delaware
Cardnet Merchant Services Ltd. *

  	United Kingdom
Cardservice Canada Company

  	Canada
Cardservice Delaware, Inc.

  	Delaware
Cardservice International, Inc.

  	California
Cardservice Omni Limited

  	United Kingdom
CardSolve International Inc. Solucartes International Inc.

  	Canada
Carlsbad Holdings, LP

  	Delaware
CashCall Systems Inc. *

  	Canada
Casino ATM LLC

  	Delaware
Casino Credit Services, LLC

  	Delaware
CCI Acquisition, LLC *

  	Delaware
Central Credit LLC *

  	Delaware
CESI Holdings, Inc.

  	Delaware
Chase Merchant Services, L.L.C. *

  	Delaware
Christopher C. Varvias & Assoc. Elect. MT S.A. *

  	Greece
Credit Card Holdings Limited

  	Ireland
Credit Performance Inc.

  	Delaware
CUETS/Important Corp Merchant Partnership *

  	Ontario
CUETS/Important Corp Processing Partnership *

  	Ontario
```
This retrieves `EX-21.*` documents from SEC and stores them locally for the manual review. This does not search for patterns as it assumes the exhibit is the pure list of subsidiaries owned by the corporation and disclosed in SEC filings. 

There are some shortcomings of the API, and scarping pagination is not supported yet. However you can retrieve historical documents by specifying the cutoff data to search from: 

```
$ ./amoeba.py edgar -O search-corp -c 0000994980 -t 10-K -y EX-21 -b 20101010
```

Analyst can take the information obtained from the EX-21 documents and research the subsidiaries one by one. 


### Solution B: Filing form pattern search

The other mode is to be able to search for patterns across filing documents.
_Amoeba_ tool put in this mode is able to search across common filing types and exhibits.

```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 10-Q -y EX-21 -b 20000101  -P "aquire" -P "acquisition"
```

As we have mentioned before there is little structure to the disclosures for companies that do not fill out Ex-21. The patterns you specify and the types of filings you search in will determine the rate of success. 

To illustrate here we are performing multiple searches with various degrees of success.


Type: 10-Q
Subtype: EX-21
Patterns: "acquire", "acquisition"
Results: None.
```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 10-Q -y EX-21 -b 20000101  -P "aquire" -P "acquisition"
```
Type: 10-Q
Subtype: 10-Q
Patterns: "acquire", "acquisition"
Results: None.
```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 10-Q -y 10-Q -b 20000101  -P "aquire" -P "acquisition"
```

Type: 10-K
Subtype: EX-99
Patterns: "acquire", "acquisition"
Results: None.
```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 10-K -y EX-99 -b 20000101  -P "aquire" -P "acquisition"
```

Type: 10-K
Subtype: EX-99
Patterns: "fiserv"
Results: None.
```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 10-K -y EX-99   -P "fiserv"
```
Type: 10-K
Subtype: 10-K
Patterns: "fiserv"
Results: None.
```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 10-K -y 10-K   -P "fiserv"
```

Type: 425
Subtype: 425
Patterns: "acquire", "acquisition"
Results: Success (with manual review).
```
$ ./amoeba.py  edgar -O search-corp -c 0000994980 -t 425 -y 425   -P "acquire" -P "acquisition"
```
(Abridged output for analysis):
```
        >>> proposed acquisition and related transactions and to achieve the synergies


-- Context -- 
of 1995, including statements regarding the ability of Fiserv to complete the
proposed acquisition and related transactions and to achieve the synergies
described herein. Statements can generally be identified as forward-looking
----

        >>> | As you know, back in 2007, we acquired CheckFree and that was really to make


-- Context -- 
  
| As you know, back in 2007, we acquired CheckFree and that was really to make
a strong statement. That was pre-iPhone, actually not quite true. It was 45
----

        >>> acquisition of the Elan debit processing business. Integration with our card


-- Context -- 
$3.2 billion for the year, which includes 2 months of impact from the
acquisition of the Elan debit processing business. Integration with our card
services business is in flight and progressing well.
----

        >>> merger agreement to acquire Important Corp Corporation in an all-stock transaction


-- Context -- 
On January 16, 2019, Fiserv announced that it had entered into a definitive
merger agreement to acquire Important Corp Corporation in an all-stock transaction
for an equity value of approximately $22 billion as of the announcement. The
----

        >>> On January 16, 2019, we announced that Fiserv has agreed to acquire Important Corp


-- Context -- 

On January 16, 2019, we announced that Fiserv has agreed to acquire Important Corp
in an all-stock transaction, uniting two premier companies to create one of
----

        >>>  Merger Agreement ) pursuant to which the Company will acquire Important Corp


-- Context -- 
press release announcing their entry into a definitive merger agreement (the

Corporation in an all-stock transaction. A copy of the joint press release is
----

        >>> This is important, because in December, we announced the intent to acquire


-- Context -- 

This is important, because in December, we announced the intent to acquire
Cashcard Australia Limited. It s a leading electronic payment service
----
        >>> 1. Important Corp's acquisition of Concord would combine the largest and third-largest point-of-sale ("POS") PIN debit networks in the United States. POS PIN debit networks are the telecommunications and payment infrastructure that connects merchants to consumers' demand deposit accounts at banks. These networks enable consumers to purchase goods and services from merchants through PIN debit transactions by swiping their bank card at a merchant's terminal and entering a Personal Identification Number, or PIN. Within seconds, the purchase amount is debited from the customer's bank account and transferred to the retailer's bank. 


-- Context -- 

1. Important Corp's acquisition of Concord would combine the largest and third-largest point-of-sale ("POS") PIN debit networks in the United States. POS PIN debit networks are the telecommunications and payment infrastructure that connects merchants to consumers' demand deposit accounts at banks. These networks enable consumers to purchase goods and services from merchants through PIN debit transactions by swiping their bank card at a merchant's terminal and entering a Personal Identification Number, or PIN. Within seconds, the purchase amount is debited from the customer's bank account and transferred to the retailer's bank. 

----

        >>> based alternatives. Concord acquires, routes, authorizes, captures, and


-- Context -- 
financial transactions faster, more efficient, and more secure than paper-
based alternatives. Concord acquires, routes, authorizes, captures, and
settles virtually all types of electronic payment and deposit access
----

        >>> only two years ago, the DOJ approved Concord's acquisition of STAR, which


-- Context -- 
combined company would handle less than 45% of PIN debit transactions, when
only two years ago, the DOJ approved Concord's acquisition of STAR, which
resulted in Concord handling approximately 60% of exactly the same
----

        >>> customers' needs. This quarter, for example, we acquired 51% of Eposs a


-- Context -- 
distribution network by acquiring companies that have products to meet our
customers' needs. This quarter, for example, we acquired 51% of Eposs a
company that specializes in cellular prepaid products, focusing on serving
----

        >>> handcuffed on certain behaviors as it relates to our acquisition of Concord.


-- Context -- 
12.3%. We expect full-year revenue growth close to 14%. Remember, we are
handcuffed on certain behaviors as it relates to our acquisition of Concord.
Once again, our operating margins at 22.6% and our cash flow remain very
----

        >>> growth from the same period last year. On August 5th the company acquired a


-- Context -- 
**Payment Services** delivered third quarter revenue of $935 million, a 14%
growth from the same period last year. On August 5th the company acquired a
51% stake in Eposs, a U.K. provider of prepaid payment solutions. During the
----

        >>> announced a definitive merger agreement for Important Corp to acquire all


-- Context -- 
be entitled to vote at the meeting. On April 2, 2003, Important Corp and Concord
announced a definitive merger agreement for Important Corp to acquire all
outstanding stock of Concord in an all-stock transaction valued at
----
```

## Amoeba Usage:

```
$ ./amoeba.py  edgar -H
usage: amoeba.py edgar [-h] [-e ENDPOINT] -O
                       {find-corp-name,find-corps-names,search-corp}
                       [-m CIKMAP] [-n EDGAR_COMPANY_NAME]
                       [-N EDGAR_COMPANY_NAMES_FUZZY] [--fuzzydetails]
                       [-c COMPANY_CIK] [-t COMPANY_FILING_TYPE]
                       [-y COMPANY_FILING_SUBTYPE]
                       [-i COMPANY_FILING_NO_ENTRIES]
                       [-b COMPANY_FILING_DATEB] [-P COMPANY_FILING_PATTERN]
                       [-d]

optional arguments:
  -h, --help            show this help message and exit
  -e ENDPOINT
  -O {find-corp-name,find-corps-names,search-corp}
                        Find corporation by name, Find corporations by name
                        patterns, Search records of a corporation
  -m CIKMAP             Path to readable CIK mapping file
  -n EDGAR_COMPANY_NAME
                        Company Name
  -N EDGAR_COMPANY_NAMES_FUZZY
                        List of Approx Company Names
  --fuzzydetails        Details on the company address. Default: False
  -c COMPANY_CIK        Main Mode: Search Findings for a Company with CIK
                        number
  -t COMPANY_FILING_TYPE
                        Specify Filing Type: <see list of types> Default: 10-k
  -y COMPANY_FILING_SUBTYPE
                        Specify Filing Sub Type: <EX-XX[.xx]> Default: EX-21
  -i COMPANY_FILING_NO_ENTRIES
                        Specify Number of Documents to Retrieve: <n> Default:
                        100
  -b COMPANY_FILING_DATEB
                        Specify "Before" Date to Retrieve: <YYYYMMDD> Default:
                        20200101
  -P COMPANY_FILING_PATTERN
                        <Required> Specify Patterns to search for: <"a" "b"
                        "c"> Default: None
  -d                    Download Filing documents but do NOT process. Default:
                        False

```