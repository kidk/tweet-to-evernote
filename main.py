#!/usr/bin/env python2
import tweepy
import pprint
import json
from evernote.api.client import EvernoteClient
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import ConfigParser, os

config = ConfigParser.ConfigParser()
config.readfp(open('credentials.cfg'))

# Login to Twitter
twitterAuth = tweepy.OAuthHandler(config.get("Credentials", "TWITTER_CONSUMER_TOKEN"), config.get("Credentials", "TWITTER_CONSUMER_SECRET"))
twitterAuth.set_access_token(config.get("Credentials", "TWITTER_ACCESS_TOKEN"), config.get("Credentials", "TWITTER_ACCESS_SECRET"))
twitterApi = tweepy.API(twitterAuth)
print("Twitter - Login to %s successfull" % twitterApi.me().name)

# Login to Evernote
client = EvernoteClient(token=config.get("Credentials", "EVERNOTE_TOKEN"), sandbox=False)
user_store = client.get_user_store()

# Check API version
version_ok = user_store.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)
if not version_ok:
    print("Old version of Evernote API")
    exit(1)

note_store = client.get_note_store()

# Get saved from twitter
favorites = []
for favorite in tweepy.Cursor(twitterApi.favorites).items():
   favorites.append({
       'id': favorite.id,
       'text': favorite.text
   })

pprint.pprint(favorites)

# Push to evernote and unfavorite
for tweet in favorites:
    try:
        # Create new note
        note = Types.Note()
        note.title = tweet['text'][:30].encode('utf-8')

        # Add content
        note.content = '<?xml version="1.0" encoding="UTF-8"?>'
        note.content += '<!DOCTYPE en-note SYSTEM ' \
            '"http://xml.evernote.com/pub/enml2.dtd">'
        note.content += '<en-note>%s<br/>' % tweet['text'].encode('utf-8')
        note.content += '</en-note>'

        # Set tag
        note.tagNames = ["#twitter"]

        # Set attributes
        noteAttributes = Types.NoteAttributes()
        noteAttributes.sourceURL = "https://twitter.com/statuses/%s" % tweet['id']
        note.attributes = noteAttributes

        # Save to Evernote
        created_note = note_store.createNote(note)

        # Unsave it on twitter
        twitterApi.destroy_favorite(tweet['id'])

        print("Processed %s" % tweet['id'])
    except:
        print("Failed to process %s" % tweet['id'])
