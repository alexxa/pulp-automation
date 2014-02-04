from pulp_auto.item import Item, Request
#from pulp_auto.pulp import Request
from . import path_join
from pulp import normalize_url, pulp_path

import requests

class Upload(Item):
    path = '/content/uploads/'
    required_data_keys = ['upload_id']
    relevant_data_keys = ['upload_id', 'unit_type_id', 'unit_key', 'unit_metadata']

    def reset(self, value=0):
        '''reset self.offset to given value'''
        self.offset = value

    def __init__(self, data={}):
        super(Upload, self).__init__(data=data)
        self.reset()

    @property
    def id(self):
        #print self.data
        return self.data['upload_id']

    @id.setter
    def id(self, value):
        self.data['upload_id'] = value
        

    # from_response inherited from Item
    # RUD methods inherited from Item

    @classmethod
    def create(cls, pulp, data):
        '''create an upload in pulp; upload.data is based on pulp response'''
        request = Request('POST', cls.path, data=None)
        print 'POST request: ', request
        upload = cls.from_response(pulp.send(request))
        # augment data as r
        upload |= data
        print 'Upload: ', upload
        return upload

    def chunk(self, pulp, data):
        '''upload a chunk of data'''
        with pulp.asserting(True), pulp.async(False):
            # if async is True, pulp sends data in batch mode
            # watch out for request ordering
            request = self.request('PUT', path=str(self.offset), data=data, headers={'Content-Type': 'application/octet-stream'})
            print 'Request: ', request
            print "Response: ", pulp.send(request)
            pulp.send(request)
        # augment self.offset accordingly
        self.reset(self.offset + len(data))

    @classmethod
    def from_fd(cls, pulp, fd, create_data, chunk_size=524288):
        '''upload data from a file descriptor; return finished upload item'''
        upload = cls.create(pulp, create_data)
        while True:
            chunk = fd.read(chunk_size)
            if not chunk:
                break
            upload.chunk(pulp, chunk)
        return upload

def batch_upload_files(pulp, details=[], timeout=3600):
    '''create upload requests for each detail item and perform the uploads
    returns list of finished Uploads
    details = [(filename, create_data),...]
    '''
    import gevent
    
    def upload_job(pulp, detail):
        '''upload single file detail'''
        from gevent import monkey
        monkey.patch_all()
        with open(detail[0]) as fd:
            upload = Upload.from_fd(pulp, fd, detail[1])
        return upload

    jobs = map(
        lambda detail: gevent.spawn(upload_job(pulp, detail)),
        details
    )

    try:
        gevent.joinall(jobs, timeout=timeout)
    finally:
        # return list of finished uploads
        return [job.value for job in jobs]


