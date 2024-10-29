#Done By Dacorie Smith

import requests
from requests.auth import HTTPBasicAuth
import csv
from datetime import date
import os
from nltk.sentiment import SentimentIntensityAnalyzer
import json
from datetime import datetime


class RedditAPI:
    def __init__(self, client_id, client_secret, user_agent):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.base_url = 'https://oauth.reddit.com'
        self.auth_url = 'https://www.reddit.com/api/v1/access_token'
        self.headers = {'User-Agent': self.user_agent}
        self.access_token = self.authenticate()

    def authenticate(self):
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        data = {'grant_type': 'client_credentials'}
        response = requests.post(self.auth_url, auth=auth, data=data, headers=self.headers)
        response.raise_for_status()
        return response.json()['access_token']

    def make_headers(self):
        self.headers['Authorization'] = f'bearer {self.access_token}'

    def get_subreddit_posts(self, subreddit):
        url = f'{self.base_url}/r/{subreddit}/top'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def search_posts(self, keyword):
        search_url = f"{self.base_url}/search?limit=1000&q={keyword}&sort=new"
        response = requests.get(search_url, headers=self.headers)
        response.raise_for_status()
        return response.json()


class PostFilter:
    @staticmethod
    def filter_posts(posts, min_length=10):
        filtered_posts = []
        counter = 0
        for post in posts['data']['children']:
            counter += 1
            selftext = post['data'].get('selftext', '')
            if len( selftext) > min_length:
                filtered_posts.append({
                    'title': post['data'].get('title', 'N/A'),
                    #'category': post['data'].get('category', 'N/A'),
                    #likes': post['data'].get('likes', 0),
                    'num_comments': post['data'].get('num_comments', 0),
                    'subreddit': post['data'].get('subreddit', 'N/A'),
                    #'view_count': post['data'].get('view_count', 0),
                    'selftext': selftext
                })
            if counter == 3:
                break
        return filtered_posts


class CSVWriter:
    @staticmethod
    def write_to_csv(file_path, posts):
        file_exists = os.path.exists(file_path)
        with open(file_path, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['title', 'category', 'likes', 'num_comments', 'subreddit', 'view_count', 'selftext']
            fieldnames = ['title', 'num_comments', 'subreddit', 'selftext']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(posts)


class JSONWriter:
    @staticmethod
    def write_to_json(file_path, posts):
        file_exists = os.path.exists(file_path)
        data = []
        if file_exists:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

        # Append new posts and write them back
        data.extend(posts)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)



class JobHuntingPostScraper:
    def __init__(self, client_id, client_secret, user_agent, csv_file_path, subreddits):
        self.api = RedditAPI(client_id, client_secret, user_agent)
        self.subreddits = subreddits
        self.csv_file_path = self.generate_csv_file_path(csv_file_path)

    def generate_csv_file_path(self, base_file_path):
        # Get current date and time
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Extract the directory and file name
        directory, file_name = os.path.split(base_file_path)
        # Extract the file extension (e.g., .csv)
        file_name_without_ext, ext = os.path.splitext(file_name)
        # Construct the new file name with the current time attached
        new_file_name = f"{file_name_without_ext}_{current_time}{ext}"
        # Return the full file path
        return os.path.join(directory, new_file_name)

    def fetch_and_store_posts(self):
        try:
            self.api.make_headers()
            all_post_straps = []
            for subreddit in self.subreddits:
                try:
                    posts = self.api.get_subreddit_posts(subreddit)
                    filtered_posts = PostFilter.filter_posts(posts)
                    all_post_straps.extend(filtered_posts)
                except Exception as e:
                    print(f"Error fetching or filtering posts for subreddit {subreddit}: {e}")
            CSVWriter.write_to_csv(self.csv_file_path, all_post_straps)
        except Exception as e:
            print(f"Error in fetch_and_store_posts method: {e}")

    def search_and_store_posts(self, keywords):
        try:
            self.api.make_headers()
            all_post_straps = []
            for keyword in keywords:
                try:
                    posts = self.api.search_posts(keyword)
                    filtered_posts = PostFilter.filter_posts(posts)
                    all_post_straps.extend(filtered_posts)
                except Exception as e:
                    print(f"Error searching or filtering posts for keyword '{keyword}': {e}")
            CSVWriter.write_to_csv(self.csv_file_path, all_post_straps)
        except Exception as e:
            print(f"Error in search_and_store_posts method: {e}")




