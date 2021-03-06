import pulp_test, json, pprint, pulp_auto
from pulp_auto.repo import create_yum_repo, Repo
from pulp_auto.task import Task
from pulp_auto.units import Orphans, UnitFactory, RpmOrphan, PackageGroupOrphan, PackageCategoryOrphan, ErratumOrphan, DistributionOrphan, DrpmOrphan, SrpmOrphan, YumRepoMetadataFileOrphan,PuppetModuleOrphan, IsoOrphan
from . import ROLES

def setUpModule():
    pass

@pulp_test.requires_any('repos', lambda repo: repo.type == 'rpm')
class SimpleOrphanTest(pulp_test.PulpTest):

    @classmethod
    def setUpClass(cls):
        super(SimpleOrphanTest, cls).setUpClass()
        # prepare orphans by syncing and deleting a repo
        # make sure the repo is gone
        repo_config = [repo for repo in ROLES.repos if repo.type == 'rpm'][0]
        repo = Repo(repo_config)
        repo.delete(cls.pulp)
        # create and sync repo
        cls.repo, _, _ = create_yum_repo(cls.pulp, **repo_config)
        sync_task = Task.from_response(cls.repo.sync(cls.pulp))[0]
        sync_task.wait(cls.pulp)
        # this is where orphans appear
        cls.repo.delete(cls.pulp)

    def test_00_get_orphan_info(self):
        Orphans.info(self.pulp)
        self.assertPulpOK()

    def test_01_orphan_info_data_integrity(self):
        info = Orphans.info(self.pulp)
        orphans = Orphans.get(self.pulp)
        self.assertPulpOK()
        for orphan_type_name in orphans.keys():
            # reported count info is the same as the orphans counted
            self.assertEqual(len(orphans[orphan_type_name]), info[orphan_type_name]['count'])
            orphan_type = UnitFactory.type_map.orphans[orphan_type_name]
            # '_href' is correct
            self.assertEqual(pulp_auto.path_join(pulp_auto.path, orphan_type.path), info[orphan_type_name]['_href'])
            # all orphans are of the same type
            for orphan in orphans[orphan_type_name]:
                self.assertTrue(isinstance(orphan, orphan_type), "different type: %s, %s" % (orphan_type_name, orphan.type_id))

    def test_02_delete_single_orphan(self):
        old_info = Orphans.info(self.pulp)
        rpm_orphans = RpmOrphan.list(self.pulp)
        assert rpm_orphans, "No orphans found; there might be other 'Zoo' repos in %s" % self.pulp
        rpm_orphans[0].delete(self.pulp)
        del rpm_orphans[0]
        self.assertPulpOK()
        new_info = Orphans.info(self.pulp)
        self.assertEqual(old_info['rpm']['count'], new_info['rpm']['count'] + 1)
        self.assertEqual(
            sorted(map(lambda x: x.data['name'], rpm_orphans)),
            sorted(map(lambda x: x.data['name'], RpmOrphan.list(self.pulp)))
        )

    def test_03_delete_orphans(self):
        delete_response = Orphans.delete(self.pulp)
        self.assertPulpOK()
        delete_task = Task.from_response(delete_response)
        delete_task.wait(self.pulp)
        info = Orphans.info(self.pulp)
        orphans = Orphans.get(self.pulp)
        self.assertPulpOK()
        for orphan_type_name in info.keys():
            self.assertEqual(len(orphans[orphan_type_name]), info[orphan_type_name]['count'])
            self.assertEqual(orphans[orphan_type_name], [])

    def test_04_create_orphans_again(self):
        # first a repo created, synced and then deleted
        self.setUpClass()

    def test_05_delete_orphan_rpm(self):
        RpmOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_06_delete_orphan_pkggroup(self):
        PackageGroupOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_07_delete_orphan_pkgcategory(self):
        PackageCategoryOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_08_delete_orphan_erratum(self):
        ErratumOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_09_delete_orphan_distribution(self):
        DistributionOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_09_delete_orphan_drpm(self):
        DrpmOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_09_delete_orphan_srpm(self):
        SrpmOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_09_delete_orphan_yum_repo_metadata(self):
        YumRepoMetadataFileOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_10_delete_orphan_puppet_module(self):
        PuppetModuleOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    def test_10_delete_orphan_ISO(self):
        IsoOrphan.delete_all(self.pulp)
        self.assertPulpOK()

    @classmethod
    def tearDownClass(cls):
        pass
