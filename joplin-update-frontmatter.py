#!/usr/bin/python3

##
# joplin-update-frontmatter.py
# 
# When Joplin exports files as MD (for use in Obsidian) it does not include Tags
# Obsidian stores Tags in a block at the front of the MD files called FrontMatter (https://help.obsidian.md/Advanced+topics/YAML+front+matter)
# This script is designed to create a YAML FrontMatter block, within each Joplin note, so that on export Obsidian notes will have Tags
# Additional fields can be added to the FrontMatter, but Obsidian only recognizes "aliases", "tags", and "cssclass"
# 

## Joplin API Documentation (https://joplinapp.org/api/references/rest_api/):
# curl http://localhost:41184/notes?token=YOURBIGTOKEN
# Get a specific note body, created times, updated times:
#   curl "http://localhost:41184/notes/NOTEID/?fields=body,created_time,user_created_time,updated_time,user_updated_time&token=YOURBIGTOKEN"
# Get a specific notes tags:
#   curl "http://localhost:41184/notes/NOTEID/tags?token=YOURBIGTOKEN"

# Program creates YAML FrontMatter in the following format:
# ---
# joplin-id: 039c4d1ad9c4403baad10acda1b48a90
# created-at: 2012-11-10T09:25:49-0800
# modified-at: 2012-11-10T09:29:35-0800
# tags: [Note, Multi-Word-Tag, lower-case-tag]
# ---

import json
from datetime import datetime, timezone
import random
import requests

# Debug booleans
# DEBUG will just print FrontMatter without changing the Joplin notes at all, includes title of the note
# DEBUGTAGS will print FrontMatter of first note with Tags and then exit the program (needs DEBUG to work)
DEBUG = True
DEBUGTAGS = True

# CHANGE THE SETTING BELOW TO YOUR BIG TOKEN (See Joplin API documentation)
TOKEN = "bdc823c9c97fd162134e5b63dea151a92648f32fa3963b0d65f22e995b59f5a8e176582d6ad8ece2c065166758a435f4931f8523842f28f24c849e042d0a6040"

# This doesn't need changing for most
NOTES_ENDPOINT = "http://localhost:41184/notes"

def get_note_metadata(noteid):
    # Return the metadata desired, valid fields are:  
    # id                      text  
    # parent_id               text  ID of the notebook that contains this note. Change this ID to move the note to a different notebook.
    # title                   text  The note title.
    # body                    text  The note body, in Markdown. May also contain HTML.
    # created_time            int   When the note was created.
    # updated_time            int   When the note was last updated.
    # is_conflict             int   Tells whether the note is a conflict or not.
    # latitude                numeric 
    # longitude               numeric 
    # altitude                numeric 
    # author                  text  
    # source_url              text  The full URL where the note comes from.
    # is_todo                 int   Tells whether this note is a todo or not.
    # todo_due                int   When the todo is due. An alarm will be triggered on that date.
    # todo_completed          int   Tells whether todo is completed or not. This is a timestamp in milliseconds.
    # source                  text  
    # source_application      text  
    # application_data        text  
    # order                   numeric 
    # user_created_time       int   When the note was created. It may differ from created_time as it can be manually set by the user.
    # user_updated_time       int   When the note was last updated. It may differ from updated_time as it can be manually set by the user.
    # encryption_cipher_text  text  
    # encryption_applied      int 
    # markup_language         int 
    # is_shared               int 
    # body_html               text  Note body, in HTML format
    # base_url                text  If body_html is provided and contains relative URLs, provide the base_url parameter too so that all the URLs can be converted to absolute ones. The base URL is basically where the HTML was fetched from, minus the query (everything after the '?'). For example if the original page was https://stackoverflow.com/search?q=%5Bjava%5D+test, the base URL is https://stackoverflow.com/search.
    # image_data_url          text  An image to attach to the note, in Data URL format.
    # crop_rect               text  If an image is provided, you can also specify an optional rectangle that will be used to crop the image. In format { x: x, y: y, width: width, height: height }
    return requests.get('{}/{}/?fields=body,title,user_created_time,user_updated_time&token={}'.format(NOTES_ENDPOINT, noteid, TOKEN))

def get_note_tags(noteid):
    note_tags = []
    res = requests.get('{}/{}/tags?token={}'.format(NOTES_ENDPOINT, noteid, TOKEN)).json()["items"]
    for tag in res:
        note_tags.append((tag.get("title")))
    return note_tags

def get_all_note_ids(page=0):
    note_ids = []
    res = requests.get('{}?order_by=title&limit=100&page={}&token={}'.format(NOTES_ENDPOINT, page, TOKEN))
    notes = res.json()["items"]
    for note in notes:
        note_ids.append((note.get("id"), note.get("title")))
    if res.json()["has_more"]:
        note_ids.extend(get_all_note_ids(page + 1))
    return note_ids

note_ids = []
note_metadata = []
tag_names = []
new_body = ''
new_tag_list = ''
note_ids = get_all_note_ids()
for note in note_ids:
    frontMatter = ''
    note_metadata = get_note_metadata(note[0])
    tag_names = get_note_tags(note[0])
    if DEBUG:
       # Print the Title of the note
       print(note_metadata.json()["title"])
    # Establish frontmatter block
    frontMatter = frontMatter + '---\n'
    frontMatter = frontMatter + 'joplin-id: ' + note[0] + '\n'
    # Convert millisecond epoch time to formatted date and time
    utc_time = datetime.fromtimestamp(note_metadata.json()["user_created_time"]/1000, timezone.utc)
    local_time = utc_time.astimezone()
    frontMatter = frontMatter + 'created-at: ' + local_time.strftime("%Y-%m-%dT%H:%M:%S%z") + '\n'
    # Convert millisecond epoch time to formatted date and time
    utc_time = datetime.fromtimestamp(note_metadata.json()["user_updated_time"]/1000, timezone.utc)
    local_time = utc_time.astimezone()
    frontMatter = frontMatter + 'modified-at: ' + local_time.strftime("%Y-%m-%dT%H:%M:%S%z") + '\n'
    if tag_names:
       # Obsidian does not recognize tags with spaces, so they must be converted to '-'
       new_tag_list = [sub.replace(' ', '-') for sub in tag_names]
       frontMatter = frontMatter + 'tags: [' + ", ".join(new_tag_list) + ']\n'
       if DEBUGTAGS:
          # Print the FrontMatter for the first note with Tags, then exits, requires DEBUG true as well
          frontMatter = frontMatter + '---' + '\n'
          print(frontMatter)
          break
    # End frontmatter block
    frontMatter = frontMatter + '---' + '\n'
    if DEBUG:
       # Print the FrontMatter and do not update the note in the Joplin database
       print(frontMatter)
    else:
       new_body = frontMatter + note_metadata.json()["body"]
       if new_body is not None:
          # Only update if the new body is not empty (just a safeguard)
          requests.put('{}/{}?token={}'.format(NOTES_ENDPOINT, note[0], TOKEN),
                       data='{{ "body" : {} }}'.format(json.dumps(new_body)))
