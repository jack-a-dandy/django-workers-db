from django.test import TestCase
from django.core.management import call_command
from .factories import WorkerFactory
from .models import Worker
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db.models import F, Q
from .pagination import WorkersListPagination


class AuthenticationViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = "testuser"
        cls.password = "testpassword"
        User.objects.create_user(
            username=cls.username, password=cls.password, email="test@mail.com")

    def test_unathenticated_get(self):
        resp = self.client.get("/auth")
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "auth.html")

    def test_login(self):
        resp = self.client.post(
            "/auth", data={"username": self.username, "password": "12345"}, follow=True)
        self.assertTemplateUsed(resp, "auth.html")
        self.assertNotIn('_auth_user_id', self.client.session)
        resp = self.client.post(
            "/auth", data={"username": self.username, "password": self.password}, follow=True)
        self.assertRedirects(resp, reverse('list'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_authenticated_get(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get("/auth")
        self.assertRedirects(resp, "/")

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get(reverse("logout"))
        self.assertRedirects(resp, "/")
        self.assertNotIn('_auth_user_id', self.client.session)


class TreeViewTest(APITestCase):
    APINAME = 'api-tree'
    PARAM = 'depth'

    @classmethod
    def setUpTestData(cls):
        call_command('seed', workers=3, levels=3)
        cls.mid = WorkerFactory.create(head=None).id-3
        WorkerFactory.create(head=Worker.objects.get(pk=cls.mid))

    def toData(self, instance):
        return {
            'id': instance.id,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'patronymic': instance.patronymic,
            'position': instance.position.name,
            'has_subordinates': instance.has_subordinates()
        }

    def test_workers_without_head(self):
        resp = self.client.get(reverse(self.APINAME, args=(0,)))
        self.assertEqual(resp.data, [self.toData(i)
                                     for i in Worker.objects.filter(head=None)])

    def test_subordinates_depth(self):
        data = [self.toData(i) for i in Worker.objects.filter(
            head=Worker.objects.get(pk=self.mid))]
        for i in data:
            if i['has_subordinates']:
                i['subordinates'] = [self.toData(i) for i in Worker.objects.filter(
                    head=Worker.objects.get(pk=i['id']))]

        resp = self.client.get("{}?{}={}".format(
            reverse(self.APINAME, args=(self.mid,)), self.PARAM, 2))
        self.assertEqual(resp.data, data)
        resp = self.client.get("{}?{}={}".format(
            reverse(self.APINAME, args=(0,)), self.PARAM, -9))
        self.assertEqual(resp.data, [self.toData(i)
                                     for i in Worker.objects.filter(head=None)])
        resp = self.client.get("{}?{}={}".format(
            reverse(self.APINAME, args=(self.mid+1,)), self.PARAM, 8))
        self.assertEqual(resp.data, [self.toData(i) for i in Worker.objects.filter(
            head=Worker.objects.get(pk=self.mid+1))])
        resp = self.client.get("{}?{}={}".format(
            reverse(self.APINAME, args=(0,)), self.PARAM, "string"))
        self.assertEqual(resp.data, [self.toData(i)
                                     for i in Worker.objects.filter(head=None)])


class ListViewSetTest(APITestCase):
    APIPATH = "/api/list/"

    @classmethod
    def setUpTestData(cls):
        cls.username = "testuser"
        cls.password = "testpassword"
        User.objects.create_user(
            username=cls.username, password=cls.password, email="test@mail.com")
        call_command('seed', workers=10, levels=5)
        cls.mid = Worker.objects.latest('id').id-9

    def setUp(self):
        self.client.login(username=self.username, password=self.password)

    def toData(self, instance):
        return {
            'id': instance.id,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'patronymic': instance.patronymic,
            'position': instance.position.name,
            'salary': instance.salary,
            'recruitment_date': str(instance.recruitment_date),
            'photo': instance.photo.url if instance.photo else None,
            'head': instance.head.id if instance.head else None
        }

    def toBaseDict(self, instance):
        d = dict(instance)
        d['photo'] = d['photo'].split("http://testserver")[1]
        return d

    def test_put(self):
        id = self.mid+1
        data = self.toData(Worker.objects.get(id=id))
        data['photo'] = ''
        data['last_name'] = "Fisherson"
        data['salary'] = 10000000
        resp = self.client.put("{}{}/".format(self.APIPATH, id), data)
        self.assertEqual(200, resp.status_code)
        data['photo'] = None
        self.assertEqual(self.toData(Worker.objects.get(id=id)), data)

    def test_post(self):
        id = self.mid+2
        data = self.toData(Worker.objects.get(id=id))
        data['last_name'] = "TESTAMENT"
        data['salary'] = 99999999
        data['position'] = "President"
        data['head'] = ''
        data.pop('id')
        data.pop('photo')
        resp = self.client.post(self.APIPATH, data)
        self.assertEqual(201, resp.status_code)
        data['id'] = resp.data['id']
        data['photo'] = None
        data['head'] = None
        self.assertEqual(self.toData(Worker.objects.get(id=data['id'])), data)

    def test_delete(self):
        pk = WorkerFactory.create(head=None).id
        resp = self.client.delete("{}{}/".format(self.APIPATH, pk))
        self.assertEqual(204, resp.status_code)
        self.assertRaises(ObjectDoesNotExist, Worker.objects.get, id=pk)

    def test_get(self):
        id = self.mid
        resp = self.client.get("{}{}/".format(self.APIPATH, id))
        self.assertEqual(200, resp.status_code)
        resp.data['photo'] = resp.data['photo'].split("http://testserver")[1]
        self.assertEqual(resp.data, self.toData(Worker.objects.get(id=id)))

    def test_get_list(self):
        resp = self.client.get(self.APIPATH)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [
                         self.toData(i) for i in Worker.objects.all()])

    def test_ordering(self):
        resp = self.client.get("{}?ordering=last_name".format(self.APIPATH))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [
                         self.toData(i) for i in Worker.objects.order_by("last_name")])
        resp = self.client.get("{}?ordering=head".format(self.APIPATH))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [self.toData(
            i) for i in Worker.objects.order_by(F("head").asc(nulls_first=True))])
        resp = self.client.get("{}?ordering=-head".format(self.APIPATH))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [self.toData(
            i) for i in Worker.objects.order_by(F("head").desc(nulls_last=True))])
        resp = self.client.get("{}?ordering=position".format(self.APIPATH))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [
                         self.toData(i) for i in Worker.objects.order_by("position__name")])

    def test_filtering(self):
        v = Worker.objects.get(id=self.mid).salary
        resp = self.client.get("{}?salary={}".format(self.APIPATH, v))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [
                         self.toData(i) for i in Worker.objects.filter(salary=v)])
        resp = self.client.get("{}?no_head=True".format(self.APIPATH))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [
                         self.toData(i) for i in Worker.objects.filter(head=None)])
        v = Worker.objects.get(id=self.mid+1).position.name
        resp = self.client.get("{}?position={}".format(self.APIPATH, v))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [
                         self.toData(i) for i in Worker.objects.filter(position__name=v)])

    def test_searching(self):
        v = Worker.objects.get(id=self.mid).position.name[2:5]
        lookups = Q(position__name__icontains=v) | Q(first_name__icontains=v) | Q(
            last_name__icontains=v) | Q(patronymic__icontains=v)
        resp = self.client.get("{}?search={}".format(self.APIPATH, v))
        self.assertEqual([self.toBaseDict(i) for i in resp.data['results']], [
                         self.toData(i) for i in Worker.objects.filter(lookups).distinct()])

    def test_id_put(self):
        id = self.mid+4
        data = self.toData(Worker.objects.get(id=id))
        resp = self.client.put("{}{}/".format(self.APIPATH, id), data)
        self.assertEqual(400, resp.status_code)
        try:
            Worker.objects.get(id=id)
        except ObjectDoesNotExist:
            self.fail("Id mustn't be editable.")

    def test_invalid_value(self):
        id = self.mid+3
        data = self.toData(Worker.objects.get(id=id))
        data['position'] = True
        resp = self.client.put("{}{}/".format(self.APIPATH, id), data)
        self.assertEqual(400, resp.status_code)

    def test_self_referencing_head_patch(self):
        id = self.mid
        resp = self.client.patch(
            "{}{}/".format(self.APIPATH, id), {'head': id})
        self.assertEqual(400, resp.status_code)

    def test_permission(self):
        apic = APIClient()
        resp = apic.get(self.APIPATH)
        self.assertEqual(403, resp.status_code)
