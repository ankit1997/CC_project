import os
import traceback
import numpy as np
from PIL import Image

class ClientHelper:
    def __init__(self):
        self.TEXT_EXTENSIONS = ['.txt', '.py', '.c', '.cpp', '.java']
        self.IMG_EXTENSIONS = ['.jpg', '.png', '.jpeg']
        self.dirname = None

    def init(self, json):
        dirname = json['dirname']
        storage = json['storage']
        # os.makedirs(dirname, exist_ok=True)
        if not os.path.isdir(dirname):
            os.mkdir(dirname, 700)
        self.dirname = dirname

        # make storage data file
        with open(os.path.join(dirname, '.storage'), 'w') as file:
            file.write(str(storage))

    @property
    def storage(self):
        with open(os.path.join(self.dirname, '.storage')) as file:
            try:
                store = float(file.read().strip())
            except:
                print("Storage value in client is not a valid number.")
                store = 0
        return store

    def get_file(self, json):
        fname = json['fname']
        print("Getting {}".format(fname))

        fname = os.path.join(self.dirname, fname)
        extension = os.path.splitext(os.path.basename(fname))[1]

        res = {'success': True, 'error': '', 'fname': fname, 'fdata': ''}
        if os.path.isfile(fname):
            if extension in self.TEXT_EXTENSIONS:
                res['fdata'] = self._get_text_file(fname)
            elif extension in self.IMG_EXTENSIONS:
                res['fdata'] = self._get_img_file(fname)
            else:
                res['success'] = False
                res['error'] = 'File format {} not supported...yet!'.format(extension)
        else:
            res['success'] = False
            res['error'] = 'File {} not found.'.format(fname)

        print("Done.")
        return res

    def save_file(self, json):
        print("Saving file...")

        fdata = json['fdata']
        fname = os.path.basename(json['fname'])
        extension = os.path.splitext(fname)[1]
        fname = os.path.join(self.dirname, fname)

        res = {'success': False, 'error': '', 'meta': None}

        # Check if file already exists
        if os.path.isfile(fname):
            res['meta'] = 'File already existed, overwritten in client.'

        if extension in self.TEXT_EXTENSIONS:
            res['success'] = self._save_text_file(fname, fdata)
        elif extension in self.IMG_EXTENSIONS:
            res['success'] = self._save_img_file(fname, fdata)
        else:
            res['error': 'File format {} not supported!'.format(extension)]

        return res

    def test(self, json):
        try:
            import tester.tester as tester
        except ImportError:
            return {'result': "ERROR: No tester.py found. First send the tester file."}

        fname = os.path.basename(json['fname'])
        fname = os.path.join(self.dirname, fname)

        inputFile = os.path.basename(json['inputFile'])
        inputFile = os.path.join(self.dirname, inputFile)
        
        outputFile = os.path.basename(json['outputFile'])
        outputFile = os.path.join(self.dirname, outputFile)

        # Save files
        with open(fname, 'w') as f:
            f.write(json['fdata'])
        with open(inputFile, 'w') as f:
            f.write(json['inputData'])
        with open(outputFile, 'w') as f:
            f.write(json['outputData'])

        return tester.test(fname, inputFile, outputFile)

    def _save_text_file(self, fname, data):
        try:
            with open(fname, 'w') as file:
                file.write(data)
            return True
        except:
            print(traceback.format_exc())
        return False

    def _save_img_file(self, fname, data):
        '''
            Args:
            fname : Name of the file
            data : Binary image data
        '''
        try:
            img = Image.fromarray(np.asarray(data, dtype=np.uint8))
            img.save(fname)
            return True
        except:
            print(traceback.format_exc())
        return False

    def _get_text_file(self, fname):
        return open(fname).read()

    def _get_img_file(self, fname):
        return np.array(Image.open(fname)).tolist()
