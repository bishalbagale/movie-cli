from requests_html import HTMLSession
from colorama import Fore
import subprocess
import sys
import time

session = HTMLSession()

pageNo = 1


def banner():
    print("""\
        
███╗░░░███╗░█████╗░██╗░░░██╗██╗███████╗░░░░░░░█████╗░██╗░░░░░██╗
████╗░████║██╔══██╗██║░░░██║██║██╔════╝░░░░░░██╔══██╗██║░░░░░██║
██╔████╔██║██║░░██║╚██╗░██╔╝██║█████╗░░█████╗██║░░╚═╝██║░░░░░██║
██║╚██╔╝██║██║░░██║░╚████╔╝░██║██╔══╝░░╚════╝██║░░██╗██║░░░░░██║
██║░╚═╝░██║╚█████╔╝░░╚██╔╝░░██║███████╗░░░░░░╚█████╔╝███████╗██║
╚═╝░░░░░╚═╝░╚════╝░░░░╚═╝░░░╚═╝╚══════╝░░░░░░░╚════╝░╚══════╝╚═╝""")
    print()
    print()
    print("\t\t\t\t\t created by: bishalbagale")
    print()


def SorM():
    global category
    global searchInput
    series_or_movie = input("category? series or movie [s/m]? : ")
    print(f"{Fore.GREEN}press * and hit enter to go back{Fore.WHITE}")
    searchInput = input("search : ")
    if series_or_movie.upper() == "S":
        category = "TV"
        search(category, pageNo, searchInput)
    elif series_or_movie.upper() == "M":
        category = "Movies"
        search(category, pageNo, searchInput)
    else:
        print(f"{Fore.RED}choose correct category !{Fore.WHITE}")
        SorM()


def nextpageLink(rawLinks):
    for each in rawLinks:
        if "/torrent" in each: return each
    else: pass


def search(cat, pgNo, searchInput):  #search
    count = 0  # initial no. of search results

    if searchInput != "*":  #proceed with search dont go back to choose category
        search = searchInput.replace(" ", "%20")
        print()
        url = f"https://www.1377x.to/category-search/{search}/{cat}/{pgNo}/"
        r = session.get(url)

        # get the link to the next page from search results

        tbody = r.html.find(
            "tbody", first=True)  #get the tablebody containing search result
        searchResults = tbody.find(
            "tr")  #list of search results //contents of the table

        resultDict = {}  #dictionary of link to next page
        if len(searchResults) != 0:  #validate the result
            for result in searchResults:
                count += 1

                seeds = result.find(".seeds", first=True).text
                leeches = result.find(".leeches", first=True).text
                size = result.find(".size", first=True).text
                # uploader = result.find(".uploader", first=True).text
                name = result.find(".name", first=True).text
                nextpage = nextpageLink(result.absolute_links)
                resultDict[count] = nextpage  #add to the dictionary
                #alter the color of output
                if count % 2 == 0: color = Fore.LIGHTBLUE_EX
                else: color = Fore.LIGHTCYAN_EX
                print(
                    f"{color}{count}) {name} -->se:{seeds} -->le:{leeches} -->size:{size}"
                )
            try:  #check if multiple page results are available

                page = r.html.find(".pagination", first=True).find(
                    "ul", first=True).find(
                        "li"
                    )[-1].text  # grab last li tag to get the total no. of page
                print()
                print(
                    f"\t\t\t\t\t\t\t{Fore.LIGHTYELLOW_EX}page : {pgNo}/{page}{Fore.WHITE}"
                )
                print(
                    f"{Fore.GREEN}\n# press p to change page or press the indexed no. to choose the content and press enter{Fore.WHITE}"
                )
                chooseMovie(resultDict)

            except AttributeError:
                # In case of single page result

                print(f"\t\t\t\t\t\t\t{Fore.LIGHTYELLOW_EX}page : 1/1")
                chooseMovie(resultDict)

        else:  # no valid result found
            print(
                Fore.RED +
                "No match found! \n consider checking spelling or come back later !"
            )
    else:
        SorM()  #go back to choose category


def moreResults():
    pg = input("goto page-no. : ")
    search(category, pg, searchInput)


def chooseMovie(resultDict):

    indexInput = input()
    if indexInput.upper() == "P":
        moreResults()
    else:
        try:
            mLink = resultDict[int(indexInput)]
            contentChoosed(mLink)
        except KeyError:

            print(f"{Fore.RED}Invalid input !! Enter valid input{Fore.WHITE}")
            chooseMovie(resultDict)


# Scrape the torrent link of the content
def contentChoosed(mLink):
    r = session.get(mLink)
    links = r.html.absolute_links
    for link in links:
        if "magnet:?" in link:
            torrentLink = link
    downloadORstream(torrentLink)


def streamingMedium():

    medium = input("want to stream though vlc or mpv [v/m]? ")
    if medium.upper() == "V":
        return "vlc"
    elif medium.upper() == "M":
        return "mpv"
    else:
        print(f"\n {Fore.RED}invalid input !{Fore.WHITE}")
        streamingMedium()


def downloadORstream(torrentLink):

    cmd = []
    cmd.append("webtorrent")
    verify_download = input("want to stream or download [s/d]? ")
    if verify_download.upper() == "D":
        cmd.append(f'"{torrentLink}"')
    elif verify_download.upper() == "S":
        medium = streamingMedium()
        cmd.append(f'"{torrentLink}"')
        if medium == "vlc":
            cmd.append("--vlc")
        else:
            cmd.append("--mpv")

    else:
        print(f"\n {Fore.RED}invalid input !{Fore.WHITE}")
        downloadORstream(torrentLink)

    if sys.platform.startswith('win32'):
        subprocess.call(cmd, shell=True)
    elif sys.platform.startswith('linux'):
        subprocess.call(cmd)
    elif sys.platform.startswith('darwin'):
        print("\n tf you doing here rich kid ? pay for your movie !!")


banner()
time.sleep(1)
SorM()