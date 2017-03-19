#########
#
# spotify_top_tracks.py
#
# Update the 'Top Hits' Playlist identified in the program
#
# 1) Get the current playlist
# 2) Create a dictionary by artist with a list of the top tracks
# 3) For each artist in the dictionary
#    a) get the current top 5 tracks
#    b) update the add list with tracks that are not in the current playlist
#    c) update the delete list with tracks that are not in the current top 5 tracks
# 4) Send the Add list (no more than 100 tracks at a time)
# 5) Send the Delete list (no more than 100 tracks at a time)

import spotipy
import spotipy.util as util
import json

Client_ID = "0a74ae28cab244c093b0e90b5e591bf6"
Client_Secret = "5e2cd784323b44cc802cd96135d06b74"

Scope = "playlist-read-private playlist-modify-private playlist-modify-public"
User_Name = "derekfields"
Redirect = "http://localhost:8080/index.html"
Playlist_URI = 'user:derekfields:playlist:4GrBozbW98JQj9tE06fzG3'
Playlist = "4GrBozbW98JQj9tE06fzG3"

Current_Playlist = "C:\\Users\\dfields\\Dropbox\\PycharmProjects\\spotify_top_tracks\\cur_playlist"

def store_current_playlist(playlist):
    """Store the playlist to persistent storage"""
    with open(Current_Playlist,"w") as pfile:
        json.dump(playlist, pfile)

def get_current_playlist():
    """Retrieve the current playlist from persistent storage"""
    with open(Current_Playlist) as pfile:
        playlist = json.load(pfile)
    return playlist

def get_spotify_playlist(spotify):
    """Retrieve the playlist from Spotify"""
    dict_artists = dict()
    offset = 0
    done = False
    while not done:
        results = spotify.user_playlist_tracks('derekfields',playlist_id=Playlist, offset = offset,
                    fields="total, offset, items(track(name,id,uri,popularity, artists(id, uri, name)))")
        # #2
        for item in results['items']:
            track = item['track']
            aname = track['artists'][0]['id']
            if aname in dict_artists:
                dict_artists[aname].append(track['id'])
            else:
                dict_artists[aname] = list()
                dict_artists[aname].append(track['id'])
        offset += len(results['items'])
        if offset >= int(results['total']):
            done = True
    return dict_artists

# 3) For each artist in the dictionary
#    a) get the current top tracks
#    c) update the add list with tracks that are not in the current playlist
#    d) update the delete list with tracks that are not in the current top tracks

def update_spotify_playlist(spotify, dict_artists):
    add_count = 0
    del_count = 0
    for artist in dict_artists.keys():
        add_list = list()
        delete_list = list()
        results = spotify.artist_top_tracks(artist)
        top_tracks = results['tracks']
        current_list = dict_artists[artist]
        for track in top_tracks:
            if track['id'] not in current_list:
                add_list.append(track['id'])
        for track in current_list:
            if track not in [ t['id'] for t in top_tracks ]:
                delete_list.append(track)

        if len(delete_list):
            spotify.user_playlist_remove_all_occurrences_of_tracks('derekfields',playlist_id=Playlist, tracks=delete_list)
            del_count += len(delete_list)
        if len(add_list):
            add_count += len(add_list)
            spotify.user_playlist_add_tracks(user='derekfields',playlist_id=Playlist, tracks=add_list)
    print("Added {} tracks, Deleted {} tracks".format(add_count, del_count))

def main():
    print("Starting Top Tracks")
    token = util.prompt_for_user_token(User_Name, Scope, Client_ID, Client_Secret, Redirect)
    if token:
        spotify = spotipy.Spotify(auth=token)
    else:
        print("Can't get token for {}".format(User_Name))
        return

    playlist = get_spotify_playlist(spotify)
    update_spotify_playlist(spotify, playlist)

if __name__ == "__main__":
    main()