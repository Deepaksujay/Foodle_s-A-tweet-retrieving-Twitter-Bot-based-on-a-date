import tweepy
import time,datetime,pytz

FILE_NAME = 'date_last_tweet.txt'

BOT_SCREEN_NAME = 'foodle_s'

def read_last_seen(FILE_NAME):
    file_read = open(FILE_NAME,'r')
    last_seen_id = int(file_read.read().strip())
    file_read.close
    return last_seen_id

def store_last_seen(FILE_NAME,id):
    file_write = open(FILE_NAME,'w')
    file_write.write(str(id))
    file_write.close()
    return None

consumer_key = 'sMU2JD5eKpXROWO2XyrN6TFP0'
consumer_secret = 'LvqfZGVpMIx9HJDo273ptLYfD0hTSDHTq7wPQp7cyPotfxWpck'
access_token = '1475020244913586177-SNEmu0oW8XOPX5SbxXwyDyua93IH7M'
access_token_secret = '6GyvoVx0GqIDirnZLhCbIVdYZDmCSLXbwUNJf3LsO13Ij'


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,wait_on_rate_limit=True)

def get_date_from(tweet):
    created_at = tweet.created_at
    return created_at

def find_tweet(tweets,date,a,b):
    if b >= a:
        mean = int((b + a)/2)
        if get_date_from(tweets[mean]).date() == date.date():
            return mean
        elif get_date_from(tweets[mean]).date() > date.date():
            return find_tweet(tweets,date,mean+1,b)
        else:
            return find_tweet(tweets,date,a,mean-1)
    else:
        return False

def get_tweet(screen_name,date,tweet_id):
    Retrived = True
    # IST = pytz.timezone('Asia/Kolkata')
    format = '%d-%m-%y %H:%M:%S'
    start_date = date + ' 00:00:00'
    end_date = date + ' 23:59:59'
    start_date = datetime.datetime.strptime(start_date,format)
    end_date = datetime.datetime.strptime(end_date,format)
    first = True
    while Retrived:
        if first:
            tweets = api.user_timeline(screen_name = screen_name,count = 200,max_id = tweet_id)
            first = False
        else:
            tweets = api.user_timeline(screen_name = screen_name,count = 200,max_id = tweets[-1].id)
        print(screen_name,get_date_from(tweets[0]).replace(tzinfo=None),get_date_from(tweets[-1]).replace(tzinfo=None),len(tweets))
        if get_date_from(tweets[0]).replace(tzinfo=None) < start_date:
            break
        elif len(tweets) == 1:
            return False
        if (not (get_date_from(tweets[-1]).replace(tzinfo=None) > end_date)) and (not (get_date_from(tweets[0]).replace(tzinfo=None) < start_date)):
            main_tweet_index = find_tweet(tweets,end_date,0,len(tweets)-1)
            if not main_tweet_index:
                return False
            else:
                return tweets[main_tweet_index] 

def check_date(day,month,year):
    if month < 0 or month > 12:
        return True
    if year < 15:
        return True
    if(month==1 or month==3 or month==5 or month==7 or month==8 or month==10 or month==12):
        max=31
    elif(month==4 or month==6 or month==9 or month==11):
        max=30
    elif(year%4==0 and year%100!=0 or year%400==0):
        max=29
    else:
        max=28
    if day < 1 or day > max:
        return True
    else:
        return False

def get_date_and_screen_name(tweet):
    error_code = None
    MONTHS = ['jan','feb','mar','apr','may','jun','jul','aug','sep',
        'oct','nov','dec']
    mention_main =  tweet.in_reply_to_screen_name
    if mention_main == BOT_SCREEN_NAME:
        mention_main = None
    test = 1
    for hashtag in tweet.entities['hashtags']:
        if test == 1:
            day_ = hashtag['text']
            break
        test = test + 1
    date = ''
    try:
        month = day_[slice(3)]
        month = month.lower()
        month = str(MONTHS.index(month) + 1)
        day = str(day_[slice(3,5,1)])
        year = str(day_[slice(7,9,1)])
        date = day+'-'+month+'-'+year
        error = check_date(int(day),int(month),int(year))
    except:
        error = True
    if not mention_main:
        error = True
        error_code = 'Not_accepting_non_reply_tweets'
    return date,mention_main,error,error_code

def main_code():
    # my_account = api.get_user()
    # time.sleep(10)
    mentioned_tweets = api.mentions_timeline(since_id = read_last_seen(FILE_NAME),count = 5)
    mentioned_tweets = mentioned_tweets[::-1]
    url = 'https://twitter.com/'
    for tweet in mentioned_tweets:
        date,mentioned_screen_name,error,error_code = get_date_and_screen_name(tweet)
        if not error:
            main_tweet = get_tweet(mentioned_screen_name,date,tweet.in_reply_to_status_id)
            # main_tweet = False
            if main_tweet:
                url = url + mentioned_screen_name + '/status/' + main_tweet.id_str
                print(url)
                api.update_status(f"Here is the tweet, enjoy!\n{url}",in_reply_to_status_id = tweet.id,auto_populate_reply_metadata = True)
            else:
                api.update_status(f"There's no tweets from '{mentioned_screen_name}' on {date}, there might also be a chance that it is too old to retrive as twitter restrics me!",in_reply_to_status_id = tweet.id,auto_populate_reply_metadata = True)
        elif error_code == "Not_accepting_non_reply_tweets":
            api.update_status(f"Hey '{tweet.user.screen_name}', at present we are not accepting tweets which doesn't reply to one, Kindly wait for next schedule update.\nThank You",in_reply_to_status_id = tweet.id,auto_populate_reply_metadata = True)
        else:
            # print(date,mentioned_screen_name,error)
            api.update_status(f"Hey '{tweet.user.screen_name}' there's something wrong with the Tweet.\nCheck bio for instructions",in_reply_to_status_id = tweet.id,auto_populate_reply_metadata = True)
        store_last_seen(FILE_NAME,tweet.id)

main_code()