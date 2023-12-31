"""
Include all the functions that made up of `parse_pmid_info` function
"""

import bs4
import httpx

async def fetch_json(url, params):
    """
    Utility function to fetch and convert json response.

    This function primary use to fetch the pmid_list (JSON response)
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()


async def fetch_html(url):
    """
    This function use to parse HTML or XML response to bs4 src.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    return bs4.BeautifulSoup(response.text, features="xml")


def construct_apa_author_name(last_name, initials):
    family_name = " ".join(sur + '.' for sur in initials)
    return f'{last_name}, {family_name}'


def get_text_or_none(element):
    """
    Helper function to return None instead of get_text if the element is None
    """
    if element is not None:
        return element.get_text()
    else:
        return None


def get_author_variants(src):
    """
    Name of author in variant format
    """
    author_list = []
    authors = src.select("Author")
    if len(authors) > 0:
        try:
            for i in authors:
                def name_getter(x): return i.select_one(x).get_text()
                last_name = name_getter("LastName")
                fore_name = name_getter("ForeName")
                initials = name_getter("Initials")
                apa_name = construct_apa_author_name(last_name, initials)
                affiliate = get_text_or_none(src.select_one('Affiliation'))
                author_list.append({'last_name': last_name, 'fore_name': fore_name,
                                'initials': initials, 'apa_name': apa_name, 'affiliate': affiliate})

            return author_list
        except Exception:
            return []
    else:
        return []


async def get_cited_num(pmid):
    cited_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={pmid}'
    src = await fetch_html(cited_url)
    num_cite = get_text_or_none(src.select_one('div.results-amount > h3 > span'))
    return num_cite


