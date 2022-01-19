#!/usr/bin/env python3
"""
MediaServer Database module.
Contains all interactions between the webapp and the queries to the database.
"""

import configparser
import json
import sys
from modules import pg8000

################################################################################
#   Welcome to the database file, where all the query magic happens.
#   My biggest tip is look at the *week 8 lab*.
#   Important information:
#       - If you're getting issues and getting locked out of your database.
#           You may have reached the maximum number of connections.
#           Why? (You're not closing things!) Be careful!
#       - Check things *carefully*.
#       - There may be better ways to do things, this is just for example
#           purposes
#       - ORDERING MATTERS
#           - Unfortunately to make it easier for everyone, we have to ask that
#               your columns are in order. WATCH YOUR SELECTS!! :)
#   Good luck!
#       And remember to have some fun :D
################################################################################

#############################
#                           #
# Database Helper Functions #
#                           #
#############################
#####################################################
#   Database Connect
#   (No need to touch
#       (unless the exception is potatoing))
#####################################################

def database_connect():
    """
    Connects to the database using the connection string.
    If 'None' was returned it means there was an issue connecting to
    the database. It would be wise to handle this ;)
    """
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'database' not in config['DATABASE']:
        config['DATABASE']['database'] = config['DATABASE']['user']

    # Create a connection to the database
    connection = None
    
    try:
        # Parses the config file and connects using the connect string
        connection = pg8000.connect(database=config['DATABASE']['database'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])

    except pg8000.OperationalError as operation_error:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(operation_error)
        return None

    except Exception as ex:
        template = "LINE 72: An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
    # return the connection to use
    return connection

##################################################
# Print a SQL string to see how it would insert  #
##################################################

def print_sql_string(inputstring, params=None):
    """
    Prints out a string as a SQL string parameterized assuming all strings
    """

    if params is not None:
        if params != []:
           inputstring = inputstring.replace("%s","'%s'")
    
    print(inputstring % params)

