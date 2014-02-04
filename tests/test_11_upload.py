import pulp_test, json
from pulp_auto import uploader, Request   
#from pulp_auto.repo import Repo



class UploadTest(pulp_test.PulpTest):
    @classmethod
    def setUpClass(cls):
        super(UploadTest, cls).setUpClass()
        
        cls.upload = uploader.Upload.create(cls.pulp, data={'upload_id': "my_upload_id"})



class SimpleUploadTest(UploadTest):

    def test_01_create_upload_request(self):
        self.assertPulpOK()
     
        
    def test_02_list__upload_request(self):
        '''test_02_list__upload_request     FIXME after a bug 1058771 will be fixed.'''
        
        with self.pulp.asserting(True):
            response =  self.pulp.send(Request('GET', uploader.Upload.path))
        data = response.json()    

        self.assertIn(self.upload.id, data['upload_ids'])    
        
    
    def test_03_get__upload_request(self):
        '''test_03_get__upload_request      FIXME after a bug 1060239 will be fixed.'''
        
        # precisely for one upload_request
        
        pass  
        
    def test_04_upload_bits(self):
        '''test_04_upload_bits    Something wrong is here'''
        #filename = '/var/cache/yum/x86_64/20/fedora/packages/protobuf-c-0.15-8.fc20.x86_64.rpm'
        filename = '/home/igulina/git/pulp-automation/tests/test_1_log_in.py'
        file_data = {}
        
        #details = ('/var/cache/yum/x86_64/20/fedora/packages/protobuf-c-0.15-8.fc20.x86_64.rpm', {"upload_id":"my_id"})
        
        
        with open(filename) as fd:
            upload = uploader.Upload.from_fd(self.pulp, fd, file_data)
        return upload
        
        pass
        
    def test_05_import_into_repo(self):
        '''test_05_import_into_repo      Fix me'''
        
        pass
                    
    def test_06_delete_upload_request(self):
        self.upload.delete(self.pulp)
        self.assertPulpOK()
   

