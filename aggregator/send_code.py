import operator
import random
from datetime import datetime

from aggregator.custom_api_exeptions import Http429, Http204, Http400
from aggregator.redis_settings import REDIS
from notifications.sms import send_sms


class SendCode:
    def sort_codes(self, user_id):
        codes_in_binary = REDIS.hgetall(user_id)
        sorted_codes = sorted(codes_in_binary.items(), key=operator.itemgetter(1), reverse=True)
        codes = []
        for x in sorted_codes:
            codes.append(
                [x[0].decode("utf-8"), datetime.strptime(x[1].decode("utf-8"), '%Y-%m-%d %H:%M:%S.%f')]
            )
        return codes

    def get_last_code(self, sorted_codes):
        last_code = {}
        if sorted_codes:
            code = sorted_codes[0][0]
            time = sorted_codes[0][1]
            last_code = {"code": code,
                         "time": time}
        return last_code

    def has_send_code_permission(self, user_id, sorted_codes):
        if not sorted_codes:
            return True

        if len(sorted_codes) >= 3 and (datetime.now() - sorted_codes[-1][1]).seconds < 10 * 60:
            raise Http429(detail='Невозможно отправить сообщение. 10 минут еще не прошло.')

        elif len(sorted_codes) >= 3 and (datetime.now() - sorted_codes[-1][1]).seconds > 10 * 60:
            self.delete_codes(user_id)

        last_code = self.get_last_code(sorted_codes)
        if last_code and (datetime.now() - last_code['time']).seconds < 1.5 * 60:
            raise Http429(detail='Невозможно отправить сообщение. 1 минута 30 секунд еще не прошла.')

        return True

    def generate_set_code(self, user_id):
        # TODO generate code
        # code = str(random.randint(1000, 9999))
        code = "0000"
        REDIS.hmset(user_id, {code: str(datetime.now())})
        return code

    def delete_codes(self, user_id):
        REDIS.delete(user_id)

    def check_lifetime_code(self, last_code):
        if (datetime.now() - last_code['time']).seconds > 2 * 60:
            raise Http400(detail='Время жизни кода закончилось.')
        return True

    def send_code(self, user_id, phone):
        codes = self.sort_codes(user_id)
        print(codes)
        if self.has_send_code_permission(user_id, codes):
            # TODO -------------------------
            # send_sms(phone, self.generate_set_code(user_id))
            self.generate_set_code(user_id)
            return True
        return False

    def check_code(self, user_id, code_check):
        codes = self.sort_codes(user_id)

        if not codes:
            raise Http204(detail='Код не отправлен.')

        last_code = self.get_last_code(codes)
        if not last_code['code'] == code_check:
            raise Http400(detail='Неверный код.')

        self.check_lifetime_code(last_code)
        self.delete_codes(user_id)

        return True