#####################################################
#   SQL Dictionary Fetch
#   useful for pulling particular items as a dict
#   (No need to touch
#       (unless the exception is potatoing))
#   Expected return:
#       singlerow:  [{col1name:col1value,col2name:col2value, etc.}]
#       multiplerow: [{col1name:col1value,col2name:col2value, etc.}, 
#           {col1name:col1value,col2name:col2value, etc.}, 
#           etc.]
#####################################################
def dictfetchall(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""
    
    result = []
    if (params is None):
        print(sqltext)
    else:
        print("we HAVE PARAMS!")
        print_sql_string(sqltext,params)
    
    print("LINE 125: INSIDE dictfetchall FUNCTION BEFORE EXECUTING SQL!!!!! ********************* \n")
    cursor.execute(sqltext,params)
    cols = [a[0].decode("utf-8") for a in cursor.description]
    returnres = cursor.fetchall()
    for row in returnres:
        result.append({a:b for a,b in zip(cols, row)})
    # cursor.close()

    for x in result:
        print(x)
        print("--------------------------------------------------------------------------------------------------------------------")
    return result

def dictfetchone(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""
    # cursor = conn.cursor()
    result = []
    cursor.execute(sqltext,params)
    cols = [a[0].decode("utf-8") for a in cursor.description]
    returnres = cursor.fetchone()
    result.append({a:b for a,b in zip(cols, returnres)})
    return result


#####################################################
#   Query (1)
#   Login
#####################################################
def check_login(username, password):
    """
    Check that the users information exists in the database.
        - True => return the user data
        - False => return None
    """
    conn = database_connect()

    if(conn is None):
        return None
    
    cur = conn.cursor()
    try:
        #sql below tries to log user in!
        sql ="""
            SELECT * FROM mediaserver.UserAccount
            WHERE username = %s and password = %s
            """

        print("USERNAME: ", username)
        print("PASSWORD: ", password)

        r = dictfetchone(cur, sql, (username, password))

        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    #except:
    except Exception as e:
        print("LINE 176: Query Failed with error {}".format(e))
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Is Superuser? - 
#   is this required? we can get this from the login information
#####################################################

def is_superuser(username):
    """
    Check if the user is a superuser.
        - True => Get the departments as a list.
        - False => Return None
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT isSuper
            FROM mediaserver.useraccount
            WHERE username=%s AND isSuper
            """
        
        print("username is: "+username)
        cur.execute(sql, (username))
        r = cur.fetchone()              # Fetch the first row
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (1 b)
#   Get user playlists
#####################################################
def user_playlists(username):
    """
    Check if user has any playlists
        - True -> Return all user playlists
        - False -> Return None
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #sql below tries to find all playlists for a particular user~

        sql = """
            SELECT collection_id, collection_name, COUNT(media_id)
            FROM mediaserver.MediaCollection 
            JOIN mediaserver.MediaCollectionContents
            USING(collection_id)
            JOIN mediaserver.MediaItem USING(media_id)
            WHERE username = %s
            GROUP BY collection_id, collection_name
            ORDER BY collection_id ASC
            """

        print("username is: "+username)
        r = dictfetchall(cur,sql, (username,))
        # print("return val is: ")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting User Playlists:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (1 a)
#   Get user podcasts
#####################################################
def user_podcast_subscriptions(username):
    """
    Get user podcast subscriptions.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #sql below tries to find all the podcasts that the user is subscribed to ~

        sql = """
            SELECT * FROM mediaserver.PodCast 
            JOIN mediaserver.Subscribed_Podcasts
            USING(podcast_id)
            WHERE username = %s
            """
        
        r = dictfetchall(cur,sql, (username,))

        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast subs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (1 c)
#   Get user in progress items
#####################################################
def user_in_progress_items(username):
    """
    Get user in progress items that aren't 100%
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        #sql below tries to find all in-progress items for the user~
        sql = """
            SELECT distinct media_id, play_count as playcount , progress, lastviewed, storage_location
            FROM mediaserver.MediaCollection mc
            JOIN mediaserver.UserMediaConsumption umc USING(username)
            JOIN mediaserver.MediaItem USING(media_id)
            WHERE umc.progress != 100 AND umc.progress!= 0 AND mc.username = %s
            ORDER BY lastviewed DESC
            """

        r = dictfetchall(cur,sql,(username,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting User Consumption - Likely no values:", sys.exc_info()[0])
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Get all artists
#####################################################
def get_allartists():
    """
    Get all the artists in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT
            a.artist_id, a.artist_name, COUNT(amd.md_id) AS count
            FROM 
                mediaserver.artist a 
                LEFT OUTER JOIN mediaserver.artistmetadata amd 
                ON (a.artist_id=amd.artist_id)
            GROUP BY a.artist_id, a.artist_name
            ORDER BY a.artist_name;
            """

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Artists:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all songs
#####################################################
def get_allsongs():
    """
    Get all the songs in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT 
            s.song_id, s.song_title, string_agg(saa.artist_name,',') AS artists
            FROM 
            mediaserver.song s LEFT OUTER JOIN
            (mediaserver.Song_Artists sa JOIN mediaserver.Artist a 
            ON (sa.performing_artist_id = a.artist_id)
            ) AS saa  ON (s.song_id = saa.song_id)
            GROUP BY s.song_id, s.song_title
            ORDER BY s.song_id
            """

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all podcasts
#####################################################
def get_allpodcasts():
    """
    Get all the podcasts in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT 
                p.*, pnew.count AS count  
                FROM 
                mediaserver.podcast p, 
                (SELECT 
                    p1.podcast_id, count(*) AS count 
                FROM 
                    mediaserver.podcast p1 
                    LEFT OUTER JOIN mediaserver.podcastepisode pe1 
                    ON (p1.podcast_id=pe1.podcast_id) 
                    GROUP BY p1.podcast_id) pnew 
                WHERE p.podcast_id = pnew.podcast_id;
            """

        r = dictfetchall(cur,sql)
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Podcasts:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Get all albums
#####################################################
def get_allalbums():
    """
    Get all the Albums in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT
                a.album_id, a.album_title, anew.count AS count, anew.artists
            FROM 
                mediaserver.album a, 
                (SELECT 
                    a1.album_id, COUNT(distinct as1.song_id) AS count, array_to_string(array_agg(distinct ar1.artist_name),',') AS artists
                FROM 
                    mediaserver.album a1 
			LEFT OUTER JOIN mediaserver.album_songs as1 ON (a1.album_id = as1.album_id) 
			LEFT OUTER JOIN mediaserver.song s1 ON (as1.song_id=s1.song_id)
			LEFT OUTER JOIN mediaserver.Song_Artists sa1 ON (s1.song_id = sa1.song_id)
			LEFT OUTER JOIN mediaserver.artist ar1 ON (sa1.performing_artist_id = ar1.artist_id)
                GROUP BY a1.album_id) anew 
            WHERE a.album_id = anew.album_id;
            """

        r = dictfetchall(cur,sql)
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Albums:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Query (3 a,b c)
#   Get all tvshows
#####################################################
def get_alltvshows():
    """
    Get all the TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # the query below gets all tv shows + ep counts
        sql = """
            SELECT tvshow_id, tvshow_title, COUNT(episode)
            FROM
            mediaserver.tvepisode
            JOIN
            mediaserver.tvshow
            USING (tvshow_id)
            GROUP BY tvshow_title, tvshow_id
            ORDER BY tvshow_id;
            """

        r = dictfetchall(cur,sql)
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all movies
#####################################################
def get_allmovies():
    """
    Get all the Movies in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT
            m.movie_id, m.movie_title, m.release_year, count(mimd.md_id) AS count
            FROM 
                mediaserver.movie m LEFT OUTER JOIN mediaserver.mediaitemmetadata mimd 
                ON (m.movie_id = mimd.media_id)
            GROUP BY m.movie_id, m.movie_title, m.release_year
            ORDER BY movie_id;
            """

        r = dictfetchall(cur,sql)
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get one artist
#####################################################
def get_artist(artist_id):
    """
    Get an artist by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT *
            FROM mediaserver.artist a LEFT OUTER JOIN
                (mediaserver.artistmetadata 
                NATURAL JOIN mediaserver.metadata
                NATURAL JOIN mediaserver.MetaDataType) amd
            ON (a.artist_id = amd.artist_id)
            WHERE a.artist_id=%s
            """

        r = dictfetchall(cur,sql,(artist_id,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Artist with ID: '"+artist_id+"'", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (2 a,b,c)
#   Get one song
#####################################################
def get_song(song_id):
    """
    Get a song by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # the query below gets all info about a song + artists that performed it
        sql = """
            SELECT S.song_title, artist_name AS artists, length
            FROM
            mediaserver.Song S
            NATURAL JOIN
            (mediaserver.Song_Artists SA
            JOIN
            mediaserver.Artist A
            ON
            (SA.performing_artist_id = A.artist_id)) saa
            WHERE S.song_id = %s
            GROUP BY s.song_title, length, artists;
            """

        r = dictfetchall(cur,sql,(song_id,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (2 d)
#   Get metadata for one song
#####################################################
def get_song_metadata(song_id):
    """
    Get the meta for a song by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # the query below gets all metadata about a song
        sql = """
        select *
        FROM
        mediaserver.song s
        JOIN
        mediaserver.mediaitem mi
        ON
        (s.song_id  = mi.media_id)
        LEFT OUTER JOIN
        (mediaserver.mediaitemmetadata
        NATURAL JOIN
        mediaserver.metadata
        NATURAL JOIN
        mediaserver.metadatatype)
        USING (media_id)
        WHERE song_id = %s;
        """


        r = dictfetchall(cur,sql,(song_id,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting song metadata for ID: "+song_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (6 a,b,c,d,e)
#   Get one podcast and return all metadata associated with it
#####################################################
def get_podcast(podcast_id):
    """
    Get a podcast by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        sql = """
            SELECT * FROM mediaserver.Podcast P
            NATURAL JOIN mediaserver.PodcastMetaData
            NATURAL JOIN mediaserver.metadata
            NATURAL JOIN mediaserver.MetaDataType
            LEFT OUTER JOIN mediaserver.MetaDataAssociated MDA
            on (md_id = md_id_associated)
            WHERE P.podcast_id = %s
            """
        r = dictfetchall(cur,sql,(podcast_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast with ID: "+podcast_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (6 f)
#   Get all podcast eps for one podcast
#####################################################
def get_all_podcasteps_for_podcast(podcast_id):
    """
    Get all podcast eps for one podcast by their podcast ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        sql = """
            SELECT media_id, podcast_episode_title, 
            podcast_episode_URI, podcast_episode_published_date,
            podcast_episode_length
            FROM mediaserver.Podcast P
            NATURAL JOIN mediaserver.PodcastEpisode
            WHERE podcast_id = %s
            ORDER BY podcast_episode_published_date DESC
        """
        r = dictfetchall(cur,sql,(podcast_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Podcast Episodes for Podcast with ID: "+podcast_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (7 a,b,c,d,e,f)
#   Get one podcast ep and associated metadata
#####################################################
def get_podcastep(media_id): #podcast_id before 
    """ 
    Get a podcast ep by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #queries all info about a podcast episode + associated data

        sql = """
            SELECT media_id, podcast_episode_title, podcast_episode_uri, podcast_episode_published_date, 
            podcast_episode_length, md_value, md_type_name
            FROM mediaserver.podcastepisode AS PCE
            NATURAL JOIN mediaserver.metadata
            NATURAL JOIN mediaserver.mediaitemmetadata 
            NATURAL JOIN mediaserver.MetaDataType
            LEFT OUTER JOIN (--mediaserver.mediaitemmetadata 
            mediaserver.MetaDataAssociated
            NATURAL JOIN mediaserver.MetaDataPermittedAssociations) AS pemd
            ON (PCE.media_id = pemd.md_id_associated)
            WHERE media_id = %s
            """

        r = dictfetchall(cur,sql,(media_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast Episode with ID: "+media_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 a,b)
#   Get one album
#####################################################
def get_album(album_id):
    """
    Get an album by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #the query below tries to get all info about an album + all relevant metadata
        sql = """
            SELECT *
            FROM mediaserver.album
            NATURAL JOIN
            mediaserver.albummetadata a
            LEFT OUTER JOIN
            (mediaserver.metadata
            NATURAL JOIN
            mediaserver.metadatatype) mmd
            ON (a.md_id = mmd.md_id)
            WHERE a.album_id = %s;
            """

        r = dictfetchall(cur,sql,(album_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 d)
#   Get all songs for one album
#####################################################
def get_album_songs(album_id):
    """
    Get all songs for an album by the album ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # the query below gets all info about a song + artists
        sql = """
            SELECT album_songs.track_num, s.song_id, song_title, 
            string_agg(a.artist_name,',') AS artists
            FROM
            mediaserver.album_songs
            NATURAL JOIN
            mediaserver.song s
            NATURAL JOIN
            (mediaserver.song_artists sa
            JOIN
            mediaserver.artist a
            ON
            (sa.performing_artist_id = a.artist_id))
            WHERE album_id = %s
            GROUP BY album_songs.track_num, s.song_id, song_title
            ORDER BY track_num;
            """

        r = dictfetchall(cur,sql,(album_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums songs with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 c)
#   Get all genres for one album
#####################################################
def get_album_genres(album_id):
    """
    Get all genres for an album by the album ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # the query below gets all info about all genres in an album,
        # based on all genres of the song in that album
        sql = """
        select distinct md_value, md_type_name
        from
        mediaserver.album_songs
        natural join
        mediaserver.song s
        join
        mediaserver.audiomedia am
        on
        (s.song_id = am.media_id)
        left outer join
        (mediaserver.mediaitemmetadata
        natural join
        mediaserver.metadata
        natural join
        mediaserver.metadatatype)
        using
        (media_id)
        where album_id = %s;
        """

        r = dictfetchall(cur,sql,(album_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums genres with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (10)
#   May require the addition of SQL to multiple 
#   functions and the creation of a new function to
#   determine what type of genre is being provided
#   You may have to look at the hard coded values
#   in the sampledata to make your choices
#####################################################

# helper function to identity genres media
def get_media(genre_id):

    """
    Get media the genre_id is from
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        sql = """
            SELECT md_type_name
            FROM
            mediaserver.metadata m
            NATURAL JOIN
            mediaserver.metadatatype
            WHERE (m.md_value = %s)
            """

        r = dictfetchall(cur,sql,(genre_id,))

        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Media with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (10)
#   Get all songs for one song_genre
#####################################################
def get_genre_songs(genre_id):
    """
    Get all songs for a particular song_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # the query below gets all info about all songs that belong to a particular genre_id
        sql = """
            SELECT song_title AS title, 'Song' AS type, media_id AS item_id
            FROM
            mediaserver.song s
            JOIN
            mediaserver.mediaitemmetadata mimd
            ON
            (s.song_id = mimd.media_id)
            NATURAL JOIN
            mediaserver.metadata
            NATURAL JOIN
            mediaserver.metadatatype
            WHERE (md_type_name = 'song genre')
            AND
            (md_value = %s);
            """

        r = dictfetchall(cur,sql,(genre_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Songs with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (10)
#   Get all podcasts for one podcast_genre
#####################################################
def get_genre_podcasts(genre_id):
    """
    Get all podcasts for a particular podcast_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # the query below gets all info about all podcasts that belong to a particular genre_id
        sql = """
            SELECT podcast_title AS title, 'Podcast' AS type, null AS item_id, podcast_id AS id
            FROM
            mediaserver.podcast
            NATURAL JOIN
            mediaserver.podcastmetadata
            NATURAL JOIN
            mediaserver.metadata
            NATURAL JOIN
            mediaserver.metadatatype
            WHERE (md_type_name = 'podcast genre')
            AND
            (md_value = %s)
            ORDER BY item_id DESC;
            """

        r = dictfetchall(cur,sql,(genre_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcasts with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (10)
#   Get all movies and tv shows for one film_genre
#####################################################
def get_genre_movies_and_shows(genre_id):
    """
    Get all movies and tv shows for a particular film_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # the query below gets all info about all movies + tv shows that belong to a particular genre_id

        sql = """
            SELECT *
            FROM
            (select movie_title AS title, 'Movie' AS type, media_id AS item_id, 
            md_type_name, md_value, movie_id AS id
            FROM
            mediaserver.metadatatype
            NATURAL JOIN
            mediaserver.metadata
            NATURAL JOIN
            mediaserver.mediaitemmetadata mimd
            JOIN mediaserver.movie m
            ON (m.movie_id = mimd.media_id)
           
            UNION

            SELECT tvshow_title as title, 'TV Show' AS type, null AS item_id, 
            md_type_name, md_value, tvshow_id AS id
            FROM
            mediaserver.tvshow
            NATURAL JOIN
            mediaserver.tvshowmetadata
            NATURAL JOIN
            mediaserver.metadata
            NATURAL JOIN
            mediaserver.metadatatype) AS u
            WHERE (u.md_type_name = 'film genre')
            AND (u.md_value = %s)
            ORDER BY item_id;
            """

        r = dictfetchall(cur,sql,(genre_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Movies and tv shows with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Query (4 a,b)
#   Get one tvshow
#####################################################
def get_tvshow(tvshow_id):
    """
    Get one tvshow in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # query below tries to get all info about a tv show + includes all relevant metadata

        sql = """
            SELECT tvshow_id, tvshow_title, md_value, md_type_name
            FROM mediaserver.tvshow
            NATURAL JOIN
            mediaserver.tvshowmetadata t
            LEFT OUTER JOIN
            (mediaserver.metadata
            NATURAL JOIN
            mediaserver.metadatatype) mmd
            ON (t.md_id = mmd.md_id)
            WHERE t.tvshow_id = %s
            """

        r = dictfetchall(cur,sql,(tvshow_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (4 c)
#   Get all tv show episodes for one tv show
#####################################################
def get_all_tvshoweps_for_tvshow(tvshow_id):
    """
    Get all tvshow episodes for one tv show in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # query below gets all info about all tv eps in a tv show
        sql = """
            SELECT media_id, tvshow_episode_title, season, episode, air_date
            FROM mediaserver.tvshow t
            NATURAL JOIN
            mediaserver.tvepisode
            WHERE t.tvshow_id = %s
            ORDER BY season, episode;
            """

        r = dictfetchall(cur,sql,(tvshow_id,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get one tvshow episode
#####################################################
def get_tvshowep(tvshowep_id):
    """
    Get one tvshow episode in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT *
            FROM mediaserver.TVEpisode te 
            LEFT OUTER JOIN
            (mediaserver.mediaitemmetadata 
            NATURAL JOIN mediaserver.metadata
            NATURAL JOIN mediaserver.MetaDataType 
            NATURAL JOIN mediaserver.mediaitem) temd
            ON (te.media_id=temd.media_id)
            WHERE te.media_id = %s;
            """

        r = dictfetchall(cur,sql,(tvshowep_id,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get one movie
#####################################################
def get_movie(movie_id):
    """
    Get one movie in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT *
            FROM mediaserver.movie m 
            LEFT OUTER JOIN
                (mediaserver.mediaitemmetadata 
                NATURAL JOIN mediaserver.metadata 
                NATURAL JOIN mediaserver.MetaDataType
                NATURAL JOIN mediaserver.mediaitem) mmd
            ON (m.movie_id=mmd.media_id)
            WHERE m.movie_id=%s;
            """

        r = dictfetchall(cur,sql,(movie_id,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Find all matching tvshows
#####################################################
def find_matchingtvshows(searchterm):
    """
    Get all the matching TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT 
                t.*, tnew.count AS count  
            FROM 
                mediaserver.tvshow t, 
                (SELECT 
                    t1.tvshow_id, count(te1.media_id) AS count 
                FROM 
                    mediaserver.tvshow t1 LEFT OUTER JOIN mediaserver.TVEpisode te1 
                    ON (t1.tvshow_id=te1.tvshow_id) 
                    GROUP BY t1.tvshow_id) tnew 
            WHERE t.tvshow_id = tnew.tvshow_id AND lower(tvshow_title) ~ lower(%s)
            ORDER BY t.tvshow_id;
            """

        r = dictfetchall(cur,sql,(searchterm,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Query (9)
#   Find all matching Movies
#####################################################
def find_matchingmovies(searchterm):
    """
    Get all the matching Movies in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # the query below gets all info about movie that matches a given search term
        sql = """
            SELECT m.*
            FROM mediaserver.movie m
            WHERE lower(movie_title) ~ lower(%s)
            ORDER BY m.movie_id;
            """

        r = dictfetchall(cur,sql,(searchterm,))
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Add a new Movie
#####################################################
def add_movie_to_db(title,release_year,description,storage_location,genre):
    """
    Add a new Movie to your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        SELECT 
            mediaserver.addMovie(
                %s,%s,%s,%s,%s);
        """

        cur.execute(sql,(storage_location,description,title,release_year,genre))
        conn.commit()                   # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a movie:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (8)
#   Add a new Song
#####################################################
def add_song_to_db(storage_location, description, song_title, length, song_genre, artist_id):
    """
    Get all the matching Movies in your media server
    """
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
                SELECT 
                    mediaserver.addSong(
                        %s,%s,%s,%s,%s,%s);
                """

        cur.execute(sql, (storage_location, description, song_title, length, song_genre, artist_id))
        conn.commit()  # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db
        return r

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a song:", sys.exc_info()[0])
        raise
    cur.close()  # Close the cursor
    conn.close()  # Close the connection to the db

    #############################################################################
    # Fill in the Function  with a query and management for how to add a new    #
    # song to your media server. Make sure you manage all constraints           #
    #############################################################################
    return None



#####################################################
#   Get last Movie
#####################################################
def get_last_movie():
    """
    Get all the latest entered movie in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT MAX(movie_id) AS movie_id 
            FROM mediaserver.movie
            """

        r = dictfetchone(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a movie:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#  FOR MARKING PURPOSES ONLY
#  DO NOT CHANGE


#####################################################
#   Get last Song
#####################################################
def get_last_song():
    """
    Get all the latest entered song in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            SELECT MAX(song_id) AS song_id
            FROM mediaserver.Song
            """

        r = dictfetchone(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a song:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


def to_json(fn_name, ret_val):
    """
    TO_JSON used for marking; Gives the function name and the
    return value in JSON.
    """
    return {'function': fn_name, 'res': json.dumps(ret_val)}

# =================================================================
# =================================================================

#extra functionality: EASY: displaying user contact details on login page

def get_contact_details(username):
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql ="""
            SELECT * FROM mediaserver.contactMethod
            WHERE username = %s;
            """
        r = dictfetchall(cur,sql,(username,))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting User Contact Details with username: "+username, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


def user_integrated_webplayer(username, media_id):
    """
    Get user in progress items that aren't 100%
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        #sql below tries to find all in-progress items for the user~
        sql = """
            SELECT progress, play_count FROM
            mediaserver.UserMediaConsumption
            WHERE username = %s
            and media_id = %s
        """

        r = dictfetchall(cur,sql,(username, media_id, ))
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting User Consumption - Likely no values:", sys.exc_info()[0])
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def add_user_media_to_db(playcount, progress, date, username, media_id):
    """
    Add user media progress to db
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        sql = """
            INSERT INTO mediaserver.usermediaconsumption (username, media_id, play_count, progress, lastviewed)
            SELECT ua.username, mi.media_id, %s, %s, %s
            FROM mediaserver.useraccount ua, mediaserver.mediaitem mi
            WHERE ua.username = %s AND media_id = %s;
            """

        cur.execute(sql,(playcount,progress,date,username, media_id,))
        conn.commit()                   # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a user media:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def update_user_media_db(playcount, progress, date, username, media_id):
    """
    Update user media progress to db
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        sql = """
            UPDATE mediaserver.usermediaconsumption
            SET play_count= %s, progress = %s, lastviewed = %s
            WHERE username = %s AND media_id = %s;
            """

        cur.execute(sql,(playcount,progress,date,username, media_id,))
        conn.commit()                   # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        print("Unexpected error updating a user media:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


def get_all_songgenres():
    """
    Get all the TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # the query below gets all song genres + ep counts
        sql = """
            SELECT DISTINCT(md_value)
            FROM mediaserver.MetaData NATURAL JOIN mediaserver.MetaDataType
            WHERE md_type_name = 'song genre'
            """

        r = dictfetchall(cur,sql)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting song genres:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None