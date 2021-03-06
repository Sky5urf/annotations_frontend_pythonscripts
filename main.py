from camomile import Camomile
import json
import sys, os


def fixit(file):  # Fixes the extra extension
    return file.split('.')[0:-1]


def correct_extensions():  # Rename the uppercase extensions into lowercase one
    for root, dirs, files in os.walk('/home/mrim/huchetn/public/nmedia'):
        for name in files:
            a = os.path.join(root, name)
            if not a.split('.')[-1].islower():
                os.rename(a, ''.join(a.split('.')[0:-1]) + '.' + a.split('.')[-1].lower())


def correct_description(data):
    video_types = ['mp4']
    images_types = ['jpeg', 'jpg', 'png']
    data['extension'] = data['type']
    if data['extension'] in video_types:
        data['type'] = 'video'
    elif data['extension'] in images_types:
        data['type'] = 'image'


def build_db(path):
    corpus_actif = None

    # Open the file
    print(' Reading media file...')
    with open(path + '/Medias.txt', 'r') as f:
        read_data = f.read()  # Get the string

    json_data = json.loads(read_data)  # And load into json object the data

    print(' Fetching corpora...')
    corpora = client.getCorpora()  # Get the corpora
    for corpus in corpora:  # For each corpus
        if corpus.name == 'test':  # If its name is test
            corpus_actif = corpus  # We assign it to corpus active

    if corpus_actif is not None:  # If the corpus exists
        client.deleteCorpus(corpus_actif._id)  # We have to delete it

    corpus_actif = client.createCorpus('test')  # And recreate it, to clear it

    print(' Corpus identifier: ' + str(corpus_actif._id))
    media = []  # List of medium

    print(' Constructing media list...')
    # For each object in the json object
    for index in json_data:
        objet = json_data[index]  # We get the object
        description = objet['description']
        description['id'] = index
        correct_description(objet['description'])
        media.append({  # We append to the list the object correctly created
            'name': objet['url'] + '.' + objet['description']['extension'],
            'description': objet['description'],
            'url': objet['url']
        })

    print(' Creating the media on the server...')
    media_with_id = client.createMedia(corpus_actif._id, media)  # Yay, we have the media ids

    print(' Building indexes...')
    indexes = {}
    # We have to build an associative map
    for medium in media_with_id:
        indexes[medium['description']['id']] = medium._id

    #print(json.dumps(indexes, sort_keys=True, indent=2, separators=(',', ': ')))

    print(' Reading objects file...')
    # Open the file
    with open(path + '/Objects.txt', 'r') as f:
        read_data = f.read()  # Get the string
    objets = json.loads(read_data)  # Load the data into a json object

    print(' Replacing media identifiers...')
    for index in objets:  # For each object
        objet = objets[index]
        for medium in range(0, len(objet['media'])):  # We iterate over each medium referenced
            objet['media'][medium] = indexes[objet['media'][medium]]  # We replace it with the indexed value

    print(' Writing objects into Objects.txt...')
    # Output the file corrected
    # with open('Objects.txt', 'w') as f:
    #     f.write(json.dumps(objets, sort_keys=True, indent=2, separators=(',', ': ')))

    print(' Reading endroits file...')
    with open(path + '/Endroits.txt', 'r') as f:
        read_data = f.read()  # Get the string
    endroits = json.loads(read_data)  # Load the data into a json object

    print(' Creating metadata on the server...')
    # Adds the metadata into the server
    client.setCorpusMetadata(corpus_actif._id, {'objet': objets, 'endroit': endroits})

    print(' Done.')


# Login into Camomile
print(' Connecting...')
client = Camomile('http://localhost:3000')
print(' Logging in...')
client.login('root', 'admin')

if __name__ == "__main__":
    build_db(sys.argv[1])
    #correct_extensions()

print(' Logging out...')
client.logout()  # Logout of the camomile server
