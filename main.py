import requests
import time
from flask import Flask, request, url_for, session, redirect
from spotipy.oauth2 import SpotifyOAuth
import spotipy

app = Flask(__name__)
#creating a temp cookie to load faster
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
#creating a dummy key to access
app.secret_key = 'abcd123'
#authentication token 
TOKEN_INFO = 'token_info'
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    #if theres no token or 60 seconds past before token refresh ti and send it
    if not token_info:
        raise Exception("No token info")
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info

@app.route('/')
def login():
     #calling the authorization function 
    auth_url = create_spotify_oauth().get_authorize_url()
     #this will retunr the url for it 
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
     #create a new session
    session.clear()
    #requestinig the actual token under
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('get_top_artists', _external=True))

@app.route('/get_top_artists')
def get_top_artists():
    try:
        #using token to get acces
        token_info = get_token()
        #use spotipy spotify api to access the account
        sp = spotipy.Spotify(auth=token_info['access_token'])
        #api documentation for top artist only grabbing the 4
        results = sp.current_user_top_artists(limit=5)
        #lc for getting the artist in the top artiist
        top_artists = [artist['name'] for artist in results['items']]
        #printing the array of top artist
        #hometown 
        hometown=[]
        #google search api key
        API_KEY='AIzaSyD4V8kQUETVnk3d6kca1mDXKlF2NqQ1RDM'
        #search engine api key
        SEARCH_ENGINE='11f4e477034c3497b'
        towns=[]
        for x in top_artists:
            query=x+'hometown'
            url='https://www.googleapis.com/customsearch/v1'
            params={
                'q': query,
                'key':API_KEY,
                'cx':SEARCH_ENGINE
        }
            response=requests.get(url,params=params)
            result=response.json()
            if 'items' in result and len(result['items']) > 0:
                hometown.append(result['items'][0]['snippet'])
        return hometown
    except Exception as e:
        print("Error:", e)
        return []
        


app.config['SERVER_NAME'] = 'previewforflask.vercel.app'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id='a8dd8b7decf845e1b7becdc8dbb909e3',
        client_secret="c6cfafd242384321b9c4aa81b58fb5fd",
        redirect_uri='https://previewforflask.vercel.app/redirect',
        scope='user-top-read'
    )


 

if __name__ == '__main__':
    #fix the host and port issues so it works  on other users computers
    #deploy on the interentt
    #do a gitpull a run locally
    #implement database logic mongodb or sqL
    app.run(debug=True, port=5000, host='0.0.0.0')
