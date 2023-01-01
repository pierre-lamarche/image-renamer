import os
import argparse
import re
import exifread
from time import strptime, strftime
import shutil
from tqdm import tqdm

def metadata_extractor(image):
    try:
        with open(image, mode='rb') as f:
            tags = exifread.process_file(f, details=True)
        if 'EXIF DateTimeOriginal' in tags:
            temps = strptime(tags['EXIF DateTimeOriginal'].printable, "%Y:%m:%d %H:%M:%S")
            date_formatee = strftime("%Y-%m-%d", temps)
        extension = re.match(r'.*\.(.*)$', image).group(1)
        res = {'fichier': image, 'temps': temps, 'date_formatee': date_formatee, 'extension': extension}
    except Exception as e:
        print(f"Problème pour le fichier {image}: {e}")
        res = None
    return res

def image_renamer(dossier_images, dossier_sortie, base_nom):
    liste_images = [f"{dossier_images}/{fichier}" for fichier in os.listdir(dossier_images) if
                    os.path.isfile(os.path.join(dossier_images, fichier)) and
                    re.match(r'.*\.(.*)$', fichier).group(1).lower() in ['png', 'jpeg', 'jpg']]

    images = {fichier: metadata_extractor(fichier) for fichier in liste_images if metadata_extractor(fichier) is not None}
    images_ordonnees = {k: v for k, v in sorted({image: images[image]['temps'] for image in images}.items(),
                                                key=lambda x: x[1])}
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)

    date_retard = None
    increment = 1
    pbar = tqdm(total=len(images))
    for image in images_ordonnees:
        if date_retard and date_retard == images[image]['date_formatee']:
            increment += 1
        else:
            increment = 1
        shutil.copy(image,
                    f"{dossier_sortie}/{images[image]['date_formatee']}_{base_nom}_{str(increment).zfill(3)}.{images[image]['extension']}")
        date_retard = images[image]['date_formatee']
        pbar.update(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dossier_images', type=str, help='Dossier contenant les images à renommer')
    parser.add_argument('-o', '--output', dest='dossier_sortie', type=str, help='Dossier de sortie des données',
                        default=None)
    parser.add_argument('--base', dest='base_nom', default='image', type=str, help='Radical du nom de fichier')
    args = parser.parse_args()

    if not args.dossier_sortie:
        dossier_sortie = args.dossier_images
    else:
        dossier_sortie = args.dossier_sortie
    image_renamer(args.dossier_images, dossier_sortie, args.base_nom)
