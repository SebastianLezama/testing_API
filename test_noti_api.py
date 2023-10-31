
import requests
import time
from dotenv import load_dotenv
import os


load_dotenv()
base_url = "http://44.195.141.130:8000/"
get_services = "api/v1/services"
get_agents = "api/v1/agents"
get_phone_number = "api/v1/phone_numbers/"
get_sms_list = "api/v1/sms"
post_create_sms = "api/v1/sms"


def create_session():
    api_key = os.environ['TOKEN_API']
    s = requests.Session()
    s.headers.update({
        "Accept": "*/*",
        "Authorization": "Bearer " + api_key
    })

    def api_calls(r, *args, **kwargs):
        req_remaining = r.headers['X-Ratelimit-Remaining']
        if int(req_remaining) <= 5:
            print("API request limit, sleeping")
            time.sleep(30)

    s.hooks["response"] = api_calls

    return s


class TestNotiApi:
    def setup_method(self, method):
        self.session = create_session()
        self.phone_number = os.environ['PHONE_NUMBER']

    def test_create_show_sms(self):
        sms_message = {"recipient": 1140737970, "message": "Hello mundo!"}
        post_response = self.session.post(
            base_url + post_create_sms, json=sms_message)
        post_response_time = int(str(post_response.elapsed).split('.')[1])/1000
        assert post_response.status_code == 200
        assert post_response_time <= 500

        sms_id = post_response.json()['data']['sms_id']
        get_show_sms_by_id = f'api/v1/sms/{sms_id}'
        get_response = self.session.get(
            f'{base_url}{get_show_sms_by_id}')
        get_response_time = int(str(get_response.elapsed).split('.')[1])/1000
        assert get_response.status_code == 200
        assert get_response_time <= 500

    def test_get_services(self):
        response = self.session.get(
            f'{base_url}{get_services}')
        get_response_time = int(str(response.elapsed).split('.')[1])/1000

        assert response.status_code == 202
        assert get_response_time <= 500

    def test_get_agents(self):
        response = self.session.get(
            f'{base_url}{get_agents}')
        get_response_time = int(str(response.elapsed).split('.')[1])/1000

        assert response.status_code == 200
        assert get_response_time <= 500

    def test_get_sms_list(self):
        response = self.session.get(
            f'{base_url}{get_sms_list}')
        get_response_time = int(str(response.elapsed).split('.')[1])/1000

        assert response.status_code == 200
        assert get_response_time <= 500

    def test_get_phone_number(self):
        response = self.session.get(
            f'{base_url}{get_phone_number}{self.phone_number}')
        get_response_time = int(str(response.elapsed).split('.')[1])/1000

        assert response.status_code == 200
        assert get_response_time <= 500

        # TEST ERROR MESSAGES

    def test_create_sms_error(self):
        sms_message = {"recipient": "4321", "message": "Hello mundo!"}
        response = self.session.post(
            base_url + post_create_sms, json=sms_message)
        post_response_time = int(str(response.elapsed).split('.')[1])/1000
        status = response.json()['status']

        # status_code TBD
        assert response.status_code == 200
        assert post_response_time <= 500
        # status TBD
        assert status == "success"

    def test_show_sms_error(self):
        sms_id = 78989899898989
        get_show_sms_by_id = f'api/v1/sms/{sms_id}'
        response = self.session.get(
            f'{base_url}{get_show_sms_by_id}')
        get_response_time = int(str(response.elapsed).split('.')[1])/1000

        assert response.status_code == 404
        assert get_response_time <= 500

    def test_get_phone_number_error(self):
        phone_number = "444444"
        response = self.session.get(
            f'{base_url}{get_phone_number}{phone_number}')
        get_response_time = int(str(response.elapsed).split('.')[1])/1000
        status = response.json()['status']
        # status_code TBD
        assert response.status_code == 200
        assert get_response_time <= 500
        assert status == "error"
