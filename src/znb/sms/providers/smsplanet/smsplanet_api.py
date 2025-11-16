import requests

from znb.sms.exceptions import SmsSendingException


class SMSPlanet_API:
    """
    Klasa do komunikacji z SMS Planet.

    https://smsplanet.pl/
    https://smsplanet.pl/doc/slate/index.html#introduction
    """

    def __init__(self, token: str, from_field: str = "TEST"):
        self.url = "https://api2.smsplanet.pl/sms"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                        "Authorization": f"Bearer {token}"}
        self.from_field = from_field

    def send(
        self,
        contacts: list[str],
        message: str,
        report_name: str = "",
        demo: bool = False
    ) -> str:
        data = {
            'from': self.from_field,
            'to': contacts,
            'msg': message,
            'name': report_name,
            'test': 1 if demo else 0,
        }
        r = requests.post(self.url, data=data, headers=self.headers)
        status_code = r.status_code
        response = r.json()
        message_id = response.get("messageId")
        error_code = response.get("errorCode")
        error_msg = response.get("errorMsg")
        if status_code != 200 or (not message_id) or error_code or error_msg:
            raise SmsSendingException(
                f"Błąd {error_code}: {error_msg} (HTTP code {status_code}), "
                f"messageId: {message_id}. Data: {data}, headers: {self.headers}"
            )
        return message_id
