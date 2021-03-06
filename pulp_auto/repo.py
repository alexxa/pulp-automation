import item, json
from pulp_auto import (Request, )
from . import (path_join, format_response)


class Repo(item.Item):
    relevant_data_keys = ['id', 'display_name', 'description', 'notes']
    path = '/repositories/'


    def importer_config_update(
        self,
        pulp,
        data
    ):
        path = ""
        return pulp.send(self.request('PUT', path=path, data=data))

    def associate_importer(
        self,
        pulp,
        data,
        path='/importers/'
    ):
        return pulp.send(self.request('POST', path=path, data=data))

    def associate_distributor(
        self,
        pulp,
        data,
        path='/distributors/'
    ):
        return pulp.send(self.request('POST', path=path, data=data))

    def sync(
        self,
        pulp,
        data={
            'override_config': {
            }
        },
        path='/actions/sync/'
    ):
        return pulp.send(self.request('POST', path=path, data=data))

    def publish(
        self,
        pulp,
        data,
        path='/actions/publish/'
    ):
        return pulp.send(self.request('POST', path=path, data=data))

    def list_importers(
        self,
        pulp,
    ):
        path = path_join(self.path, self.id, Importer.path)
        with pulp.asserting(True):
            response = pulp.send(self.request('GET', path=path)).json()
        return map(lambda x: Importer(data=x, path_prefix=path_join(self.path, self.id)), response)

    def list_distributors(
        self,
        pulp,
    ):
        path = path_join(self.path, self.id, Distributor.path)
        with pulp.asserting(True):
            response = pulp.send(self.request('GET', path=path)).json()
        return map(lambda x: Distributor(data=x, path_prefix=path_join(self.path, self.id)), response)

    def get_importer(
        self,
        pulp,
        id,
    ):
        path = path_join(self.path, self.id, Importer.path)
        with pulp.asserting(True):
            return Importer.from_response(pulp.send(self.request('GET', path=path)))

    def get_distributor(
        self,
        pulp,
        id,
    ):
        path = path_join(self.path, self.id, Distributor.path)
        with pulp.asserting(True):
            return Distributor.from_response(pulp.send(self.request('GET', path=path)))

    def copy(
        self,
        pulp,
        source_repo_id,
        data={
            'override_config': {
                'resolve_dependencies': True,
                'recursive': True
            }
        },
        path='/actions/associate/'
    ):
        data.update({'source_repo_id': source_repo_id})
        return pulp.send(self.request('POST', path=path, data=data))


    def unassociate_units(
        self,
        pulp,
        data,
        path='/actions/unassociate/'
    ):
        # example of criteria usage 
        # {"criteria": {"type_ids": ["puppet_module"], "filters": {"unit": {"name": "tomcat7_rhel"}}}}
        return pulp.send(self.request('POST', path=path, data=data))


    def within_repo_search(
        self,
        pulp,
        data,
        path='/search/units/'
    ):
        return pulp.send(self.request('POST', path=path, data=data))


class Importer(item.AssociatedItem):
    path = '/importers/'
    relevant_data_keys = ['id', 'importer_type_id', 'repo_id', 'config', 'last_sync']


class Distributor(item.AssociatedItem):
    path = '/distributors/'
    relevant_data_keys = ['id', 'distributor_type_id', 'repo_id', 'config', 'last_publish', 'auto_publish']


class Association(item.AssociatedItem):
    path = '/search/units/'


def create_yum_repo(
    pulp,
    id,
    feed,
    display_name=None,
    relative_url=None,
    http=True,
    https=True,
    **kvs
):
    '''create an almost default yum repo'''
    repo = Repo(
        {
            'id': id,
            'display_name': display_name,
            'notes': {"_repo-type": "rpm-repo"}
        }
    )
    if relative_url is None:
        relative_url = id
    with pulp.asserting(True):
        repo = Repo.from_response(repo.create(pulp))
        importer = Importer.from_response(repo.associate_importer(
            pulp,
            data={
                'importer_type_id': 'yum_importer',
                'importer_id': 'yum_importer',
                'importer_config': {
                    'feed': feed
                }
            }
        ))
        distributor = Distributor.from_response(repo.associate_distributor(
            pulp,
            data={
                'distributor_id': id + "_distributor",
                'distributor_type_id': 'yum_distributor',
                'distributor_config': {
                    'http': http,
                    'https': https,
                    'relative_url': relative_url
                },
                'auto_pubblish': False
            }
        ))
    return repo, importer, distributor


def create_puppet_repo(
    pulp,
    id,
    queries=[],
    feed='http://forge.puppetlabs.com',
    display_name=None,
    http=True,
    https=False
):

    '''create an almost default puppet repo'''
    repo = Repo(
         {
             'id': id,
             'display_name': display_name,
             'notes': {"_repo-type": "puppet-repo"}
         }
    )
    with pulp.asserting(True):
        repo = Repo.from_response(repo.create(pulp))
        importer = Importer.from_response(repo.associate_importer(
            pulp,
            data={
                'importer_type_id': 'puppet_importer',
                'importer_config': {
                    'feed': feed,
                    'queries': queries
                }
            }
        ))
        distributor = Distributor.from_response(repo.associate_distributor(
            pulp,
            data={
                'distributor_id': id + "_distributor",
                'distributor_type_id': 'puppet_distributor',
                'distributor_config': {
                    'http': http,
                    'https': https
                },
                'auto_pubblish': False
            }
        ))
    return repo, importer, distributor


SAMPLE_YUM_DISTRIBUTOR_CONFIG_DATA = {
    "distributor_id": "yum_distributor",
    "auto_publish": True,
    "distributor_type": "yum_distributor",
    "distributor_config": {
        "http": False,
        "https": True,
        "relative_url": "/repos/pulp/pulp/demo_repos/zoo/"
    }
}

SAMPLE_EXPORT_DISTRIBUTOR_CONFIG_DATA = {
    "distributor_id": "export_distributor",
    "auto_publish": False,
    "distributor_type": "export_distributor",
    "distributor_config": {
        "http": False,
        "https": True
    }
}

SAMPLE_YUM_DISTRIBUTOR_DATA = {
    "_id": {
        "$oid": "5257ef5cc805d066faef1d2f"
    },
    "_ns": "repo_distributors",
    "auto_publish": True,
    "config": {
        "http": False,
        "https": True,
        "relative_url": "/repos/pulp/pulp/demo_repos/zoo/"
    },
    "distributor_type_id": "yum_distributor",
    "id": "yum_distributor",
    "last_publish": "2013-10-11T13:06:32Z",
    "repo_id": "test_rpm_repo",
    "scheduled_publishes": [],
    "scratchpad": {}
}

SAMPLE_EXPORT_DISTRIBUTOR_DATA = {
    "_id": {
        "$oid": "5257ef5cc805d066faef1d30"
    },
    "_ns": "repo_distributors",
    "auto_publish": False,
    "config": {
    "http": False,
    "https": True
    },
    "distributor_type_id": "export_distributor",
    "id": "export_distributor",
    "last_publish": None,
    "repo_id": "test_rpm_repo",
    "scheduled_publishes": [],
    "scratchpad": None
}
