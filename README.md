# Mockingbird: Generate mock documents for data classification

## About

Mockingbird is a Python library for generating mock documents in various formats. It accepts user-defined data, and embeds it into documents generated in many different formats. Developers can use Mockingbird to quickly generate datasets, with particular use for validating the efficacy of a data classification software. 

## Installation
 
The easiest way to install Mockingbird is by using `pip`:

`pip install mockingbird`

For local development, clone the repository and run `pip install .`

## Getting Started

Mockingbird can run as a functional Python library or as a CLI. 


### CLI Usage

Once installed with pip, unix-like systems can use the command `mockingbird_cli --h` to access Mockingbird's 
command line interface. Some sample CLI calls are:

```
mockingbird_cli --type dry -o ./output/dry_test/
mockingbird_cli --type csv -i ./samples/csv_sample.csv -o ./output/csv/
mockingbird_cli --type csv_curl -i <curl'able URL> -o ./output/csv_curl/
mockingbird_cli --type mockaroo -i ./samples/sample_schema.json --mockaroo_api <mockaroo API> -o ./output/mockaroo
```

### As a Python Library

#### Starting from Code

Mockingbird functions as a fully functional Python library. A basic example generating documents using
mock-data is demonstrated below. In this example, key-value pairs are inserted as strings mapping to a list of strings. 


```
from mockingbird import Mockingbird

# Spawn a new Mockingbird session
fab = Mockingbird()

# Set which file extensions to output
fab.set_file_extensions(["html", "docx", "yaml", "xlsx", "odt"])

# Input the data we want to test / inject into the documents
fab.add_sensitive_data(keyword="ssn", entries=["000-000-0000", "999-999-9999"])
fab.add_sensitive_data(keyword="dob", entries=["01/01/1991", "02/02/1992"])

# Generate and save the fabricated documents
fab.save(save_path="./output_basic/")
fab.dump_meta_data(output_file="./output_basic/meta_data.json")
```


#### Starting from CSV

Mockingbird can be started using a CSV file, treating the column headers as keywords, and the remaining rows as entries. 

The CSV's are expected to be structured as the following,
```
FILE: mockingbird_data.csv

ssn, dob
000-000-000, 01/01/1991
999-999-999, 02/02/1992
```

```
from mockingbird.mb_wrappers import MockingbirdFromCSV


# This effectively loads files from the csv and generates a session using each column
fab = MockingbirdFromCSV("csv_sample.csv")
fab.set_all_extensions()

fab.save(save_path="./output_csv/")
fab.dump_meta_data(output_file="./output_csv/meta_data.json")
```

Optionally, multiple keywords can be defined in the CSV header file, which Mockingbird will split up into separate 
keywords. For example, rather than just testing the keyword ```ssn```, we can test ```ssn``` and ```social security number```.
Multiple keywords can be defined in the CSV file by using `;` as a delimiter. 

For example,

```
FILE: mockingbird_data.csv

ssn;social security number,dob;date of birth;birth
000-000-000, 01/01/1991
999-999-999, 02/02/1992
```

This will generate documents for each keyword in each column header. 


#### Starting Using Mockaroo

Using a Mockaroo API key, we can request mocked data using json requests from Mockaroo's servers. Currently, the request has to be saved to
a json file on disk, and loaded during runtime. More documentation can be found at [Mockaroo's Website](https://www.mockaroo.com/api/docs), but below
is a json-example.

```
FILE: mockaroo_request.json

[
  {
    "name": "ssn;social security;social",
    "type": "SSN"
  },
  {
    "name": "cc;credit card",
    "type": "Credit Card #"
  },
  {
    "name": "phone;phone-number;number",
    "type": "Phone"
  },
  {
    "name": "name;fullname;full name",
    "type": "Full Name"
  }
]
```

In code, Mockingbird can use this request as a json-payload, 

```
import json
from mockingbird.mb_wrappers import MockingbirdFromMockaroo

with open("mockaroo_request.json") as json_file:
    schema_request = json.load(json_file)

fab = MockingbirdFromMockaroo(api_key="MOCKAROO_API_KEY", schema_request=schema_request)
fab.set_all_extensions()
fab.save(save_path="./output_mockaroo/")
fab.dump_meta_data(output_file="./output_mockaroo/meta_data.json")
```


## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full license text.