def get_unique_subreddits(subreddit_names):
    subreddits_list = subreddit_names.strip().split('\n')
    subreddits_list = [sub.strip() for sub in subreddits_list if sub.strip()]
    return sorted(set(subreddits_list))


if __name__ == "__main__":
    # Subreddit names
    subreddit_names = """
    LifeAdvice
    careeradvice
    QuebecTI
    jobs
    Advice
    antiwork
    NoStupidQuestions
    Adulting
    recruitinghell
    FPandA
    adhdwomen
    careerguidance
    UnemploymentCA
    teachinginkorea
    Serverlife
    germany
    biotech
    analytics
    ITCareerQuestions
    LeavingAcademia
    neoliberal
    csMajors
    gamedev
    berlin
    supplychain
    ImposterSyndrome
    findapath
    cscareerquestionsEU
    librarians
    BPOinPH
    AMLCompliance
    securityguards
    MerchantNavy
    Healthygamergg
    BreakUps
    BeautyBizTalk
    OffMyChestPH
    PHJobs
    AskIndia
    JobFair
    snowflake
    JobsPhilippines
    indiasocial
    workingfilipino
    walmart
    piercing
    Upwork
    developersIndia
    MalayalamMovies
    kroger
    GetEmployed
    britishcolumbia
    AITAH
    libraryofshadows
    DarkTales
    Odd_directions
    Scams
    interviews
    lawofattraction
    UKJobs
    CivilEngineersAus
    Switzerland
    Doculand
    UXDesign
    EngineeringResumes
    askSingapore
    PhD
    servicenow
    resumes
    managers
    work
    cscareers
    remotework
    freelance
    freelancers
    WorkOnline
    forhire
    freelance
    digitalnomad
    telecommuting
    remotejobr
    WFH
    jobs
    careerguidance
    resumes
    interviews
    jobbit
    JobFair
    Startups
    Entrepreneur
    Productivity
    GetMotivated
    freelanceWriters
    RemoteWork
    gifs
    behindthegifs
    gif
    Cinemagraphs
    WastedGifs
    educationalgifs
    perfectloops
    highqualitygifs
    gifsound
    combinedgifs
    retiredgif
    michaelbaygifs
    gifrecipes
    mechanical_gifs
    bettereveryloop
    gifextra
    slygifs
    gifsthatkeepongiving
    wholesomegifs
    noisygifs
    brokengifs
    loadingicon
    splitdepthgifs
    blackpeoplegifs
    whitepeoplegifs
    asianpeoplegifs
    scriptedasiangifs
    reactiongifs
    shittyreactiongifs
    chemicalreactiongifs
    physicsgifs
    babyelephantgifs
    weathergifs
    pics
    PhotoshopBattles
    perfecttiming
    itookapicture
    Pareidolia
    ExpectationVSReality
    dogpictures
    misleadingthumbnails
    FifthWorldPics
    TheWayWeWere
    pic
    nocontextpics
    miniworlds
    foundpaper
    images
    screenshots
    mildlyinteresting
    interestingasfuck
    damnthatsinteresting
    beamazed
    reallifeshinies
    thatsinsane
    playitagainsam
    gentlemanboners
    prettygirls
    hardbodies
    girlsmirin
    thinspo
    goddesses
    shorthairedhotties
    fitandnatural
    wrestlewiththeplot
    skinnywithabs
    bois
    GentlemanBonersGifs
    asiancuties
    asiangirlsbeingcute
    PhotoshopBattles
    ColorizedHistory
    reallifedoodles
    HybridAnimals
    colorization
    amiugly
    roastme
    rateme
    uglyduckling
    prettygirlsuglyfaces
    wallpapers
    wallpaper
    Offensive_Wallpapers
    videos
    youtubehaiku
    artisanvideos
    DeepIntoYouTube
    nottimanderic
    praisethecameraman
    killthecameraman
    perfectlycutscreams
    donthelpjustfilm
    abruptchaos
    ShowerThoughts
    DoesAnybodyElse
    changemyview
    crazyideas
    howtonotgiveafuck
    tipofmytongue
    quotes
    casualconversation
    makenewfriendshere
    relationship_advice
    raisedbynarcissists
    legaladvice
    advice
    amitheasshole
    mechanicadvice
    toastme
    needadvice
    IAmA
    ExplainlikeIAmA
    AMA
    casualiama
    de_Iama
    whowouldwin
    wouldyourather
    scenesfromahat
    AskOuija
    themonkeyspaw
    shittysuperpowers
    godtiersuperpowers
    decreasinglyverbose
    jesuschristouija
    whatisthisthing
    answers
    NoStupidQuestions
    amiugly
    whatsthisbug
    samplesize
    tooafraidtoask
    whatsthisplant
    isitbullshit
    questions
    morbidquestions
    AskReddit
    ShittyAskScience
    TrueAskReddit
    AskScienceFiction
    AskOuija
    AskScience
    askhistorians
    AskHistory
    askculinary
    AskSocialScience
    askengineers
    askphilosophy
    askdocs
    askwomen
    askmen
    askgaybros
    askredditafterdark
    asktransgender
    askmenover30
    tifu
    self
    confession
    fatpeoplestories
    confessions
    storiesaboutkevin
    talesfromtechsupport
    talesfromretail
    techsupportmacgyver
    idontworkherelady
    TalesFromYourServer
    KitchenConfidential
    TalesFromThePizzaGuy
    TalesFromTheFrontDesk
    talesfromthecustomer
    talesfromcallcenters
    talesfromthesquadcar
    talesfromthepharmacy
    starbucks
    pettyrevenge
    prorevenge
    nuclearrevenge
    nosleep
    LetsNotMeet
    Glitch_in_the_Matrix
    shortscarystories
    thetruthishere
    UnresolvedMysteries
    UnsolvedMysteries
    depression
    SuicideWatch
    Anxiety
    foreveralone
    offmychest
    socialanxiety
    trueoffmychest
    unsentletters
    rant
    YouShouldKnow
    everymanshouldknow
    LearnUselessTalents
    changemyview
    howto
    Foodforthought
    educationalgifs
    lectures
    education
    college
    GetStudying
    teachers
    watchandlearn
    bulletjournal
    applyingtocollege
    lawschool
    todayilearned
    wikipedia
    OutOfTheLoop
    IWantToLearn
    explainlikeimfive
    explainlikeIAmA
    ExplainLikeImCalvin
    anthropology
    Art
    redditgetsdrawn
    heavymind
    drawing
    graffiti
    retrofuturism
    sketchdaily
    ArtPorn
    pixelart
    artfundamentals
    learnart
    specart
    animation
    wimmelbilder
    illustration
    streetart
    place
    breadstapledtotrees
    chairsunderwater
    painting
    minipainting
    gamedev
    engineering
    ubuntu
    cscareerquestions
    EngineeringStudents
    askengineers
    learnprogramming
    compsci
    java
    javascript
    coding
    machinelearning
    howtohack
    cpp
    artificial
    python
    learnpython
    Economics
    business
    entrepreneur
    marketing
    BasicIncome
    business
    smallbusiness
    stocks
    wallstreetbets
    stockmarket
    environment
    zerowaste
    history
    AskHistorians
    AskHistory
    ColorizedHistory
    badhistory
    100yearsago
    HistoryPorn
    PropagandaPosters
    TheWayWeWere
    historymemes
    castles
    linguistics
    languagelearning
    learnjapanese
    french
    etymology
    law
    math
    theydidthemath
    medicalschool
    medizzy
    psychology
    JordanPeterson
    Science
    AskScience
    cogsci
    medicine
    everythingscience
    geology
    Space
    SpacePorn
    astronomy
    astrophotography
    aliens
    rockets
    spacex
    nasa
    biology
    Awwducational
    chemicalreactiongifs
    chemistry
    physics
    entertainment
    fantheories
    Disney
    obscuremedia
    anime
    manga
    anime_irl
    awwnime
    TsundereSharks
    animesuggest
    animemes
    animegifs
    animewallpaper
    wholesomeanimemes
    pokemon
    onepiece
    naruto
    dbz
    onepunchman
    ShingekiNoKyojin
    yugioh
    BokuNoHeroAcademia
    DDLC
    berserk
    hunterxhunter
    tokyoghoul
    shitpostcrusaders
    Books
    WritingPrompts
    writing
    literature
    booksuggestions
    lifeofnorman
    poetry
    screenwriting
    freeEbooks
    boottoobig
    hfy
    suggestmeabook
    lovecraft
    comics
    comicbooks
    polandball
    marvel
    webcomics
    bertstrips
    marvelstudios
    defenders
    marvelmemes
    avengers
    harrypotter
    batman
    calvinandhobbes
    xkcd
    DCComics
    arrow
    unexpectedhogwarts
    spiderman
    deadpool
    KingkillerChronicle
    asoiaf
    gameofthrones
    freefolk
    jonwinsthethrone
    gameofthronesmemes
    daeneryswinsthethrone
    asongofmemesandrage
    lotr
    lotrmemes
    tolkienfans
    celebs
    celebhub
    EmmaWatson
    jessicanigri
    kateupton
    alisonbrie
    EmilyRatajkowski
    jenniferlawrence
    alexandradaddario
    onetruegod
    joerogan
    keanubeingawesome
    crewscrew
    donaldglover
    elonmusk
    cosplay
    cosplaygirls
    lego
    boardgames
    rpg
    chess
    poker
    jrpg
    DnD
    DnDGreentext
    DnDBehindTheScreen
    dndnext
    dungeonsanddragons
    criticalrole
    DMAcademy
    dndmemes
    magicTCG
    modernmagic
    magicarena
    zombies
    cyberpunk
    fantasy
    scifi
    starwars
    startrek
    asksciencefiction
    prequelmemes
    empiredidnothingwrong
    SequelMemes
    sciencefiction
    InternetIsBeautiful
    facepalm
    wikipedia
    creepyPMs
    web_design
    google
    KenM
    bannedfromclubpenguin
    savedyouaclick
    bestofworldstar
    discordapp
    snaplenses
    tronix
    instagramreality
    internetstars
    robinhood
    shortcuts
    scams
    tiktokcringe
    crackheadcraigslist
    4chan
    Classic4chan
    greentext
    facepalm
    oldpeoplefacebook
    facebookwins
    indianpeoplefacebook
    terriblefacebookmemes
    insanepeoplefacebook
    Tinder
    OkCupid
    KotakuInAction
    wikileaks
    shitcosmosays
    twitch
    livestreamfail
    serialpodcast
    podcasts
    tumblrinaction
    tumblr
    blackpeopletwitter
    scottishpeopletwitter
    WhitePeopleTwitter
    wholesomebpt
    latinopeopletwitter
    YoutubeHaiku
    youtube
    youngpeopleyoutube
    gamegrumps
    h3h3productions
    CGPGrey
    yogscast
    jontron
    Idubbbz
    defranco
    cynicalbrit
    pyrocynical
    SovietWomble
    RedLetterMedia
    videogamedunkey
    loltyler1
    ksi
    MiniLadd
    jacksepticeye
    """

    # Unique and sorted subreddits
    unique_subreddits = get_unique_subreddits(subreddit_names)

    # Your Reddit application credentials
    client_id = 'YIe9bFNK-bSkuCVdqDm6wA'
    client_secret = '9JR2Z-QLurO7D_G096_KaiDT1jsLqw'
    user_agent = 'MyAPI/0.0.1'

    # File path for CSV output
    csv_file_path = "data/redit_data_pull.csv"

    # Initialize the scraper
    scraper = JobHuntingPostScraper(client_id, client_secret, user_agent, csv_file_path, unique_subreddits)

    # Fetch posts from subreddits and save to CSV
    scraper.fetch_and_store_posts()

    # Keywords related to difficult job hunting experiences
    bad_job_hunting_keywords = ['rejection', 'overqualified', 'underqualified', 'no response', 'ghosted',
                                'bad job interview', 'interview', 'job hunting']

    # Search posts based on keywords and save to CSV
    scraper.search_and_store_posts(bad_job_hunting_keywords)
