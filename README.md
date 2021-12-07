
<div id="top"></div>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<h3 align="center">COVID-19 Dashboard</h3>

  <p align="center">
    A dashboard application that coordinates information about the COVID infection rates from the Public Health England API and news
stories about Covid from the news.org API.
    <br />
    <a href="https://github.com/vigneshmohan2002/ECM1400_Project"><strong>Explore the docs »</strong></a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#dashboard-in-use">Dashboard in use</a></li>
    <li><a href="#json-file-format">JSON File Format</a></li>
    <li><a href="#accepted-values-for-ud_location_type">Accepted values for ud_location_type</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

COVID-19 Dashboard

Since the outbreak of COVID-19 the day-to-day routine for many people has been disrupted and
keeping up-to-date with the local and national infection rates and news on government guidelines
has become a daily challenge. This application aims to help users get all the information they need about the pandemic in a quick glance.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [sched.py](https://docs.python.org/3/library/sched.html)
* [Flask.py](https://flask.palletsprojects.com/en/2.0.x/)
* [json.py](https://docs.python.org/3/library/json.html)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Installation

1. Get a free API Key at https://newsapi.org
2. Download the project at https://github.com/vigneshmohan2002/ECM1400_Project
3. Install the sched and flask packages if necessary.
   ```sh
   pip install sched
   pip install flask
   ```
4. Enter your API key from newsapi.org in `config.json`
   ```sh
   News_API_key = "ENTER_YOUR_API_KEY"
   ```
5. Run the project from user_interface.py
    ```sh
   python3 user_interface.py
   ```
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Dashboard in use

https://github.com/vigneshmohan2002/ECM1400_Project/blob/c3d4eaf13eed891a06b85da85d22c31af78ba93f/Screen%20Shot%202021-12-07%20at%2012.35.06%20AM.png

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## JSON File Format

{
  ud_location:  The location of the user in England
  
  ud_location_type:  The location type (See below)
  
  ud_search_terms: Terms the user wishes the news articles to be relevant to
  
  filepath: The filepath where the user wishes to store the csv files downlaoded and processed  by the application
  
  News_API_key: Enter the user's own API key here
  
update_no_time_specified: Whether the user would like an immediate update when the "Submit" button is pressed without an update time specified or not. 'true' or 'false'
  
 structure: {"Name of column in .csv file": "API Name as seen in https://coronavirus.data.gov.uk/metrics/name"} (Each key-value pair generates a separate column)
  Each tuple in the summation_country and summation_area lists results in an additional key-value pair returned by covid_API_request, passing each element as a parameter into the finding_summation_over_rows function.
  summation_country: [(name_of_column_csv, user_defined_dict_key, number_of_days, skip)],
  summation_area: [(name_of_column_csv, user_defined_dict_key, number_of_days, skip)],
  Each tuple in the most_recent_datapoint_country and most_recent_datapoint_area lists results in an additional key-value pair returned by covid_API_request, passing each element as a parameter into the finding_most_recent_datapoint function.
  most_recent_datapoint_country: [(name_of_column_csv, user_defined_dict_key, skip)],
  most_recent_datapoint_area: [(name_of_column_csv, user_defined_dict_key, skip)],
  number_of_articles_on_the_page: Number of articles generated in an update.
}

<p align="right">(<a href="#top">back to top</a>)</p>



## Accepted values for ud_location_type


`region`

Region data

`nhsRegion`

NHS Region data

`utla`

Upper-tier local authority data

`ltla`

Lower-tier local authority data
<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Vignesh Mohanarajan - Github: @vigneshmohan2002 - vm347@exeter.ac.uk

Project Link: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name)

<p align="right">(<a href="#top">back to top</a>)</p>
