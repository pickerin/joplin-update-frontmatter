# joplin-update-frontmatter
Add YAML Front Matter block to all notes in Joplin

When Joplin exports files as MD (for use in Obsidian) it does not include Tags. 
Obsidian stores Tags in a block at the front of the MD files called Front Matter (https://help.obsidian.md/Advanced+topics/YAML+front+matter). 
This script is designed to create a YAML Front Matter block, within each Joplin note, so that on export Obsidian notes will have Tags. 
Additional fields can be added to the Front Matter, but Obsidian only currently recognizes "aliases", "tags", and "cssclass". 

## Joplin API Documentation (https://joplinapp.org/api/references/rest_api/):
curl http://localhost:41184/notes?token=YOURBIGTOKEN
### Get a specific note body, created times, updated times:
curl "http://localhost:41184/notes/NOTEID/?fields=body,created_time,user_created_time,updated_time,user_updated_time&token=YOURBIGTOKEN"
### Get a specific notes tags:
curl "http://localhost:41184/notes/NOTEID/tags?token=YOURBIGTOKEN"

Program creates YAML Front Matter in the following format:
```
---
joplin-id: 039c4d1ad9c4403baad10acda1b48a90
created-at: 2012-11-10T09:25:49-0800
modified-at: 2012-11-10T09:29:35-0800
tags: [Note, Multi-Word-Tag, lower-case-tag]
---
```
