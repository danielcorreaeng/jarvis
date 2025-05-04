import time
import sys,os
import subprocess
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# Add OAuth2 access token here.
# You can generate one for yourself in the App Console.
# See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>
TOKEN = ''
LOCALFILE = ''
REMOTEFILE = ''
dbx = ''

# Uploads contents of LOCALFILE to Dropbox
def backup():
    with open(LOCALFILE, 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading " + LOCALFILE)
        try:
            dbx.files_upload(f.read(), REMOTEFILE, mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().reason.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()

# Restore the local and Dropbox files to a certain revision
def restore(rev=None):
    # Restore the file on Dropbox to a certain revision
    print("Restoring " + REMOTEFILE + " to revision " + rev + " on Dropbox...")
    dbx.files_restore(REMOTEFILE, rev)

    # Download the specific revision of the file at REMOTEFILE to LOCALFILE
    print("Downloading current " + REMOTEFILE + " from Dropbox, overwriting " + LOCALFILE + "...")
    #dbx.files_download_to_file(LOCALFILE, REMOTEFILE, rev)
    
    with open(LOCALFILE, "wb") as f:
        metadata, res = dbx.files_download(REMOTEFILE, rev)
        f.write(res.content)

# Look at all of the available revisions on Dropbox, and return the oldest one
def select_revision():
    # Get the revisions for a file (and sort by the datetime object, "server_modified")
    print("Finding available revisions on Dropbox...")
    entries = dbx.files_list_revisions(REMOTEFILE, limit=30).entries
    revisions = sorted(entries, key=lambda entry: entry.server_modified)

    for revision in revisions:
        print(revision.rev, revision.server_modified)

    # Return the oldest revision (first entry, because revisions was sorted oldest:newest)
    #return revisions[0].rev
    return revisions[-1].rev

def check_remote_file():
    try:
        dbx.files_get_metadata(REMOTEFILE)
        return True
    except:
        sys.exit("ERROR: File dont found.")

def Main(param): 
	'''Integration with Dropbox. Parameters: <save/load> <localfile> <remotefile> <token>'''

	global TOKEN
	global LOCALFILE
	global REMOTEFILE
	global dbx

	localoption='save'

	if(len(param)==4):
		localoption = param[0]
		LOCALFILE = param[1]
		REMOTEFILE = param[2]
		TOKEN = param[3]
	else:
		sys.exit("ERROR: insufficient parameters.")

	# Check for an access token
	if (len(TOKEN) == 0):
		sys.exit("ERROR: Looks like you didn't add your access token. "
			"Open up backup-and-restore-example.py in a text editor and "
			"paste in your token in line 14.")

	# Create an instance of a Dropbox class, which can make requests to the API.
	print("Creating a Dropbox object...")
	with dropbox.Dropbox(TOKEN) as dbx:

		# Check that the access token is valid
		try:
			dbx.users_get_current_account()
		except AuthError:
			sys.exit("ERROR: Invalid access token; try re-generating an "
				"access token from the app console on the web.")

		if(localoption == 'upload'):
			# Create a backup of the current settings file
			backup()
		elif(localoption == 'download'):
            
			check_remote_file()
            
			# Restore the local and Dropbox files to a certain revision
			to_rev = select_revision()
			restore(to_rev)

		print("Done!")
	
if __name__ == '__main__':
	if(len(sys.argv) > 1):
		if(sys.argv[len(sys.argv)-1] == '-h' or sys.argv[len(sys.argv)-1] == 'help'):
			print(Main.__doc__)
			sys.exit()

	Main(sys.argv[1:])
	
	#param = ' '.join(sys.argv[1:])
	#print('param ' + param)
